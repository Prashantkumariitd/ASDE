
import uuid
import json
import socket

from ..core.db import db
from ..core.settings import Settings


def register_worker(runtime_id=None, max_concurrency=1, metadata=None):
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be at least 1")

    if max_concurrency > Settings.hard_max_workers:
        raise ValueError("Worker concurrency exceeds configured hard limit")

    worker_id = "worker_" + uuid.uuid4().hex
    runtime_id = runtime_id or socket.gethostname()

    with db() as conn:
        conn.execute(
            """
            INSERT INTO asde_worker_registry (
                worker_id, runtime_id, status, max_concurrency,
                active_tasks, heartbeat_at, metadata
            )
            VALUES (%s, %s, 'idle', %s, 0, NOW(), %s::jsonb)
            """,
            (worker_id, runtime_id, max_concurrency, json.dumps(metadata or {})),
        )

    return worker_id


def heartbeat_worker(worker_id):
    """
    Renew only unexpired task leases.
    An expired lease can never be revived by a late heartbeat.
    """
    with db() as conn:
        worker = conn.execute(
            """
            SELECT worker_id, status
            FROM asde_worker_registry
            WHERE worker_id = %s
            FOR UPDATE
            """,
            (worker_id,),
        ).fetchone()

        if not worker or worker[1] not in ("idle", "busy"):
            return False

        renewed = conn.execute(
            """
            UPDATE asde_tasks
            SET heartbeat_at = NOW(),
                lease_expires_at =
                    NOW() + (%s * INTERVAL '1 second'),
                updated_at = NOW()
            WHERE worker_id = %s
              AND status = 'running'
              AND lease_expires_at > NOW()
            RETURNING task_id
            """,
            (Settings.task_lease_seconds, worker_id),
        ).fetchall()

        active_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM asde_tasks
            WHERE worker_id = %s AND status = 'running'
              AND lease_expires_at > NOW()
            """,
            (worker_id,),
        ).fetchone()[0]

        # If tasks are still owned but all their leases expired,
        # the worker is stale and cannot heartbeat back to life.
        owned_expired = conn.execute(
            """
            SELECT COUNT(*)
            FROM asde_tasks
            WHERE worker_id = %s
              AND status = 'running'
              AND lease_expires_at <= NOW()
            """,
            (worker_id,),
        ).fetchone()[0]

        if owned_expired:
            return False

        conn.execute(
            """
            UPDATE asde_worker_registry
            SET heartbeat_at = NOW(),
                active_tasks = %s,
                status = %s
            WHERE worker_id = %s
            """,
            (active_count, "busy" if active_count else "idle", worker_id),
        )

    return True


def claim_task(worker_id, run_id=None):
    """Atomically claim one queued task and create its execution attempt."""

    with db() as conn:
        worker = conn.execute(
            """
            SELECT worker_id, status, max_concurrency
            FROM asde_worker_registry
            WHERE worker_id = %s
            FOR UPDATE
            """,
            (worker_id,),
        ).fetchone()

        if not worker:
            raise ValueError("Worker does not exist")

        _, worker_status, max_concurrency = worker

        if worker_status not in ("idle", "busy"):
            raise RuntimeError("Worker is not accepting tasks")

        active_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM asde_tasks
            WHERE worker_id = %s AND status = 'running'
              AND lease_expires_at > NOW()
            """,
            (worker_id,),
        ).fetchone()[0]

        if active_count >= max_concurrency:
            return None

        if run_id is None:
            candidate = conn.execute(
                """
                SELECT task_id, run_id, attempt_count
                FROM asde_tasks
                WHERE status = 'queued'
                  AND run_id IS NOT NULL
                  AND attempt_count < max_attempts
                  AND (next_retry_at IS NULL OR next_retry_at <= NOW())
                ORDER BY priority DESC, created_at ASC
                FOR UPDATE SKIP LOCKED
                LIMIT 1
                """
            ).fetchone()
        else:
            candidate = conn.execute(
                """
                SELECT task_id, run_id, attempt_count
                FROM asde_tasks
                WHERE status = 'queued'
                  AND run_id = %s
                  AND attempt_count < max_attempts
                  AND (next_retry_at IS NULL OR next_retry_at <= NOW())
                ORDER BY priority DESC, created_at ASC
                FOR UPDATE SKIP LOCKED
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()

        if not candidate:
            conn.execute(
                """
                UPDATE asde_worker_registry
                SET active_tasks = %s, status = %s
                WHERE worker_id = %s
                """,
                (active_count, "busy" if active_count else "idle", worker_id),
            )
            return None

        task_id, task_run_id, previous_attempts = candidate
        attempt_number = previous_attempts + 1
        attempt_id = "attempt_" + uuid.uuid4().hex

        updated = conn.execute(
            """
            UPDATE asde_tasks
            SET status = 'running',
                worker_id = %s,
                attempt_count = %s,
                started_at = COALESCE(started_at, NOW()),
                heartbeat_at = NOW(),
                lease_expires_at =
                    NOW() + (%s * INTERVAL '1 second'),
                updated_at = NOW(),
                last_error = NULL,
                next_retry_at = NULL
            WHERE task_id = %s
              AND status = 'queued'
            RETURNING task_id, run_id, attempt_count, title, task_type
            """,
            (worker_id, attempt_number, Settings.task_lease_seconds, task_id),
        ).fetchone()

        if not updated:
            raise RuntimeError("Atomic task claim failed")

        conn.execute(
            """
            INSERT INTO asde_execution_attempts (
                attempt_id, task_id, run_id, worker_id,
                attempt_number, status, metadata
            )
            VALUES (%s, %s, %s, %s, %s, 'started', %s::jsonb)
            """,
            (
                attempt_id, task_id, task_run_id, worker_id,
                attempt_number,
                json.dumps({"claim_method": "for_update_skip_locked"}),
            ),
        )

        conn.execute(
            """
            UPDATE asde_worker_registry
            SET active_tasks = %s, status = 'busy', heartbeat_at = NOW()
            WHERE worker_id = %s
            """,
            (active_count + 1, worker_id),
        )

        return {
            "task_id": updated[0],
            "run_id": updated[1],
            "attempt_count": updated[2],
            "title": updated[3],
            "task_type": updated[4],
            "attempt_id": attempt_id,
            "worker_id": worker_id,
        }


def complete_task(worker_id, task_id, attempt_id, output_refs=None):
    """
    Complete only if worker, attempt and unexpired lease still match.
    Returns False for stale or mismatched workers.
    """
    with db() as conn:
        task = conn.execute(
            """
            SELECT run_id
            FROM asde_tasks
            WHERE task_id = %s
              AND worker_id = %s
              AND status = 'running'
              AND lease_expires_at > NOW()
            FOR UPDATE
            """,
            (task_id, worker_id),
        ).fetchone()

        if not task:
            return False

        attempt = conn.execute(
            """
            UPDATE asde_execution_attempts
            SET status = 'succeeded', completed_at = NOW()
            WHERE attempt_id = %s
              AND task_id = %s
              AND worker_id = %s
              AND status = 'started'
            RETURNING attempt_id
            """,
            (attempt_id, task_id, worker_id),
        ).fetchone()

        if not attempt:
            return False

        updated = conn.execute(
            """
            UPDATE asde_tasks
            SET status = 'completed',
                output_refs = %s::jsonb,
                completed_at = NOW(),
                lease_expires_at = NULL,
                heartbeat_at = NOW(),
                updated_at = NOW()
            WHERE task_id = %s
              AND worker_id = %s
              AND status = 'running'
            RETURNING task_id
            """,
            (json.dumps(output_refs or []), task_id, worker_id),
        ).fetchone()

        if not updated:
            raise RuntimeError("Task completion transition failed")

        _refresh_worker_state(conn, worker_id)

    return True


def fail_task(
    worker_id, task_id, attempt_id,
    error_code="execution_error", retry_delay_seconds=30
):
    """Close the current attempt and retry or terminally fail the task."""

    if retry_delay_seconds < 0:
        raise ValueError("retry_delay_seconds cannot be negative")

    with db() as conn:
        task = conn.execute(
            """
            SELECT run_id, attempt_count, max_attempts
            FROM asde_tasks
            WHERE task_id = %s
              AND worker_id = %s
              AND status = 'running'
              AND lease_expires_at > NOW()
            FOR UPDATE
            """,
            (task_id, worker_id),
        ).fetchone()

        if not task:
            return False

        run_id, attempt_count, max_attempts = task

        attempt = conn.execute(
            """
            UPDATE asde_execution_attempts
            SET status = 'failed',
                completed_at = NOW(),
                error_code = %s
            WHERE attempt_id = %s
              AND task_id = %s
              AND worker_id = %s
              AND status = 'started'
            RETURNING attempt_id
            """,
            (str(error_code)[:120], attempt_id, task_id, worker_id),
        ).fetchone()

        if not attempt:
            return False

        retry = attempt_count < max_attempts

        if retry:
            conn.execute(
                """
                UPDATE asde_tasks
                SET status = 'queued',
                    worker_id = NULL,
                    lease_expires_at = NULL,
                    heartbeat_at = NULL,
                    next_retry_at =
                        NOW() + (%s * INTERVAL '1 second'),
                    last_error = %s,
                    updated_at = NOW()
                WHERE task_id = %s
                """,
                (retry_delay_seconds, str(error_code)[:500], task_id),
            )
        else:
            conn.execute(
                """
                UPDATE asde_tasks
                SET status = 'failed',
                    worker_id = NULL,
                    lease_expires_at = NULL,
                    heartbeat_at = NULL,
                    completed_at = NOW(),
                    last_error = %s,
                    updated_at = NOW()
                WHERE task_id = %s
                """,
                (str(error_code)[:500], task_id),
            )

        _refresh_worker_state(conn, worker_id)

    return "queued_for_retry" if retry else "terminal_failure"


def recover_expired_tasks(limit=50):
    """
    Recover expired running tasks using row locks.
    Old attempts are closed before tasks are requeued or failed.
    """
    if limit < 1:
        raise ValueError("limit must be positive")

    recovered = []

    with db() as conn:
        expired = conn.execute(
            """
            SELECT task_id, run_id, worker_id, attempt_count, max_attempts
            FROM asde_tasks
            WHERE status = 'running'
              AND lease_expires_at <= NOW()
            ORDER BY lease_expires_at ASC
            FOR UPDATE SKIP LOCKED
            LIMIT %s
            """,
            (limit,),
        ).fetchall()

        affected_workers = set()

        for task_id, run_id, worker_id, attempt_count, max_attempts in expired:
            affected_workers.add(worker_id)

            conn.execute(
                """
                UPDATE asde_execution_attempts
                SET status = 'lease_expired',
                    completed_at = NOW(),
                    error_code = 'worker_lease_expired'
                WHERE task_id = %s
                  AND attempt_number = %s
                  AND status = 'started'
                """,
                (task_id, attempt_count),
            )

            retry = attempt_count < max_attempts

            if retry:
                conn.execute(
                    """
                    UPDATE asde_tasks
                    SET status = 'queued',
                        worker_id = NULL,
                        lease_expires_at = NULL,
                        heartbeat_at = NULL,
                        next_retry_at = NOW(),
                        last_error = 'worker_lease_expired',
                        updated_at = NOW()
                    WHERE task_id = %s
                      AND status = 'running'
                    """,
                    (task_id,),
                )
                new_status = "queued"
            else:
                conn.execute(
                    """
                    UPDATE asde_tasks
                    SET status = 'failed',
                        worker_id = NULL,
                        lease_expires_at = NULL,
                        heartbeat_at = NULL,
                        completed_at = NOW(),
                        last_error = 'worker_lease_expired',
                        updated_at = NOW()
                    WHERE task_id = %s
                      AND status = 'running'
                    """,
                    (task_id,),
                )
                new_status = "failed"

            recovered.append({
                "task_id": task_id,
                "previous_worker_id": worker_id,
                "new_status": new_status,
                "attempt_count": attempt_count,
            })

        for worker_id in affected_workers:
            if worker_id:
                _refresh_worker_state(conn, worker_id)

    return recovered


def _refresh_worker_state(conn, worker_id):
    """Recalculate worker load from task rows, not cached counters."""

    active_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM asde_tasks
        WHERE worker_id = %s
          AND status = 'running'
          AND lease_expires_at > NOW()
        """,
        (worker_id,),
    ).fetchone()[0]

    conn.execute(
        """
        UPDATE asde_worker_registry
        SET active_tasks = %s,
            status = CASE WHEN %s > 0 THEN 'busy' ELSE 'idle' END,
            heartbeat_at = NOW()
        WHERE worker_id = %s
          AND status IN ('idle', 'busy')
        """,
        (active_count, active_count, worker_id),
    )


def stop_worker(worker_id):
    """Stop an idle worker; refuse to stop one with active tasks."""

    with db() as conn:
        worker = conn.execute(
            """
            SELECT worker_id
            FROM asde_worker_registry
            WHERE worker_id = %s
            FOR UPDATE
            """,
            (worker_id,),
        ).fetchone()

        if not worker:
            return False

        active_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM asde_tasks
            WHERE worker_id = %s AND status = 'running'
            """,
            (worker_id,),
        ).fetchone()[0]

        if active_count:
            raise RuntimeError(
                "Worker still owns active tasks; drain or recover them first"
            )

        updated = conn.execute(
            """
            UPDATE asde_worker_registry
            SET status = 'stopped',
                active_tasks = 0,
                stopped_at = NOW(),
                heartbeat_at = NOW()
            WHERE worker_id = %s
              AND status IN ('idle', 'busy')
            RETURNING worker_id
            """,
            (worker_id,),
        ).fetchone()

    return bool(updated)
