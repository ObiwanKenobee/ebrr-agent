# EBRR retrieval baseline — implementation note

## Scope

This increment implements a deterministic, model-independent retrieval core. It is intended to make the proposed evidence-routing method testable before adding Gemma prompting, fine-tuning, or a competition-specific submission package.

## Pipeline

```text
Issue text
   |
   v
Python AST symbol index
   |
   v
Deterministic lexical symbol grounding
   |
   +---- search_similar_code(qualified_symbol)
   |
   +---- get_code_neighbors(qualified_symbol)
   |
   v
Ordered candidate set
   |
   +---- get_code_subgraph(bounded_candidates)
   |
   v
RetrievalResult + warnings + budget usage
```

### Symbol indexing

`RepositorySymbolIndex.from_repository(root)` parses Python files under a repository root and indexes classes, functions, asynchronous functions and nested definitions. Each entry stores its relative path, qualified name, language, source line range, kind, optional docstring and test-file flag.

Malformed or unreadable Python files are skipped so one generated or partially edited file does not prevent indexing the rest of a repository. Default exclusions cover common generated, cache, dependency and virtual-environment directories.

`RepositorySymbolIndex.rank(issue_text)` applies deterministic token overlap across symbol names, file paths and docstrings. The score is a ranking heuristic, **not a probability or calibrated confidence**. Test symbols receive a modest ranking penalty but remain available unless explicitly excluded.

### Graph adapter

`ebrr.graph` parses the competition tool response envelopes into typed immutable records. It accepts JSON strings and mappings for testability, rejects malformed payloads, validates endpoint and score types, deduplicates names without changing their first-seen order, and exposes truncation flags.

### Retrieval controller

`EBRRRetriever.retrieve(issue_text)`:

1. Selects the top AST-grounded symbol anchors.
2. Calls `search_similar_code` for each anchor.
3. Calls `get_code_neighbors` only for AST-grounded anchors; it does not recursively trust similar-code nodes as additional seeds.
4. Builds a deterministic candidate ordering: seeds, similar nodes, then neighbors.
5. Requests one induced subgraph if at least two candidate nodes remain and budgets allow it.
6. Returns all selected evidence references, warnings, stop reason, and resource usage.

The current default is three seed symbols, five similar-code results per seed, twelve neighbors per seed, and twenty nodes in the final subgraph. These are initial engineering defaults, not empirically optimized parameters. Change them only through a versioned experiment configuration.

## Resource accounting

- Every graph tool invocation consumes one tool call before invocation. A failed invocation still consumes the attempted call.
- Every `get_code_neighbors` and `get_code_subgraph` operation consumes one graph expansion.
- Similar-code search consumes a tool call but not a graph expansion in this project's current accounting convention.
- A budget is checked before the invocation; no action is started if the reservation fails.
- `RetrievalResult.tool_calls` and `.graph_expansions` report the delta consumed by that retrieval pass.

This accounting convention is a research definition, not a claim about the harness's own separate budget categories. Experiment manifests must record both EBRR counters and native harness counters when available.

## Example

```python
from ebrr import BudgetLedger, EBRRRetriever, RepositorySymbolIndex, ResourceBudget

# graph_tools is an adapter implementing the three-method GraphTools protocol.
index = RepositorySymbolIndex.from_repository("/path/to/repository")
ledger = BudgetLedger(
    ResourceBudget(
        max_tokens=12_000,
        max_tool_calls=20,
        max_graph_expansions=10,
        max_verification_actions=4,
    )
)
retrieval = EBRRRetriever(index, graph_tools, ledger).retrieve(
    "HTTP client does not retry after a connection reset"
)

for match in retrieval.seeds:
    print(match.symbol.qualified_name, match.score, match.matched_terms)
print("Related symbols:", retrieval.selected_nodes)
print("Warnings:", retrieval.warnings)
print("Stop reason:", retrieval.stop_reason)
print("Tool calls:", retrieval.tool_calls)
```

## Validation and limitations

Unit tests use synthetic repositories and fake graph-tool responses. They verify determinism, tokenization, nested symbol indexing, response parsing, tool-call and graph-expansion budgets, truncation-compatible parsing, missing graph handling and explicit tool errors.

These tests do not validate the actual Kaggle wheel, real graph or embedding artifacts, retrieval relevance on the 129 public tasks, or repair success. Those remain the next research and integration steps.
