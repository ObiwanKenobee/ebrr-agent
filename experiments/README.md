# Experiments

Store one directory per experiment family. Each run must include a frozen config, code commit, harness/dataset/model identifiers, seed, environment, logs, and structured results.

Suggested progression:

1. `00_harness_audit/` — inspect tools, graph schema, embedding access, and evaluation interface.
2. `01_retrieval/` — compare lexical, graph, and symbol-grounded retrieval.
3. `02_repair/` — paired end-to-end repair comparison.
4. `03_ablations/` — remove one EBRR component at a time.
5. `04_generalization/` — repository-held-out analysis where sample size permits.

Do not place raw benchmark repositories, private code, hidden tests, reference patches, or credentials in this directory.
