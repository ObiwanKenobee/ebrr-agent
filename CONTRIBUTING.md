# Contributing

Thank you for helping develop EBRR. Contributions should strengthen empirical rigor and reproducibility.

## Before opening an issue or pull request

- Read `AGENTS.md`, `RESEARCH_STATUS.md`, and the relevant research protocol.
- For research claims, include the supporting experiment, configuration, and artifact.
- For implementation changes, explain the behavior change and add tests.
- Check licenses before adding datasets, repository snapshots, model artifacts, or copied code.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ruff check .
```

## Pull request expectations

A pull request should have one coherent purpose, include tests for changed behavior, update documentation where needed, and state any limitations. Do not include secrets, hidden evaluation data, raw private source repositories, or unreviewed model weights.
