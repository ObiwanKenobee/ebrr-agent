# Instructions for coding agents

This repository is a research project. Correctness, traceability, and honest reporting take priority over speed or impressive-looking output.

## Non-negotiable rules

- Do not claim an experiment ran unless its command, environment, and output are recorded.
- Do not fabricate benchmark metrics, task counts, citations, model identifiers, or hardware specifications.
- Treat reference patches and hidden tests as sealed evaluation material.
- Keep observations, hypotheses, interpretations, and recommendations distinct.
- Preserve provenance for retrieved code and evidence; avoid storing large source excerpts when a path, symbol, line range, and digest suffice.
- Keep benchmark-specific assumptions behind adapters rather than embedding them in core abstractions.
- Prefer deterministic, testable functions and explicit configuration.
- Add tests whenever behavior changes.
- Do not add model providers, datasets, or paid services without documenting the dependency and its cost/privacy implications.

## Development workflow

1. Read `RESEARCH_STATUS.md` and the relevant documents in `docs/`.
2. Identify the smallest testable change.
3. Implement it with types and validation.
4. Add or update tests.
5. Run `pytest` and `ruff check .`.
6. Record experiment-affecting decisions in `docs/DECISION_LOG.md`.
7. Update documentation and status when the research state changes.

## Scope discipline

Do not introduce a multi-agent framework, web UI, cloud deployment, or fine-tuning pipeline until the retrieval baseline and evaluation protocol are stable. Build the smallest system that can falsify the research hypotheses.
