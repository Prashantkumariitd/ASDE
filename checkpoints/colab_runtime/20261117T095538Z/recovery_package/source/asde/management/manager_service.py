
import json
import re
from pathlib import Path

from ..core.db import db
from ..communication import bus
from ..integrations.models.router import call_routed
from .decision_engine import adjudicate_claim


def _extract_json(content):
    if not isinstance(content, str):
        raise ValueError("Model response is not text")

    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise ValueError("No valid JSON object in manager response")
        data = json.loads(match.group(0))

    if not isinstance(data, dict):
        raise ValueError("Manager response must be a JSON object")

    return data


def run_manager_adjudication(
    run_id,
    manager_id,
    hypothesis_id,
    thread_id,
):
    # 1. Read claims and discussion. No writes.
    with db() as conn:
        manager = conn.execute("""
            SELECT agent_id, role, status
            FROM asde_agents
            WHERE agent_id = %s AND run_id = %s
        """, (manager_id, run_id)).fetchone()

        if not manager or manager[1] != "Chief Research Manager":
            raise RuntimeError("Registered manager identity not found")

        claims = conn.execute("""
            SELECT claim_id, statement, claim_type, epistemic_status,
                   assumptions, evidence_refs, counterevidence_refs
            FROM asde_claims
            WHERE hypothesis_id = %s
            ORDER BY claim_id
        """, (hypothesis_id,)).fetchall()

        messages = conn.execute("""
            SELECT message_id, sender_agent_id, topic, payload,
                   round_number, message_type
            FROM asde_messages
            WHERE run_id = %s AND thread_id = %s
            ORDER BY round_number ASC NULLS FIRST, created_at ASC
            LIMIT 50
        """, (run_id, thread_id)).fetchall()

        existing = conn.execute("""
            SELECT message_id
            FROM asde_messages
            WHERE run_id = %s
              AND thread_id = %s
              AND sender_agent_id = %s
              AND message_type = 'decision'
        """, (run_id, thread_id, manager_id)).fetchone()

    if existing:
        raise RuntimeError(
            f"Manager decision already exists: {existing[0]}. "
            "No duplicate call or message created."
        )

    if not claims:
        raise RuntimeError("No claims found for this hypothesis")

    if not messages:
        raise RuntimeError("Discussion thread is empty")

    claim_ids = {row[0] for row in claims}
    last_message_id = messages[-1][0]
    next_round = max(
        [row[4] for row in messages if row[4] is not None] or [0]
    ) + 1

    # 2. Prepare evidence and discussion for the real manager model.
    claim_data = []
    for row in claims:
        claim_data.append({
            "claim_id": row[0],
            "statement": row[1],
            "claim_type": row[2],
            "current_epistemic_status": row[3],
            "assumptions": row[4],
            "evidence_refs": row[5],
            "counterevidence_refs": row[6],
        })

    discussion = []
    for row in messages:
        discussion.append({
            "message_id": row[0],
            "sender_agent_id": row[1],
            "topic": row[2],
            "payload": row[3],
            "round_number": row[4],
            "message_type": row[5],
        })

    prompt = f"""
You are the Chief Research Manager of ASDE, an autonomous scientific
research organization.

Your task is to independently assess the six scientific claims below,
using the complete discussion and evidence supplied.

You are NOT the independent verifier.
Do not invent evidence, proofs, citations, or computations.
Do not treat agreement among agents as mathematical proof.
Distinguish exact feasibility, reproduction, lower-bound attainment,
global optimality, stochastic optimality, and historical reproducibility.
Preserve limitations and unresolved questions.

Return ONLY valid JSON with this structure:

{{
  "overall_assessment": "brief assessment",
  "important_limitations": ["..."],
  "claims": [
    {{
      "claim_id": "exact supplied ID",
      "recommendation": "ACCEPT or REVISE or UNRESOLVED",
      "rationale": "evidence-based explanation",
      "unresolved_questions": ["..."]
    }}
  ]
}}

Include exactly one entry for every supplied claim ID.
Do not change IDs.
Do not claim independent replication.
A recommendation is advisory; ASDE's deterministic evidence policy
will enforce the final managerial decision.

CLAIMS:
{json.dumps(claim_data, default=str, indent=2)}

DISCUSSION:
{json.dumps(discussion, default=str, indent=2)}
"""

    # 3. Real model call through approved Groq -> OpenRouter router.
    context = {
        "run_id": run_id,
        "agent_id": manager_id,
    }

    response = call_routed(
        "reasoning",
        prompt,
        context=context,
    )

    model_assessment = _extract_json(response["content"])
    model_claims = model_assessment.get("claims")

    if not isinstance(model_claims, list):
        raise ValueError("Manager JSON has no claims list")

    by_id = {}
    for item in model_claims:
        if not isinstance(item, dict):
            raise ValueError("Invalid claim assessment item")
        cid = item.get("claim_id")
        if cid not in claim_ids or cid in by_id:
            raise ValueError("Unknown or duplicate claim ID in model output")
        by_id[cid] = item

    if set(by_id) != claim_ids:
        raise ValueError("Manager did not assess exactly all six claims")

    # 4. Deterministic evidence policy overrides model recommendations.
    final_claims = []

    for row in claims:
        claim_id, statement, claim_type, current_status = row[:4]
        evidence_refs = row[5]

        policy = adjudicate_claim(claim_type, evidence_refs)
        model_item = by_id[claim_id]

        recommendation = str(
            model_item.get("recommendation", "UNRESOLVED")
        ).upper()

        final_claims.append({
            "claim_id": claim_id,
            "claim_type": claim_type,
            "statement": statement,
            "previous_epistemic_status": current_status,
            "manager_model_recommendation": recommendation,
            "manager_model_rationale": str(
                model_item.get("rationale", "")
            ),
            "manager_decision": policy.decision,
            "policy_rationale": policy.reason,
            "evidence_scope": policy.evidence_scope,
            "unresolved_questions": model_item.get(
                "unresolved_questions", []
            ),
            "policy_model_disagreement": (
                recommendation != policy.decision
            ),
        })

    payload = {
        "decision_version": "1.0",
        "decision_scope": "claim_level_test_run_adjudication",
        "hypothesis_id": hypothesis_id,
        "manager_agent_id": manager_id,
        "overall_assessment": model_assessment.get(
            "overall_assessment", ""
        ),
        "important_limitations": model_assessment.get(
            "important_limitations", []
        ),
        "claims": final_claims,
        "provider": response["provider"],
        "model": response["model"],
        "fallback_used": response["fallback_used"],
        "claim_statuses_modified": False,
        "independent_verification_created": False,
    }

    # 5. Persist one decision message in the existing discussion thread.
    message_id = bus.publish(
        run_id,
        topic="Chief Research Manager claim-wise adjudication",
        payload=payload,
        sender=manager_id,
        thread_id=thread_id,
        round_number=next_round,
        reply_to_message_id=last_message_id,
        message_type="decision",
    )

    return {
        "message_id": message_id,
        "round_number": next_round,
        "provider": response["provider"],
        "model": response["model"],
        "fallback_used": response["fallback_used"],
        "claims": final_claims,
        "overall_assessment": payload["overall_assessment"],
    }
