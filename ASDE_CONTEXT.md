# ASDE — Project Context and Handoff

**Canonical file:** `ASDE_CONTEXT.md`  
**Project repository:** `Prashantkumariitd/ASDE` (private; branch `main`)  
**Master notebook:** `ADSE_MASTER.ipynb`  
**Last documented checkpoint:** 1 November 2026  
**Current research run:** `run_64ca8ea8354347659fe78f63b8569a67`

> This document is the canonical handoff for a new ChatGPT conversation or a new engineering/research session. Read it before proposing changes or running code. It records what has been implemented and verified, what is only planned, and the constraints that must not be violated. Update this file whenever architecture, phase status, provider policy, run IDs, schema, or scientific conclusions change.

---

## 1. What ASDE is

ASDE (Autonomous Scientific Discovery Engine) is an experimental, cloud-executed, multi-agent research system. Its purpose is to investigate whether frameworks combining **locality, realism and measurement dependence / superdeterminism** can be formulated consistently and whether they yield discriminating, testable consequences.

The research programme includes (but is not limited to):

- Bell inequalities and the measurement-independence assumption.
- Local hidden-variable and measurement-dependent models.
- Quantum foundations and the distinction between mathematical possibility and physical plausibility.
- Early-universe mechanisms and possible primordial signatures.
- CMB observables and potential discriminators.
- Decoherence, thermalisation and related QFT questions.
- Mathematical consistency, statistical inference, experimental design and falsification.

**The project is not committed to proving superdeterminism or any other preferred framework.** Every premise is a hypothesis. The engine must compare alternatives, derive predictions, search for contradictions and attempt falsification. A mathematically consistent model is not automatically physically true; an LLM-generated argument is not evidence; multiple agents agreeing is not independent validation.

### Mission statement

“Investigate testable consequences of frameworks combining locality, realism and superdeterminism. Treat all premises as hypotheses; compare alternatives, derive discriminating predictions, and actively attempt falsification.”

---

## 2. Non-negotiable operating constraints

1. **Zero budget.** Do not incur paid API, compute, storage, subscription or other charges. Never enable paid fallback or spend provider credits without explicit approval.
2. **Cloud-only execution.** The user's laptop is a browser/thin client. Do not require local Python, local models, local databases or local simulation execution.
3. **One master notebook.** Continue using `ADSE_MASTER.ipynb`; do not create a succession of notebooks or ask for repeated setup.
4. **No Google Drive dependency.** Google Drive is explicitly not part of the architecture.
5. **Colab free-runtime limitations.** Runtime is temporary, quota-limited and not guaranteed to run continuously. Use bounded, user-triggered jobs, frequent checkpoints and restart recovery. Do not claim 24/7 operation or unlimited GPU. Colab free terms do not permit distributed-computing workers.
6. **No secret disclosure.** Read keys from Colab Secrets/environment. Never ask the user to paste keys into chat, print them, store them in GitHub, or put them in logs. Do not expose secret-bearing URLs.
7. **No silent model downgrade.** If the configured primary and permitted fallback fail or quota is exhausted, checkpoint and pause. Do not silently substitute a weaker/unapproved model.
8. **Autonomous research, not user-operated review.** Agents should retrieve, analyse, challenge and synthesise. Do not routinely ask the user to inspect many individual outputs or manually relay them. The user runs one complete phase cell and shares execution errors/results when needed.
9. **Deliver complete phases.** Prefer one complete, self-contained Colab cell per phase or repair operation. Avoid fragmented snippets and multi-cell procedures unless technically unavoidable.
10. **Preserve existing work.** Inspect existing GitHub/Neon state before creating or overwriting. Use idempotent inserts/upserts and checkpointed operations.

---

## 3. High-level architecture

