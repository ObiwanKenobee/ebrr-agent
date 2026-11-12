# Research plan

## Working title

**Ground Before You Generate: Evidence-Budgeted Repository Reasoning for Reliable Small Language Model Software Engineering Agents**

## Central question

Can compact language models achieve more reliable repository-level software engineering by combining symbol grounding, repository-graph navigation, explicit evidence provenance, adaptive exploration, and targeted verification under fixed resource budgets?

## Proposed contribution

Evidence-Budgeted Repository Reasoning (EBRR) is a proposed architecture and experimental framework. It treats repository repair as a sequence of evidence-gathering and decision steps rather than unrestricted text generation. The agent should identify candidate symbols, traverse relevant structural relationships, maintain traceable evidence for competing diagnoses, spend a bounded exploration budget, and validate candidate changes.

The contribution is not the existence of code graphs, retrieval, or staged repair individually. Those are established research directions. The intended contribution is a controlled study of their interaction under constrained inference and tool budgets, with explicit evidence-state tracking and adaptive stopping.

## Research questions

- **RQ1 — Structural localization:** Does AST/code-graph navigation improve localization over lexical search under equal retrieval budgets?
- **RQ2 — Symbol grounding:** Does mapping natural-language issues to candidate symbols before graph/embedding retrieval improve relevant-code recall and ranking?
- **RQ3 — Evidence discipline:** Does explicit provenance and separation of observations from hypotheses reduce unsupported diagnoses and unnecessary edits?
- **RQ4 — Adaptive exploration:** Can a stopping policy improve the trade-off between repair success, context quality, tool calls, and runtime?
- **RQ5 — Resource-constrained capability:** Which components provide the largest reliability gain per unit of compute for a compact model?

## Hypotheses (not results)

- H1: Graph-augmented retrieval improves localization when relevant relationships are represented in the graph and the agent can access them correctly.
- H2: Symbol grounding improves retrieval when the tool interface is keyed by code symbols rather than arbitrary natural-language queries.
- H3: Evidence provenance and competing hypotheses reduce unsupported patch rationales.
- H4: A budget-aware stopping policy can reduce redundant exploration without materially harming repair success.
- H5: Improvements vary by task type, repository structure, and graph/tool quality; some tasks may not benefit from graph reasoning.

## Scope

The first study should prioritize repository-level Python issue repair and the exact competition harness/data made available to participants. The harness, data schema, licenses, and evaluation interface must be audited before implementation. Broader language and repository generalization is a later study.

## Success criteria

Success is not defined as winning a leaderboard. The research should deliver:

1. An executable and documented method.
2. Fair, budget-matched baselines.
3. A leakage-resistant evaluation protocol.
4. Ablations that isolate the contribution of each component.
5. Per-task and aggregate outcomes, including failures.
6. Reproducible run metadata and a candid limitations section.

## Non-goals for the first iteration

- Training a foundation model from scratch.
- Building a general-purpose multi-agent platform.
- Building a web dashboard.
- Claiming universal superiority over frontier models.
- Extending to multiple programming languages before the benchmark adapter is validated.
