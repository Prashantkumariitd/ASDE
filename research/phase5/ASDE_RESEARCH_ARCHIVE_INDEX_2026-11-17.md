# ASDE Research Archive Index
Updated: 2026-11-17

This index corrects the earlier PHYS-04D filename-based audit. The audit
incorrectly searched only for files named NS-MD-01 ... NS-MD-12 under
research/phase5/reports. Historical Phase 5 files use p5_* names and are
therefore not missing merely because their filenames differ.

## Confirmed GitHub artifacts

### Phase 3
- research/phase3/reports/ — ten domain reports
- research/phase3/phase3_manifest.json
- research/phase3/PHASE3_INTEGRITY_AUDIT.json
Status: repository artifacts confirmed. Historical handover reports 10/10
valid Neon outputs.

### Phase 4
- research/phase4/reports/p4_01_formal_foundations.json
- research/phase4/reports/p4_02_chsh_baseline.json
- research/phase4/reports/p4_03_measurement_dependence.json
- research/phase4/reports/p4_04_competing_models.json
- research/phase4/reports/p4_05_parameter_identification.json
- research/phase4/reports/p4_06_adversarial_review.json
- research/phase4/reports/p4_07_phase_synthesis.json
- research/phase4/phase4_manifest.json
- research/phase4/computations/chsh_baseline.json
Status: repository artifacts confirmed; historical handover says seven packages completed.

### Phase 5
Confirmed files include:
- research/phase5/reports/p5_1_chsh_mi_vs_md.json
- research/phase5/reports/p5_2_mathematical_audit.json
- research/phase5/reports/p5_3_comprehensive_robustness.json
- research/phase5/reports/p5_3_robustness_representation.json
- research/phase5/reports/p5_4_5_mathematical_certification.json
- research/phase5/reports/p5_4_exact_bell_and_mechanism_audit.json
- research/phase5/reports/p5_4_hall_continuous_replication.json
- research/phase5/reports/p5_5_6_statistical_model_comparison.json
- research/phase5/reports/p5_5_7_discriminating_experiments.json
- research/phase5/reports/p5_6_hall_cosmology_gate.json
- research/phase5/reports/p5_4_physical_mechanism_gate.json
- research/phase5/reports/nist_raw_event_audit.json
- Additional p5_* reports and computations under research/phase5/

Important qualification:
- Phase 5.3 JSON is present in GitHub and contains results, despite an older
  handover saying its execution was unconfirmed at that time.
- NIST raw event-level Bell statistics remain blocked pending verified
  event selection, synchronization, and trial protocol.
- Hall cosmology gate is NO_GO_WITH_CURRENT_MECHANISM.
- Valentini pilot-wave work is a separate branch and not complete.

### NS-MD / PHYS
- PHYS-04B report saved in research/phase5/reports/PHYS-04B_20261117T060208Z.json
- PHYS-04C report saved in research/phase5/reports/PHYS-04C_20261117T060208Z.json
- PHYS-04D archive audit saved in research/phase5/reports/
- Neon inserts for PHYS-04B and PHYS-04C were confirmed inserted=True.
- PHYS-04D manifest Neon insert was confirmed inserted=True.

NS-MD-01 ... NS-MD-12 and PHYS-01 ... PHYS-03 are logical workstream
labels described in the conversation / project handover. Their dedicated
standalone report files were not identified by the earlier exact-name
audit. This does NOT mean their underlying work is absent: parts of the
work are contained in p5_* reports and in the master handover. Dedicated
raw outputs, code, and Neon row mappings should be recovered and cross-linked
before declaring each sub-experiment individually archived.

## Neon verification boundary

The current table audit checked asde_phase53_results by exact
experiment_id. That table is not a complete index of every Phase 3/4/5
result table. Other canonical tables documented in ASDE_MASTER_HANDOVER.md
include phase-specific work-item/output tables, artefacts, claims,
verifications, and dedicated Phase 5.6 / Valentini tables. A future full
DB audit must inspect schemas and query all relevant tables read-only.

## Scientific status
- NS-MD core analytical result: global MI lower bound for the specified
  uniform 2x2 binary CHSH / 16 deterministic strategy model, attained by
  explicit construction.
- Partially entangled quantum-table extension: full primal-dual numerical
  agreement across tested angles; no general closed-form expression derived.
- PHYS-04B/04C: exact numerical common-cause factorizations found. Best
  feasible I(Omega;X) upper bounds: 1.3086595 bits at 16.875 degrees and
  0.3583971 bits at 45 degrees. These are feasible upper bounds, not proven
  global minima.
- No physical spacetime mechanism established.

## Archival policy
Never reconstruct missing numerical outputs from memory or summaries and
label them as original results. Store recovered historical records with
source provenance; mark derived summaries as reconstructions.
