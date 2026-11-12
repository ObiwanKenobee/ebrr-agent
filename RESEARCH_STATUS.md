# Research status and evidence boundary

**Last updated:** 2026-11-12  
**Status:** Groundwork / pre-experimental

## What exists

- A research thesis and five research questions.
- A proposed architecture and controlled comparison plan.
- Typed data structures for issues, symbols, hypotheses, evidence, and verification records.
- A resource-budget ledger with unit tests.
- Documentation describing reproducibility and data-handling requirements.

## What does not yet exist

- A trained or fine-tuned Gemma model.
- A working adapter to the competition harness.
- A validated parser for competition graph/embedding artifacts.
- A benchmark run or measured performance result.
- Evidence that EBRR outperforms any baseline.

## Claims policy

Until experiments are run, describe EBRR as a **proposed architecture** and its expected benefits as **hypotheses**. Never invent task counts, scores, confidence intervals, hardware measurements, or successful repairs. Every result in the paper must be traceable to a committed configuration, run record, and evaluation artifact.

## Immediate next milestone

Audit the exact competition harness and task assets. Document the available tool calls, graph schema, embedding lookup semantics, patch interface, validation behavior, and data-use restrictions before implementing a benchmark adapter.
