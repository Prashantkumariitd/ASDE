
from dataclasses import dataclass
from typing import Any


EXPECTED_CERTIFICATE_SHA256 = (
    "5bad3e5ba8f21c1e05079ab833a5a2945002b332772036539842c82b635f97dc"
)


@dataclass(frozen=True)
class ManagerDecision:
    decision: str
    reason: str
    evidence_scope: str


def _certificate_valid(evidence_refs: Any) -> bool:
    """Check that the exact audited certificate is referenced."""
    if not isinstance(evidence_refs, list):
        return False

    for item in evidence_refs:
        if not isinstance(item, dict):
            continue

        certificate = item.get("certificate", {})
        if not isinstance(certificate, dict):
            continue

        if (
            certificate.get("sha256") == EXPECTED_CERTIFICATE_SHA256
            and certificate.get("total_checks") == 6
            and certificate.get("passed_checks") == 6
            and certificate.get("number_field") == "Q(sqrt(2))"
        ):
            return True

    return False


def adjudicate_claim(claim_type: str, evidence_refs: Any) -> ManagerDecision:
    """
    Deterministic, claim-specific managerial policy.
    This function does not perform scientific verification.
    """

    if not _certificate_valid(evidence_refs):
        return ManagerDecision(
            "UNRESOLVED",
            "Required exact certificate evidence is missing or mismatched.",
            "No acceptance granted."
        )

    rules = {
        "mathematical_feasibility": ManagerDecision(
            "ACCEPT",
            "Exact primal certificate is referenced; all 6 checks passed.",
            "Declared deterministic CHSH model only."
        ),
        "exact_probability_reproduction": ManagerDecision(
            "ACCEPT",
            "Exact certificate supports reproduction of all 16 target probabilities.",
            "Declared target probabilities and model only."
        ),
        "lower_bound_attainment": ManagerDecision(
            "ACCEPT",
            "Supplied primal attains the stated analytical lower bound.",
            "Scoped to the supplied primal and stated bound; broader optimality is not inferred."
        ),
        "global_deterministic_optimality": ManagerDecision(
            "UNRESOLVED",
            "Global lower-bound proof has not been independently audited.",
            "No global optimality conclusion."
        ),
        "stochastic_response_optimality": ManagerDecision(
            "UNRESOLVED",
            "No separate proof covering stochastic local responses is recorded.",
            "Stochastic strategies remain outside the accepted result."
        ),
        "historical_reproducibility": ManagerDecision(
            "UNRESOLVED",
            "Historical LP implementation and ordering were not recovered.",
            "Independent reconstruction is not historical reproduction."
        ),
    }

    return rules.get(
        claim_type,
        ManagerDecision(
            "UNRESOLVED",
            "No approved adjudication rule exists for this claim type.",
            "No acceptance granted."
        )
    )
