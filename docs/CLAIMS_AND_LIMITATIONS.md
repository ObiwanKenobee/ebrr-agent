# Claims and limitations register

Use this file to prevent hypotheses from silently turning into reported facts.

| Statement | Current status | Evidence required before claiming |
|---|---|---|
| Code graphs can help repository navigation | Established research direction; task-specific effect unmeasured here | Relevant literature and controlled baseline |
| Symbol grounding improves retrieval | Hypothesis | Paired retrieval experiment |
| Evidence provenance reduces unsupported diagnoses | Hypothesis | Annotation rubric and blinded/consistent evaluation |
| Adaptive budgets improve efficiency | Hypothesis | Budget-matched comparison with raw cost telemetry |
| EBRR improves repair success | Unknown | End-to-end benchmark experiment |
| EBRR works on consumer hardware offline | Design goal, not yet verified | Reproducible local execution and hardware report |

## Known validity threats to examine

- Small or imbalanced task samples.
- Repository-specific artifacts and repeated tasks from the same codebase.
- Incomplete or noisy graph edges and embeddings.
- Baselines receiving different effective context or tool budgets.
- Hidden-test leakage through prompts, indexes, or development feedback.
- Model stochasticity and runtime nondeterminism.
- Inconsistent test environments and flaky tests.
- Cost telemetry that omits provider/runtime overhead.
- Human judgments of evidence quality without a documented rubric.

Update this register as evidence accumulates. Do not delete limitations merely because they weaken the paper's narrative.
