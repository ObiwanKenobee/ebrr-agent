# Gemma 4 Developer Agent harness audit

**Audit date:** 2026-11-12  
**Purpose:** Record the external interfaces that the first EBRR retrieval implementation targets.  
**Evidence status:** Public competition page plus a publicly accessible mirror of `HARNESS_README.md`; re-check against the exact Kaggle dataset bundle and installed `swegemma` wheel before final competition experiments.

## Competition task and execution model

The main competition evaluates issue-level software engineering patches using a separate verification phase. The public development materials describe 129 tasks and repository-level graph/embedding assets. The agent operates in an offline workspace and interacts with the sandbox through a fixed tool surface. The evaluation result is determined by the harness verifier, not by the agent's natural-language claim that a repair is complete.

The competition page is the primary reference for the current tool names and submission requirements:

- Competition: https://www.kaggle.com/competitions/gemma-4-developer-agent
- Starter notebook: https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent/input
- Paper track: https://www.kaggle.com/competitions/gemma-4-developer-agent-paper

The detailed contracts below were cross-checked against a public mirror of the bundled harness guide:

- Public mirror: https://github.com/johnsonhk88/kaggle-Google-The-Gemma-4-Developer-Agent-Competition/blob/main/src/sample/HARNESS_README.md
- Relevant source sections: initial prompt and tool reference, especially sections 5–7.

This is a mirror, not a first-party versioned release. If its details disagree with the exact `HARNESS_README.md` and wheel distributed with the active Kaggle dataset, the active dataset wins. Record the wheel version and checksum in the run manifest.

## Graph tool contract targeted by EBRR

| Tool | Input | Output fields consumed by this implementation | Purpose |
|---|---|---|---|
| `search_similar_code` | `query: str`, `k: int` | `status`, `query`, `results[*].node_name`, optional `similarity`, optional `code`, optional `is_truncated` | Retrieve related symbols from precomputed code embeddings. |
| `get_code_neighbors` | `node: str`, optional `edge_type`, `max_neighbors: int` | `status`, `node`, `neighbors`, optional `is_truncated` | Expand callers/callees or dependency relationships around a symbol. |
| `get_code_subgraph` | `nodes: list[str]` | `status`, `nodes`, `edges[*].from`, `edges[*].to`, optional `type`, optional `is_truncated` | Retrieve induced relationships among selected nodes. |

The harness documents successful graph-tool responses as JSON strings with `status: "ok"` and errors as structured JSON with `status: "error"`. Output may be truncated by the harness. The adapter validates these fields and preserves truncation warnings rather than silently treating partial results as complete.

## Important query-resolution constraint

The mirrored harness guide states that graph and embedding lookups are indexed by dotted symbol paths. It recommends symbol-name queries such as `pkg.module.Class.method`, `Class.method`, or `parse_header`, not arbitrary natural-language issue sentences. It describes a symbol resolver and a lexical fallback for some multi-word queries.

EBRR therefore does not call the graph's embedding search with the raw issue description as though a live text-embedding service were guaranteed. The first implementation performs local AST-based symbol grounding and then calls `search_similar_code` with qualified symbol names.

This is a conservative routing choice. The precise behavior must still be verified against the competition's exact active harness version. In particular, do not compare similarity values across different retrieval paths unless the harness confirms they share the same scoring semantics.

## EBRR implementation boundary

Implemented in this repository:

1. Deterministic AST indexing of Python classes, functions and methods.
2. Query-to-symbol ranking using token overlap over identifiers, paths and docstrings.
3. Typed parsers for graph tool JSON responses.
4. A retrieval controller that searches from grounded symbol anchors, expands only the AST-grounded seeds, and requests one bounded induced subgraph.
5. Explicit accounting for tool calls and graph expansions.
6. Graceful behavior when graph tools are unavailable, return malformed data, or hit a budget limit.

Not implemented yet:

- Direct calls to ADK tools from the Kaggle runtime. The Python `GraphTools` protocol is an injectable local/test interface, not a claim that an ordinary Python package can invoke the harness tools from an ADK agent.
- A parser for the competition's actual graph JSON/NPZ files.
- A benchmark adapter for `tasks.jsonl` or repository snapshots.
- Embedding-score calibration, learned symbol grounding, patch generation, or model integration.
- Any measured retrieval or repair performance.

## Offline and safety constraints to preserve

- Assume no network or package installation access inside the task sandbox.
- Keep all file access within the provided workspace.
- Do not provide reference patches or hidden tests to the agent.
- Do not mutate test files to make a patch pass; the verifier strips protected test and runner files from submitted diffs.
- Record tool calls, graph expansions, truncation, failed lookups and verification actions.
- Treat an empty graph result as "no indexed evidence returned," not proof that a symbol or relationship does not exist in source code.
