# Ground Before You Generate

**Evidence-Budgeted Repository Reasoning (EBRR)** for reliable, resource-constrained software engineering agents.

> Research implementation in progress. The repository now contains a deterministic AST symbol index, a defensive adapter for the competition graph-tool response format, and a budget-aware symbol-grounded retrieval controller. It does **not** yet contain a Gemma fine-tune, a live ADK integration, a benchmark result, or a claim of improved repair performance.

## Research question

Can compact language models become more reliable at repository-level software engineering when they combine symbol grounding, repository-graph navigation, explicit evidence provenance, resource-aware exploration, and targeted verification?

## Proposed contribution

EBRR is a research framework for studying how a small coding agent chooses what to inspect, how it records the evidence behind a diagnosis, how it allocates a limited exploration budget, and how it verifies a proposed patch. The central hypothesis is that better interaction with repository knowledge may improve the practical capability of constrained models. This is a hypothesis to test, not an established result.

## Project status

- [x] Initial research framing and questions
- [x] Architecture and experiment protocol drafts
- [x] Minimal typed evidence and resource-budget primitives
- [x] Initial public competition harness/tool-contract audit (exact Kaggle bundle recheck pending)
- [x] Deterministic AST symbol index and lexical grounding baseline
- [x] Typed graph response adapter and bounded retrieval controller
- [ ] Verify adapters against the exact Kaggle wheel and real graph/embedding files
- [ ] Measure retrieval quality against labeled public development tasks
- [ ] Implement evidence-ledger scoring and adaptive exploration policy
- [ ] Run end-to-end repair experiments
- [ ] Publish reproducible results and paper

See [RESEARCH_STATUS.md](RESEARCH_STATUS.md) for the current evidence boundary and [docs/](docs/) for the research plan. Start with [the harness audit](docs/COMPETITION_HARNESS_AUDIT.md) and [the retrieval baseline note](docs/RETRIEVAL_BASELINE.md).

## Repository layout

```text
.
├── configs/                 # Versioned experiment configuration
├── docs/                    # Research questions, architecture, protocol, governance
├── experiments/             # Experiment definitions and run guidance
├── notebooks/               # Reproducible analysis notebooks (added as needed)
├── results/                 # Small, documented aggregate outputs only
├── scripts/                 # Local developer helpers
├── src/ebrr/                # Minimal, testable research implementation
└── tests/                   # Unit and contract tests
```

## Quick start

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
pytest
ruff check .
```

## Research principles

1. **Ground before generating.** Retrieve and inspect relevant repository evidence before proposing a modification.
2. **Separate epistemic states.** Distinguish observations, hypotheses, and contradicted hypotheses.
3. **Preserve provenance.** A diagnosis must point back to inspectable files, symbols, tests, or execution observations.
4. **Budget exploration.** Record tokens, tool calls, graph expansions, and verification actions.
5. **Verify, do not merely narrate.** Report exactly which checks ran and their outcomes.
6. **Do not leak evaluation answers.** Reference patches and hidden tests are evaluation assets, not agent context.
7. **Report negative results.** Failed tasks and ablations are part of the research record.

## Reproducibility and data

Do not commit benchmark repositories, private code, model weights, credentials, Kaggle secrets, or hidden test data. Before downloading or redistributing any dataset or repository snapshot, record its source, license, version, permitted use, and checksum. See [Data governance](docs/DATA_GOVERNANCE.md).

Each experiment should have a frozen configuration, code revision, model identifier and revision, dataset version, random seed, hardware/runtime description, and machine-readable results. See [Experiment protocol](docs/EXPERIMENT_PROTOCOL.md).

The retrieval core is deterministic and model-independent. Its graph-tool protocol is injectable for local tests; it is not yet connected directly to the competition ADK runtime. Unit tests use synthetic repositories and fake graph-tool responses, not the Kaggle task dataset.

## Citation

A citation file is provided in [`CITATION.cff`](CITATION.cff). Please cite the repository using its GitHub URL and release/tag once a citable release exists. The research paper is not yet published.

## License

The scaffold is released under the MIT License. This does not grant rights to third-party datasets, benchmark repositories, model weights, or dependencies; their own licenses apply.
