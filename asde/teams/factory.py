
import uuid
import json

from ..core.db import db
from ..agents.roster import ROSTER


def provision_roster(run_id, agents_per_team=3):
    """
    Provision agents and memberships in one atomic transaction.

    If any insertion fails, the complete roster transaction rolls back.
    """

    if not run_id:
        raise ValueError("run_id is required")

    if not isinstance(agents_per_team, int) or agents_per_team < 0:
        raise ValueError("agents_per_team must be a non-negative integer")

    teams = sorted(set(item[0] for item in ROSTER))
    planned = []

    for team in teams:
        team_roles = [item for item in ROSTER if item[0] == team]

        for _, role, mandate in team_roles[:agents_per_team]:
            planned.append({
                "agent_id": "agt_" + uuid.uuid4().hex,
                "team": team,
                "role": role,
                "mandate": mandate,
            })

    made = []

    with db() as conn:
        run_exists = conn.execute(
            "SELECT 1 FROM asde_runs WHERE run_id = %s",
            (run_id,),
        ).fetchone()

        if not run_exists:
            raise ValueError("Research run does not exist")

        for agent in planned:
            conn.execute(
                """
                INSERT INTO asde_agents (
                    agent_id, run_id, role, status, metadata
                )
                VALUES (%s, %s, %s, 'registered', %s::jsonb)
                """,
                (
                    agent["agent_id"],
                    run_id,
                    agent["role"],
                    json.dumps({
                        "team": agent["team"],
                        "mandate": agent["mandate"],
                    }),
                ),
            )

            conn.execute(
                """
                INSERT INTO asde_agent_team_memberships (
                    agent_id, team_id, role
                )
                VALUES (%s, %s, %s)
                """,
                (
                    agent["agent_id"],
                    agent["team"],
                    agent["role"],
                ),
            )

            made.append({
                "agent_id": agent["agent_id"],
                "team": agent["team"],
                "role": agent["role"],
            })

    return made
