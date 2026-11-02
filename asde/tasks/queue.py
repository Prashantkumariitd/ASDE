
import uuid
import json

from ..core.db import db


def enqueue(run_id, team_id, title, description, priority=8):
    """
    Create a task explicitly associated with its research run.
    Task insertion and event publication share one transaction.
    """

    if not run_id:
        raise ValueError("run_id is required")

    if not team_id:
        raise ValueError("team_id is required")

    tid = "tsk_" + uuid.uuid4().hex

    with db() as conn:
        run_exists = conn.execute(
            "SELECT 1 FROM asde_runs WHERE run_id = %s",
            (run_id,),
        ).fetchone()

        if not run_exists:
            raise ValueError("Research run does not exist")

        conn.execute(
            """
            INSERT INTO asde_tasks (
                task_id, run_id, team_id, title, description,
                task_type, status, priority
            )
            VALUES (%s, %s, %s, %s, %s, 'research', 'queued', %s)
            """,
            (tid, run_id, team_id, title, description, priority),
        )

        conn.execute(
            """
            INSERT INTO asde_events(run_id, event_type, payload)
            VALUES (%s, 'task_enqueued', %s::jsonb)
            """,
            (
                run_id,
                json.dumps({"task_id": tid, "team": team_id}),
            ),
        )

    return tid