```text
User / ChatGPT orchestration
          |
          v
ADSE_MASTER.ipynb (Google Colab; cloud execution)
          |
          +---- Agent orchestration / task queue / team factory
          |          |
          |          +---- Domain teams and specialist agents
          |          +---- Shared message bus / task delegation
          |          +---- Synthesis / adversarial review / verification
          |
          +---- Model router
          |          +---- Groq primary
          |          +---- OpenRouter free fallback on ANY Groq error
          |          +---- Pause + checkpoint if fallback fails
          |
          +---- Scientific execution libraries
          |          +---- NumPy / SciPy / SymPy
          |          +---- Astropy / QuTiP
          |          +---- Add CMB/statistical libraries when needed
          |
          +---- OpenAlex / Crossref and future specialist literature sources
          |
          +---- Neon PostgreSQL (persistent structured state)
          +---- Neon Object Storage (large artefacts)
          +---- GitHub private repository (code, reports, context, versioning)
```

### Components and responsibilities

- **Colab:** Runs the notebook and Python workloads in the cloud. The runtime is ephemeral; persistent state must be committed to Neon/GitHub/Object Storage.
- **Neon PostgreSQL:** System of record for projects, runs, agents, teams, memberships, tasks, messages, claims, hypotheses, experiments, verifications, knowledge sources and research outputs.
- **Neon Object Storage:** Intended for large binary artefacts and files that should not be stored as database rows or Git blobs.
- **GitHub:** Versioned source code, phase manifests, research reports, project context, reproducibility files and selected artefacts. Repo: `Prashantkumariitd/ASDE`, branch `main`.
- **Model providers:** Groq primary; OpenRouter free model as automatic fallback. Gemini and Mistral keys exist but are not part of the approved current fallback route.
- **Literature discovery:** OpenAlex for public scholarly metadata/abstract discovery; Crossref for DOI metadata/title cross-checking. These checks do not establish that a paper supports a claim.
- **Scientific libraries currently installed in the Colab environment at Phase 3 foundation:** Python 3.13.18, NumPy 2.1.3, SciPy 1.16.3, SymPy 1.14.0, Astropy 7.2.3, QuTiP 5.3.1. Runtime packages may need reinstalling after a reset.

---

## 4. Persistent resources and configuration

### GitHub

