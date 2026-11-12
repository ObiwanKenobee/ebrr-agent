# Experiment protocol

This document defines the minimum standard for experiments. Update it before any protocol change and record deviations in each run.

## Phase 0 — Audit the benchmark interface

Before implementing an adapter, inspect and document:

- Competition harness version and source revision.
- Task schema and task sampling rules.
- Repository snapshots and language coverage.
- Code graph node/edge schema and indexing assumptions.
- Embedding dimension, model/source, key semantics, and lookup API.
- Available file, search, graph, test, and patch tools.
- Which tests are visible to the agent and which are reserved for evaluation.
- Runtime, token, tool-call, hardware, and network restrictions.
- Licenses and data redistribution rules.

Record verified facts with source links or local artifact hashes. If an interface detail is unknown, label it unknown and test it; do not infer it from a stale mirror or a different harness version.

## Baselines

Compare methods with the same base model, prompt budget, tool access, task set, patch interface, and verifier wherever possible.

- **B0 — Lexical baseline:** issue terms, stack-trace terms, and conventional text search.
- **B1 — Direct structural baseline:** graph navigation using the harness's documented interface without the proposed symbol-grounding stage.
- **B2 — Symbol-grounded retrieval:** infer candidate symbols, then retrieve code and graph neighborhoods from those anchors.
- **B3 — EBRR:** symbol grounding plus evidence ledger, adaptive budget allocation, explicit stopping, and targeted verification.

If a baseline cannot be made budget-equivalent, document the discrepancy and do not present the comparison as strictly controlled.

## Evaluation phases

### A. Retrieval/localization diagnostics

Measure relevant-code Recall@k, Precision@k where labels permit, mean reciprocal rank, and retrieval volume. Define relevance labels before inspecting model outputs. If labels are derived from reference patches, keep reference artifacts sealed from the agent and disclose the labeling method.

### B. End-to-end repair

Measure benchmark-defined resolved rate, test acceptance, regression failures, patch size, tool calls, tokens, wall-clock duration, and verification actions. Report both per-task outcomes and aggregates.

### C. Ablations

Remove one component at a time: graph navigation, symbol grounding, provenance ledger, adaptive exploration/stopping, or staged verification. Keep other settings fixed.

### D. Generalization

Where the sample supports it, use repository-held-out evaluation. Do not treat multiple tasks from the same repository as independent evidence of broad ecosystem generalization. Report repository/task counts and imbalance.

## Leakage controls

- Never provide the reference patch to the agent.
- Keep hidden validation tests inaccessible to the agent.
- Do not select prompts or hyperparameters by repeatedly inspecting hidden-test outcomes.
- Use validation tasks for method development and reserve a held-out test set for final reporting where possible.
- Ensure retrieval indexes do not contain reference fixes or future repository states.
- Record any unavoidable exposure and its possible effect on validity.

## Statistical reporting

- Report task-level results, not only one aggregate score.
- Use paired comparisons on the same tasks.
- Report uncertainty intervals and the method used to calculate them.
- For small samples, avoid overconfident significance claims; include descriptive counts and effect sizes.
- Stratify by task type/repository only when sample sizes make the breakdown meaningful.
- Report failed runs, timeouts, invalid patches, and missing telemetry.

## Run metadata

Every run should record:

```yaml
run_id: YYYYMMDD-method-seed
code_commit: <git SHA>
harness_revision: <tag or SHA>
dataset_version: <identifier and checksum>
model_id: <exact identifier>
model_revision: <revision or checksum>
quantization: <method or null>
seed: <integer>
hardware: <CPU/GPU and memory>
software_environment: <OS, Python, relevant package versions>
method: <baseline name>
config_path: <path>
start_utc: <ISO-8601>
end_utc: <ISO-8601>
status: <complete|partial|failed>
notes: <deviations and caveats>
```

Do not commit secrets, private model files, raw proprietary repositories, or hidden tests. Commit small aggregate metrics and run manifests when licensing permits.
