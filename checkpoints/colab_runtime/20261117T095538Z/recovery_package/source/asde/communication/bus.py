
import uuid
import json

from ..core.db import db


MESSAGE_TYPES = {
    "proposal",
    "challenge",
    "rebuttal",
    "revision",
    "verification",
    "decision",
    "research_output",
    "notification",
}


def publish(
    run_id,
    topic,
    payload,
    sender=None,
    recipient=None,
    *,
    task_id=None,
    thread_id=None,
    round_number=None,
    reply_to_message_id=None,
    message_type="research_output",
):
    """Persist one message while preserving the legacy publish interface."""

    if not run_id:
        raise ValueError("run_id is required")

    if not topic:
        raise ValueError("topic is required")

    if not isinstance(payload, dict):
        raise ValueError("payload must be a dictionary")

    if message_type not in MESSAGE_TYPES:
        raise ValueError("Unsupported message_type")

    if round_number is not None:
        if not isinstance(round_number, int) or round_number < 1:
            raise ValueError("round_number must be a positive integer")

    message_id = "msg_" + uuid.uuid4().hex

    with db() as conn:
        run_exists = conn.execute(
            "SELECT 1 FROM asde_runs WHERE run_id = %s",
            (run_id,),
        ).fetchone()

        if not run_exists:
            raise ValueError("Research run does not exist")

        if task_id is not None:
            task = conn.execute(
                """
                SELECT 1 FROM asde_tasks
                WHERE task_id = %s AND run_id = %s
                """,
                (task_id, run_id),
            ).fetchone()

            if not task:
                raise ValueError("Task does not belong to this run")

        if reply_to_message_id is not None:
            parent = conn.execute(
                """
                SELECT thread_id, round_number
                FROM asde_messages
                WHERE message_id = %s AND run_id = %s
                """,
                (reply_to_message_id, run_id),
            ).fetchone()

            if not parent:
                raise ValueError("Reply parent not found in this run")

            if thread_id is None:
                thread_id = parent[0]

            if thread_id != parent[0]:
                raise ValueError("Reply must belong to the parent's thread")

        if thread_id is None:
            thread_id = "thr_" + uuid.uuid4().hex

        conn.execute(
            """
            INSERT INTO asde_messages (
                message_id,
                run_id,
                sender_agent_id,
                recipient_agent_id,
                topic,
                payload,
                task_id,
                thread_id,
                round_number,
                reply_to_message_id,
                message_type
            )
            VALUES (
                %s, %s, %s, %s, %s, %s::jsonb,
                %s, %s, %s, %s, %s
            )
            """,
            (
                message_id,
                run_id,
                sender,
                recipient,
                topic,
                json.dumps(payload),
                task_id,
                thread_id,
                round_number,
                reply_to_message_id,
                message_type,
            ),
        )

    return message_id


def inbox(run_id, recipient=None, limit=50):
    """Legacy inbox API; returns messages in newest-first order."""

    if not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer")

    with db() as conn:
        if recipient:
            return conn.execute(
                """
                SELECT * FROM asde_messages
                WHERE run_id = %s
                  AND (
                      recipient_agent_id = %s
                      OR recipient_agent_id IS NULL
                  )
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (run_id, recipient, limit),
            ).fetchall()

        return conn.execute(
            """
            SELECT * FROM asde_messages
            WHERE run_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (run_id, limit),
        ).fetchall()


def thread_messages(run_id, thread_id, limit=100):
    """Retrieve one discussion thread in chronological order."""

    if not run_id or not thread_id:
        raise ValueError("run_id and thread_id are required")

    if not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer")

    with db() as conn:
        return conn.execute(
            """
            SELECT * FROM asde_messages
            WHERE run_id = %s AND thread_id = %s
            ORDER BY round_number ASC NULLS FIRST, created_at ASC
            LIMIT %s
            """,
            (run_id, thread_id, limit),
        ).fetchall()
