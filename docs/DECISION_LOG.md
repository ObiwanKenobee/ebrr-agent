# Research decision log

Record decisions that affect methods, experiments, data, or reported claims. Newest entries go first.

## D-003 — Ground graph retrieval in locally indexed symbols

**Date:** 2026-11-12  
**Status:** Accepted for the first retrieval baseline

**Decision:** Build a deterministic Python AST symbol index first, rank symbol anchors from issue text, and route graph calls using qualified symbol names. Do not assume the embedding search tool provides live natural-language embeddings.

**Rationale:** The current competition tool surface provides three graph methods. The public mirror of the detailed harness guide describes symbol-key resolution for graph/embedding lookup. A symbol-grounded interface is therefore a safer initial contract than sending arbitrary issue sentences directly to every graph tool.

**Consequences:** The first implementation is an offline/testable retrieval core with an injected graph-tool protocol. It is not yet wired into the competition ADK runtime, and its ranking heuristic has no measured accuracy. The exact behavior must be checked against the active Kaggle bundle and installed wheel before final experiments.

**Evidence:** See [`COMPETITION_HARNESS_AUDIT.md`](COMPETITION_HARNESS_AUDIT.md) and [`RETRIEVAL_BASELINE.md`](RETRIEVAL_BASELINE.md).

## 2026-11-12 — Establish EBRR as the initial research scaffold

- **Decision:** Use Evidence-Budgeted Repository Reasoning (EBRR) as the working architecture and `Ground Before You Generate` as the paper title.
- **Reason:** It brings symbol grounding, graph navigation, evidence provenance, adaptive exploration, and verification into one falsifiable experimental design.
- **Trade-off:** The scope is narrower than a general autonomous-agent platform and focuses first on repository-level Python repair.
- **Status:** Initial proposal. No benchmark results exist yet.
- **Revisit when:** The exact competition harness and data interfaces have been audited.
