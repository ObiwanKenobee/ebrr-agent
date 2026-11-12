# Research status and evidence boundary

**Last updated:** 2026-11-12  
**Status:** Retrieval core implemented / pre-benchmark

## What exists

- A research thesis and five research questions.
- A proposed architecture and controlled comparison plan.
- Typed data structures for issues, symbols, hypotheses, evidence, and verification records.
- A resource-budget ledger with unit tests.
- A deterministic AST-based Python symbol index and issue-to-symbol lexical ranking baseline.
- Defensive parsers for similar-code, neighbor, and induced-subgraph tool responses.
- A budget-aware retrieval controller with explicit stop reasons, truncation warnings, and an injectable graph-tool protocol.
- A public harness interface audit with explicit provenance caveats.
- Unit tests using synthetic repositories and fake graph-tool responses.

## What does not yet exist

- A trained or fine-tuned Gemma model.
- A direct integration with the competition ADK runtime or its actual injected tools.
- A parser for the competition's on-disk graph/embedding artifacts.
- Validation against the exact active Kaggle harness wheel and dataset bundle.
- A benchmark run or measured retrieval/repair performance.
- Evidence that EBRR outperforms any baseline.

## Claims policy

Until experiments are run, describe EBRR as a **proposed architecture** and its expected benefits as **hypotheses**. Never invent task counts, scores, confidence intervals, hardware measurements, or successful repairs. Every result in the paper must be traceable to a committed configuration, run record, and evaluation artifact.

## Immediate next milestone

Run the adapter against the exact competition dataset bundle and wheel. Inspect real graph/embedding artifacts, test symbol resolution and response edge cases, and build a leakage-safe retrieval diagnostic over public development tasks. Keep reference patches out of the agent context; use them only to construct evaluation labels after the protocol is frozen.