- Repository: `Prashantkumariitd/ASDE`
- Branch: `main`
- Master notebook: `ADSE_MASTER.ipynb` (user's Colab notebook; do not create another)
- Phase 3 report directory: `research/phase3/reports/`
- Canonical handoff filename: `ASDE_CONTEXT.md`

### Neon

- Database: `neondb`
- Schema: `public`
- Owner role: `neondb_owner`
- Object Storage bucket: `asde-artifacts`
- Connection secret: `NEON_DATABASE_URL`

### Colab Secrets (names only; never print values)

- `GITHUB_REPO` = `Prashantkumariitd/ASDE`
- `GITHUB_TOKEN` — normal repository operations
- `GITHUB_PROVISIONER_TOKEN` — repository provisioning operations
- `NEON_DATABASE_URL`
- `GROQ_API_KEY`
- `OPENROUTER_API_KEY`
- `GEMINI_API_KEY` (not current fallback)
- `MISTRAL_API_KEY` (currently disabled/unusable due provider quota response)
- Optional Neon S3-compatible storage settings: `NEON_S3_ENDPOINT`, `NEON_S3_ACCESS_KEY`, `NEON_S3_SECRET_KEY`, `NEON_S3_REGION`, `NEON_S3_BUCKET=asde-artifacts`

Never request that the user paste these secrets into a chat. Use existing Colab Secrets. Do not repeatedly prompt for them if already present.

---

## 5. Database schema and persistence

Existing public-schema tables include:

- `asde_projects`
- `asde_runs`
- `asde_agents`
- `asde_teams`
- `asde_agent_team_memberships`
- `asde_tasks`
- `asde_messages`
- `asde_claims`
- `asde_hypotheses`
- `asde_experiments`
- `asde_verifications`
- `asde_artifacts`
- `asde_model_registry`
- `asde_repository_registry`
- `asde_schema_version`
- Phase 3 additions: `asde_domain_workstreams`, `asde_knowledge_sources`, `asde_phase3_work_items`, `asde_domain_research_outputs`
- Provider-attempt and Phase 2 stage-output tables were also added during implementation; inspect actual schema before relying on exact names.

### Important exact Phase 3 output table schema

`asde_domain_research_outputs` columns observed from Neon:

| Column | Type | Notes |
|---|---|---|
| `output_id` | text | NOT NULL; primary key |
| `run_id` | text | NOT NULL |
| `work_item_id` | text | NOT NULL |
| `domain_id` | text | NOT NULL |
| `provider` | text | nullable |
| `model_id` | text | nullable; **not** `model` |
| `status` | text | NOT NULL; default `planned` |
| `source_ids` | jsonb | NOT NULL; default `[]` |
| `response_text` | text | nullable; **not** `report_text` |
| `error_text` | text | nullable |
| `created_at` | timestamptz | nullable; default now() |
| `updated_at` | timestamptz | nullable; default now() |

Unique constraint: `(run_id, work_item_id)`. Primary key: `output_id`.

**Schema lesson:** always inspect `information_schema.columns` before writing repair/migration code. For `source_ids`, serialize Python values as JSON and cast to `jsonb` (e.g. `%s::jsonb`); do not assume it is a PostgreSQL array. Do not assume `model` or `report_text` columns exist.

---

## 6. Agent organisation

Phase 3 inherited a six-team, 18-logical-agent roster (three roles per team):

1. **Theoretical Physics** — Theoretical Physicist; Quantum Foundations Specialist; Cosmology Specialist.
2. **Mathematics** — Mathematical Physicist; Symbolic Mathematics Specialist; Statistics Specialist.
3. **Scientific Computing** — Numerical Methods Specialist; Simulation Engineer; Physics-Informed ML Specialist.
4. **Literature and Observation** — Literature Researcher; Observational Data Specialist; Experimental Design Specialist.
5. **Hypothesis Discovery** — Mechanism Explorer; Hypothesis Synthesiser; Research Strategist.
6. **Adversarial Verification** — Adversarial Reviewer; Independent Reproducer; Evidence Auditor.

Teams are divisions of labour, not isolated chatbot groups. Agents should be able to share context, message one another, delegate subtasks and create specialist agents/teams when justified. Team size and concurrency should adapt to task complexity, provider quotas and Colab resource limits. The desired long-term architecture is a dynamically expanding interconnected swarm, not a fixed collection of independent chatbots.

The roster is the logical agent design; do not claim that all agents run concurrently. Current Colab/provider limits require bounded execution.

---

## 7. Model routing and quota policy

### Approved routing

1. **Primary:** Groq, model `openai/gpt-oss-120b`.
2. **Fallback:** OpenRouter, model `nvidia/nemotron-3-ultra-550b-a55b:free`, on **any** Groq error (HTTP 400/401/429/5xx, timeout, network/provider exception).
3. If OpenRouter fails, checkpoint and pause. No silent downgrade.
4. Preserve both requested and actual provider/model in provenance/attempt logs.
5. Do not route to Gemini or Mistral as fallback unless the user explicitly changes this policy.

### Quota/cost cautions

- OpenRouter free-model limits previously observed: 20 requests/minute and 50 requests/day without purchased credits. Limits may change; check current account response before large batches.
- Historical Phase 2 used eight OpenRouter calls; a later Phase 3 fallback used at least one. An earlier quota check showed 33/50 remaining after Phase 2, but **current remaining quota is unknown and must not be assumed**.
- Failed free-tier requests may count toward quota. Do not run unnecessary test calls.
- Groq previously returned 429 rate limits; retry sequentially with bounded backoff, then automatic OpenRouter fallback.
- Mistral returned HTTP 429 with request limit zero; keep disabled.
- Gemini had 429/503 issues. A previous Gemini key was exposed in URL-form errors/logs and was reportedly rotated. Ensure the old exposed key is revoked; never log API keys in URLs. The router should send Gemini keys in headers if Gemini is ever re-enabled.

---

## 8. Scientific method and evidence standards

ASDE must follow a traceable scientific workflow:

1. **Define question and scope.** State the target question, competing explanations and what would count as evidence against each.
2. **Retrieve sources.** Prefer primary papers, original derivations, datasets, instrument papers and authoritative collaboration releases. Record title, authors, DOI/URL, publication/version date, source type, access/full-text status and retrieval timestamp.
3. **Verify source identity.** DOI/title matching via Crossref checks metadata identity only. It does not verify the paper's methods, conclusions or support for an ASDE claim.
4. **Extract claims with provenance.** Each claim should link to exact source passages, equations, tables, data or code where available. Distinguish abstract-only evidence from full-text review.
5. **Formalise assumptions.** Define variables, probability spaces, conditional independences, causal structure, parameter domains and mathematical assumptions explicitly.
6. **Derive predictions.** Show derivations, not only verbal summaries. Record intermediate steps and limiting cases.
7. **Compute reproducibly.** Use versioned code, fixed seeds where appropriate, units, tolerances, solver settings, package versions and environment manifests.
8. **Compare alternatives.** Include standard quantum mechanics, relevant local hidden-variable/measurement-dependent alternatives and null/baseline models.
9. **Adversarially review.** Assign independent reviewers to identify hidden assumptions, algebraic errors, selection effects, confounding, overfitting and alternative explanations.
10. **Replicate independently.** A separate agent/process should reproduce results from the recorded inputs and code, not merely restate the first result.
11. **Classify conclusions.** Use explicit labels such as `hypothesis`, `derived`, `computationally_checked`, `source_supported`, `independently_reproduced`, `empirically_tested`, `falsified`, `unresolved`.
12. **Preserve uncertainty.** Report null results, failed runs, missing data and counterevidence. Never upgrade a claim's status because multiple LLM agents agree.

### Minimum claim record (recommended)

- Stable claim ID and run ID.
- Exact claim text and claim type.
- Assumptions and definitions.
- Derivation or evidence chain.
- Source IDs / DOI / URLs and exact supporting locations.
- Counterevidence and alternative explanations.
- Numerical/code artefacts and reproducibility metadata.
- Reviewer/reproducer decisions.
- Confidence/uncertainty and current verification status.

### Literature status at the Phase 3 checkpoint

Phase 3 used OpenAlex discovery and Crossref DOI metadata checks. It generally retrieved up to five scholarly records per work item. Some records had DOI title matches, some lacked DOI or Crossref verification, and at least one title mismatch was observed. Exact aggregate counts should be recomputed from Neon rather than copied from old logs.

**Important limitation:** the Phase 3 literature work was primarily metadata/abstract-level discovery. It did not constitute systematic full-text review. Crossref title matching is not scientific validation. Source-level claims still need verification against primary full text or authoritative data.

---

## 9. Phase history and verified status

### Phase 0 — Cloud infrastructure: COMPLETE

- Colab cloud execution, Neon database connectivity, GitHub connectivity and object-storage path established.
- Bootstrap health report created.
- No inference calls during initial bootstrap.

### Phase 1 — Agent swarm and persistence: COMPLETE

- Database schema and initial six-team/18-agent logical roster created.
- Task queue, message bus, provider adapters and persistence modules integrated.
- Main research run created: `run_64ca8ea8354347659fe78f63b8569a67`.

### Phase 2 — Initial research and synthesis: COMPLETE (workflow checkpointed)

- Initial agent tasks executed, with provider rate limits causing failures on some initial attempts.
- OpenRouter fallback adapter added and tested.
- 18/18 initial agent outputs eventually completed, with original assignments and actual provider attempts recorded.
- Six team syntheses, one global synthesis and one adversarial review saved in `asde_research_stage_outputs` (exact table/schema should be checked in Neon).
- Phase 2 initially hardcoded OpenRouter for eight synthesis/review calls; this was a routing mistake and was corrected in subsequent work. Do not repeat it.
- LLM synthesis is a research lead, not scientific validation.

### Phase 3 — Domain knowledge and research infrastructure: COMPLETE (checkpoint integrity verified)

Seven registered domains:

1. `quantum_foundations`
2. `cmb_cosmology`
3. `early_universe`
4. `mathematical_physics`
5. `qft_thermalisation`
6. `scientific_computing`
7. `experimental_evidence`

Ten work items:

| Work item | Topic |
|---|---|
| `p3_quantum_foundations_01` | Formalise measurement independence |
| `p3_quantum_foundations_02` | Reconcile Bell and measurement-dependence bounds |
| `p3_cmb_cosmology_03` | Build CMB domain knowledge base |
| `p3_cmb_cosmology_04` | Map possible CMB discriminators |
| `p3_early_universe_05` | Formalise early-universe mechanisms |
| `p3_mathematical_physics_06` | Audit mathematical claims |
| `p3_qft_thermalisation_07` | Review thermalisation/decoherence |
| `p3_scientific_computing_08` | Create reproducible experiment framework |
| `p3_experimental_evidence_09` | Create observational evidence map |
| `p3_experimental_evidence_10` | Design discriminating experiments |

Phase 3 added domain workstream, knowledge-source, work-item and research-output tables; installed/verified core scientific libraries; created manifests and requirements files; and published reports to GitHub.

**Final integrity result from 1 Nov 2026:**

- Neon outputs: 10/10 valid completed records.
- GitHub reports: 10/10 present under `research/phase3/reports/`.
- Missing Neon outputs: 0.
- Incomplete work items: 0.
- Last reconciliation published `research/phase3/reports/p3_scientific_computing_08.json`.
- Final message: `SUCCESS — ALL 10 REPORTS VERIFIED ON GITHUB`.

The Phase 3 checkpoint repair required recovering two missing Neon rows from GitHub (`p3_qft_thermalisation_07`, `p3_experimental_evidence_10`) and publishing one missing GitHub report (`p3_scientific_computing_08`). The repair was persistence-only and used no LLM inference calls.

**Scientific limitation:** Phase 3 outputs are mostly LLM-generated domain research summaries and a proposed experiment framework. They are not actual completed numerical experiments, full-text systematic reviews, independent replications or validated scientific discoveries. CMB has been scoped as a domain but not yet subjected to a full CAMB/CLASS/healpy analysis.

---

## 10. Roadmap: remaining phases

### Phase 4 — Formal mathematical and physical model development (NEXT)

Objective: convert the research questions into explicit, mathematically defined competing models and verify derivations computationally.

Expected workstreams:

1. **Formal foundations:** Define hidden variables, settings, outcomes, measurement dependence, locality/factorisability, realism/ontic assumptions and relevant probability distributions. Be precise about which notion of locality is used.
2. **Bell analysis:** Re-derive relevant Bell/CHSH inequalities under explicit assumptions; identify exactly which assumption is relaxed in each alternative model. Compare measurement-dependent bounds and known limiting cases.
3. **Causal/statistical structure:** Express dependencies with conditional distributions and, where useful, causal graphs. Distinguish statistical dependence from causal influence.
4. **Mathematical consistency:** Check normalisation, positivity, parameter bounds, symmetries, dimensional consistency and limiting behaviour.
5. **Symbolic verification:** Use SymPy for algebra, simplification, differentiation/integration, equation solving and consistency checks. Save executable derivation notebooks/scripts and test cases.
6. **Competing model baselines:** Implement at least one standard quantum baseline and carefully defined alternative models; do not compare vague labels.
7. **Parameter identification:** Identify free parameters, constraints, degeneracies and what data could constrain them.
8. **Independent review:** Mathematics and adversarial teams challenge derivations; an independent reproducer reconstructs key results from definitions and code.
9. **Decision gate:** Only models that pass formal checks proceed to Phase 5. Record unresolved proofs and failed derivations rather than hiding them.

Deliverables should include formal definitions, assumptions ledger, derivation records, symbolic test suite, model comparison table, claim/evidence links and a Phase 4 report. Do not assert a derivation is correct merely because SymPy returns an expression; independent mathematical reasoning remains necessary.

### Phase 5 — Numerical experiments, CMB predictions and observational comparison

- Implement reproducible simulations for Phase 4 models.
- Identify observables that differ between models.
- For CMB work, assess whether a model yields a distinct, calculable signature in spectra/statistics (e.g. only where theoretically justified); compare with appropriate baseline cosmology and public observations.
- Consider CAMB or CLASS for cosmological transfer functions/background calculations; healpy/NaMaster for map/power-spectrum analysis; Astropy for units/cosmological utilities; SciPy/NumPy for numerical methods. Install optional packages only when needed and compatible with the current Colab Python runtime.
- Use public authoritative datasets and document masks, beams, noise, foreground treatment, likelihoods, priors, covariance and selection effects.
- Do not claim a CMB prediction exists until it has been derived from a specified model and numerically evaluated.

### Phase 6 — Independent replication and falsification

- Separate reproduction teams from original model authors.
- Re-run derivations and simulations from recorded inputs/code.
- Perform sensitivity analyses, null tests, parameter sweeps and alternative-model comparisons.
- Search actively for counterexamples, contradictions and observations that would rule out the model.
- Record failures and negative results.
- No claim becomes independently replicated without a distinct reproducibility trail.

### Phase 7 — Synthesis and reproducibility package

- Synthesize only results that survived the previous gates.
- Produce a complete reproducibility package: source catalogue, data provenance, code, environment/package versions, parameters, seeds, outputs, logs and limitations.
- Prepare research manuscript materials only when evidence warrants them; clearly separate established results, derived results, conjectures and open problems.

---

## 11. Phase 4 design rules for the next session

Before executing Phase 4:

1. Read this file and inspect the current GitHub tree and Neon schema. Do not rebuild infrastructure that already exists.
2. Recover the current run and project state from Neon. Do not create a duplicate run unless deliberately starting a new research branch.
3. Read the Phase 3 reports and relevant Phase 2 synthesis/review artefacts from GitHub/Neon. Use them as leads, not unquestioned truth.
4. Design Phase 4 as one complete, self-contained Colab cell in `ADSE_MASTER.ipynb`.
5. The cell should be idempotent and checkpoint after each bounded work unit. It must resume safely after Colab restart.
6. Use Groq primary and automatic OpenRouter fallback on any Groq error. Preserve provider/model attempt provenance. If both fail, stop and checkpoint.
7. Avoid unnecessary LLM calls. Use LLMs to propose/critique; use SymPy/SciPy and independently executable tests to verify mathematical/computational properties.
8. Add no new paid services. Do not use Google Drive.
9. Store source/derivation/result metadata in Neon; store substantial artefacts in Neon Object Storage and versioned source/reports in GitHub.
10. Add a phase manifest and update this context file at phase completion.

### Suggested Phase 4 work-item design

- Define mathematical primitives and assumption ledger.
- Formalise measurement independence and measurement dependence in probability notation.
- Derive baseline CHSH under explicit factorisation/independence assumptions.
- Derive or reconstruct selected measurement-dependent bounds from verified primary sources.
- Check limiting cases and parameter constraints symbolically.
- Construct explicit toy distributions only as mathematical examples, clearly labelled as such.
- Compare predictions and assumptions across model classes.
- Conduct independent derivation audit and counterexample search.
- Produce a gated Phase 4 synthesis.

Do not invent a new theorem, equation or citation. Retrieve and verify original sources before attributing known bounds/results. Distinguish an independently derived result from a reproduced published result.

---

## 12. Repository organisation (target/known paths)

Known Phase 3 paths:

```text
research/
  phase3/
    phase3_manifest.json
    requirements-core.txt
    requirements-cosmology-optional.txt
    ROADMAP.md
    PHASE3_INTEGRITY_AUDIT.json
    reports/
      p3_quantum_foundations_01.json
      p3_quantum_foundations_02.json
      p3_cmb_cosmology_03.json
      p3_cmb_cosmology_04.json
      p3_early_universe_05.json
      p3_mathematical_physics_06.json
      p3_qft_thermalisation_07.json
      p3_scientific_computing_08.json
      p3_experimental_evidence_09.json
      p3_experimental_evidence_10.json
```

The exact repository tree may contain additional code/modules from earlier phases. Inspect before changing. The canonical handoff should live at repository root as `ASDE_CONTEXT.md` so a new session can find it immediately.

---

## 13. Current known risks and unresolved issues

- Provider quotas/rate limits can interrupt a batch; design for sequential bounded work and resumability.
- Current OpenRouter daily quota is unknown; do not assume historical remaining counts are current.
- Free Colab runtime can disconnect and has no guaranteed GPU/continuous execution.
- Phase 3 literature is not a full-text systematic review; source verification is still needed.
- Some Crossref metadata checks were unavailable or unmatched; audit source records before citing them as evidence.
- Optional CMB libraries have not all been installed/tested in this runtime; check Python 3.13 compatibility before installation.
- Phase 3 scientific-computing work item is a framework/specification, not a completed scientific experiment.
- A past Gemini key was exposed in error URLs; verify the old key is revoked and prevent secrets in URLs/logs.
- Avoid overclaiming “autonomous discovery”: the current system is an evolving agent-orchestration/research workflow with human-triggered Colab execution and external quota constraints.

---

## 14. Instructions to a new ChatGPT conversation

You are continuing an existing project, not starting from scratch.

**First, acknowledge and preserve these facts:**

- Project is ASDE; master notebook is `ADSE_MASTER.ipynb`.
- GitHub repo is `Prashantkumariitd/ASDE`, branch `main`.
- Neon is the persistent database; no Google Drive.
- Current run ID is `run_64ca8ea8354347659fe78f63b8569a67`.
- Phases 0–3 are complete at the infrastructure/workflow checkpoint level. Phase 3 has 10/10 valid Neon outputs and 10/10 GitHub reports.
- Phase 4 is next; its focus is formal mathematical/physical model development, not another round of generic summaries.
- Groq is primary; OpenRouter free is automatic fallback on any Groq error. If both fail, checkpoint and pause. Never silently downgrade.
- Zero budget, cloud-only, Colab free constraints, no Drive, one notebook, one complete cell per phase.
- Scientific skepticism, source provenance, derivations, independent replication and falsification are mandatory.

**Then do this:**

1. Ask no questions whose answers are already in this file.
2. If current repo/database access is available, inspect the current project state before making changes. If not, provide a single safe Colab cell to inspect or continue.
3. Do not assume this document contains every code detail; inspect actual repository modules and Neon schema before modifying them.
4. Do not claim any scientific conclusion is established unless the recorded evidence supports it.
5. Keep this context file current and publish updates to GitHub after significant milestones.

---

## 15. Checkpoint maintenance

At the end of every phase or major architecture change, update:

- Current date and run ID(s).
- Phase status and verification counts.
- Added/changed database tables and actual column types.
- GitHub paths created/modified.
- Provider routing changes and observed quota/error conditions (never secrets).
- Installed scientific library versions.
- Research questions, assumptions, claims and their verification states.
- Failed tasks, known bugs and exact next action.

Keep the filename stable: **`ASDE_CONTEXT.md`**. A new conversation should be able to start by reading this one file.

---

**End of handoff document.**

## Phase 4 execution checkpoint

- Phase 4 initiated: 2026-11-01T03:49:01.873875+00:00.
- Run ID: `run_64ca8ea8354347659fe78f63b8569a67`.
- Phase 3 integrity audit accepted by user.
- Phase 4 work packages: 7.
- Formal CHSH deterministic baseline exhaustively checked over 16 assignments.
- Quantum singlet CHSH baseline numerically checked against 2√2.
- Phase 4 model classes registered as proposed, not established physical theories.
- Provider policy: Groq primary; automatic OpenRouter fallback on any Groq error; pause if both fail.
- Phase 4 execution is checkpointed in Neon and GitHub.


## Phase 5.1 checkpoint — CHSH numerical experiment

- Date: 2026-11-01
- Run: `run_64ca8ea8354347659fe78f63b8569a67`
- Experiment: `p5_1_chsh_mi_vs_md_v1`
- Status: `completed`
- Report: `research/phase5/reports/p5_1_chsh_mi_vs_md.json`
- Manifest: `research/phase5/phase5_manifest.json`
- Neon tables: `asde_phase5_experiments`, `asde_phase5_checks`
- Checks: 12/12 passed.
- Quantum singlet CHSH target: -2.828427124746.
- Deterministic local CHSH maximum: 2.
- MI LP feasible: `False`.
- MD LP feasible: `True`.
- Minimum maximum pairwise TV in the specified representation: 0.138071187458.
- Maximum MD joint-probability reconstruction error: 5.551e-17.
- Maximum no-signalling reconstruction error: 0.000e+00.
- Provider calls: 0; this phase used numerical optimisation only.
- Interpretation: the LP result is representation- and metric-specific. It does not establish a physical superdeterministic mechanism or the truth of any underlying framework.

<!-- ASDE_PHASE5_STATUS_START -->
## Phase 5 — Numerical experiments and observational predictions

### Phase 5.1 — CHSH MI vs MD
- User-reported completed experiment: `p5_1_chsh_mi_vs_md_v1`.
- Quantum CHSH: -2.828427124746.
- Local deterministic maximum absolute CHSH: 2.
- MI LP infeasible; MD LP feasible.
- Minimum maximum pairwise TV: 0.138071187458.
- Report: `research/phase5/reports/p5_1_chsh_mi_vs_md.json`.
- User-reported validation: 12/12 checks passed.

### Phase 5.2 — Mathematical audit
- Experiment: `p5_2_mathematical_audit_v1`.
- Status: `completed`.
- Numerical CHSH: `-2.828427124746`.
- Minimum maximum pairwise TV: `0.138071187458`.
- Mutual information I(Lambda:XY): `0.046273846924` bits.
- LP primal-dual gap: `2.7755575615628914e-17`.
- MI optimiser success: `True`.
- Validation: 24/24.
- Report: `research/phase5/reports/p5_2_mathematical_audit.json`.
- Angle sweep: `research/phase5/computations/p5_2_angle_sensitivity.json`.

Scientific boundary:
- LP duality is checked numerically, not by a formal exact-arithmetic certificate.
- Mutual information is obtained by numerical constrained optimisation.
- Hidden-variable label permutation is not a general representation-independence proof.
- No physical mechanism for measurement dependence has been established.
- No CMB prediction has been derived; the CMB gate remains blocked.

Next:
1. Review the dual certificate and independently verify its signs and residuals.
2. Improve mutual-information optimisation with an independent convex solver or certified bounds.
3. Test alternative hidden-variable representations and setting priors.
4. Develop a physical dynamical mechanism before attempting CMB predictions.
<!-- ASDE_PHASE5_STATUS_END -->


<!-- ASDE_PHASE5_3_5_7_START -->
## Phase 5.3–5.7 checkpoint

Updated: 2026-11-01T04:08:26.800695+00:00
Run: run_64ca8ea8354347659fe78f63b8569a67

- Phase 5.3: Robustness and representation audit executed.
- Phase 5.4: Physical mechanism gate blocked; no specified mechanism.
- Phase 5.5: Experimental evidence inventory only; no raw Bell dataset reanalysis.
- Phase 5.6: CMB/early-universe gate blocked; no derived cosmological prediction.
- Phase 5.7: Independent numerical formulation and adversarial checks executed.
- LLM/API inference calls: 0.
- Primary LP and independently ordered LP compared.
- MI results are numerical SLSQP results, not global optimality proofs.
- No claim of proving superdeterminism.

Scientific status:
The tested finite local measurement-dependent representation reproduces the selected singlet CHSH target. This does not establish a physical mechanism or empirical evidence for superdeterminism.

Reports:
- research/phase5/reports/p5_3_robustness_representation.json
- research/phase5/reports/p5_4_physical_mechanism_gate.json
- research/phase5/reports/p5_5_experimental_evidence_gate.json
- research/phase5/reports/p5_6_cosmology_gate.json
- research/phase5/reports/p5_7_independent_verification.json
- research/phase5/reports/phase5_3_to_5_7_combined.json
<!-- ASDE_PHASE5_3_5_7_END -->

