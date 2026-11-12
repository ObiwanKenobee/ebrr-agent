"""Budget-aware symbol-grounded retrieval over the competition graph tools."""

from __future__ import annotations

from dataclasses import dataclass

from ebrr.budget import BudgetExceeded, BudgetLedger
from ebrr.graph import (
    GraphToolError,
    GraphTools,
    SimilarCodeNode,
    SubgraphEdge,
    parse_neighbors_response,
    parse_similar_code_response,
    parse_subgraph_response,
)
from ebrr.symbols import RepositorySymbolIndex, SymbolMatch


@dataclass(frozen=True, slots=True)
class RetrievalConfig:
    """Deterministic limits for one repository retrieval pass."""

    max_seed_symbols: int = 3
    similar_k: int = 5
    max_neighbors_per_seed: int = 12
    max_subgraph_nodes: int = 20

    def __post_init__(self) -> None:
        for name in (
            "max_seed_symbols",
            "similar_k",
            "max_neighbors_per_seed",
            "max_subgraph_nodes",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """The complete inspectable output of a retrieval pass."""

    query: str
    seeds: tuple[SymbolMatch, ...]
    similar_nodes: tuple[SimilarCodeNode, ...]
    neighbor_map: tuple[tuple[str, tuple[str, ...]], ...]
    subgraph_nodes: tuple[str, ...]
    subgraph_edges: tuple[SubgraphEdge, ...]
    warnings: tuple[str, ...]
    stop_reason: str
    tool_calls: int
    graph_expansions: int

    @property
    def selected_nodes(self) -> tuple[str, ...]:
        ordered: dict[str, None] = {}
        for seed in self.seeds:
            ordered.setdefault(seed.symbol.qualified_name, None)
        for similar in self.similar_nodes:
            ordered.setdefault(similar.node_name, None)
        for _, neighbors in self.neighbor_map:
            for neighbor in neighbors:
                ordered.setdefault(neighbor, None)
        return tuple(ordered)


class EBRRRetriever:
    """Retrieve graph context from AST-grounded symbol anchors within a hard budget.

    The class does not call a model. It is deterministic given the repository index,
    graph-tool responses, configuration, and initial budget.
    """

    def __init__(
        self,
        symbol_index: RepositorySymbolIndex,
        graph_tools: GraphTools | None,
        budget: BudgetLedger,
        config: RetrievalConfig | None = None,
    ) -> None:
        self._index = symbol_index
        self._graph_tools = graph_tools
        self._budget = budget
        self._config = config or RetrievalConfig()

    def retrieve(self, issue_text: str) -> RetrievalResult:
        seeds = self._index.rank(issue_text, limit=self._config.max_seed_symbols)
        similar_nodes: dict[str, SimilarCodeNode] = {}
        neighbor_map: list[tuple[str, tuple[str, ...]]] = []
        subgraph_nodes: tuple[str, ...] = ()
        subgraph_edges: tuple[SubgraphEdge, ...] = ()
        warnings: list[str] = []
        start_tool_calls = self._budget.usage.tool_calls
        start_graph_expansions = self._budget.usage.graph_expansions
        stop_reason = "completed"

        if not seeds:
            stop_reason = "no_symbol_candidates"
            return self._result(
                issue_text, seeds, similar_nodes, neighbor_map, subgraph_nodes,
                subgraph_edges, warnings, stop_reason, start_tool_calls, start_graph_expansions,
            )
        if self._graph_tools is None:
            warnings.append("graph tools are unavailable; returned lexical symbol candidates only")
            stop_reason = "graph_tools_unavailable"
            return self._result(
                issue_text, seeds, similar_nodes, neighbor_map, subgraph_nodes,
                subgraph_edges, warnings, stop_reason, start_tool_calls, start_graph_expansions,
            )

        for seed in seeds:
            if self._config.similar_k == 0:
                break
            try:
                self._reserve_tool_call()
                response = parse_similar_code_response(
                    self._graph_tools.search_similar_code(
                        seed.symbol.qualified_name,
                        k=self._config.similar_k,
                    )
                )
            except BudgetExceeded:
                stop_reason = "tool_call_budget_exhausted"
                break
            except GraphToolError as exc:
                warnings.append(
                    f"similar-code lookup failed for {seed.symbol.qualified_name}: {exc}"
                )
                continue
            for node in response.results:
                if node.node_name != seed.symbol.qualified_name:
                    similar_nodes.setdefault(node.node_name, node)
            if response.is_truncated:
                warnings.append(
                    f"similar-code output was truncated for {seed.symbol.qualified_name}"
                )

        # Expand only AST-grounded seeds. Similar nodes are context candidates, not
        # recursively trusted anchors; this keeps graph exploration bounded and auditable.
        for seed in seeds:
            if stop_reason != "completed" or self._config.max_neighbors_per_seed == 0:
                break
            try:
                self._reserve_graph_expansion()
                response = parse_neighbors_response(
                    self._graph_tools.get_code_neighbors(
                        seed.symbol.qualified_name,
                        max_neighbors=self._config.max_neighbors_per_seed,
                    )
                )
            except BudgetExceeded as exc:
                stop_reason = (
                    "graph_expansion_budget_exhausted"
                    if "graph_expansions" in str(exc)
                    else "tool_call_budget_exhausted"
                )
                break
            except GraphToolError as exc:
                warnings.append(f"neighbor lookup failed for {seed.symbol.qualified_name}: {exc}")
                continue
            neighbor_map.append((seed.symbol.qualified_name, response.neighbors))
            if response.is_truncated:
                warnings.append(f"neighbor output was truncated for {seed.symbol.qualified_name}")

        candidate_nodes = self._ordered_nodes(seeds, similar_nodes, neighbor_map)
        candidate_nodes = candidate_nodes[: self._config.max_subgraph_nodes]
        if len(candidate_nodes) >= 2 and stop_reason == "completed":
            try:
                self._reserve_graph_expansion()
                response = parse_subgraph_response(
                    self._graph_tools.get_code_subgraph(candidate_nodes)
                )
                subgraph_nodes = response.nodes
                subgraph_edges = response.edges
                if response.is_truncated:
                    warnings.append("subgraph output was truncated")
            except BudgetExceeded as exc:
                stop_reason = (
                    "graph_expansion_budget_exhausted"
                    if "graph_expansions" in str(exc)
                    else "tool_call_budget_exhausted"
                )
            except GraphToolError as exc:
                warnings.append(f"subgraph lookup failed: {exc}")

        return self._result(
            issue_text, seeds, similar_nodes, neighbor_map, subgraph_nodes,
            subgraph_edges, warnings, stop_reason, start_tool_calls, start_graph_expansions,
        )

    def _reserve_tool_call(self) -> None:
        self._budget.consume_tool_call()

    def _reserve_graph_expansion(self) -> None:
        remaining = self._budget.remaining()
        if remaining.tool_calls < 1:
            raise BudgetExceeded("tool_calls budget exhausted")
        if remaining.graph_expansions < 1:
            raise BudgetExceeded("graph_expansions budget exhausted")
        self._budget.consume_tool_call()
        self._budget.consume_graph_expansion()

    @staticmethod
    def _ordered_nodes(
        seeds: tuple[SymbolMatch, ...],
        similar_nodes: dict[str, SimilarCodeNode],
        neighbor_map: list[tuple[str, tuple[str, ...]]],
    ) -> list[str]:
        ordered: dict[str, None] = {}
        for seed in seeds:
            ordered.setdefault(seed.symbol.qualified_name, None)
        for node_name in similar_nodes:
            ordered.setdefault(node_name, None)
        for _, neighbors in neighbor_map:
            for neighbor in neighbors:
                ordered.setdefault(neighbor, None)
        return list(ordered)

    def _result(
        self,
        query: str,
        seeds: tuple[SymbolMatch, ...],
        similar_nodes: dict[str, SimilarCodeNode],
        neighbor_map: list[tuple[str, tuple[str, ...]]],
        subgraph_nodes: tuple[str, ...],
        subgraph_edges: tuple[SubgraphEdge, ...],
        warnings: list[str],
        stop_reason: str,
        start_tool_calls: int,
        start_graph_expansions: int,
    ) -> RetrievalResult:
        return RetrievalResult(
            query=query,
            seeds=seeds,
            similar_nodes=tuple(similar_nodes.values()),
            neighbor_map=tuple(neighbor_map),
            subgraph_nodes=subgraph_nodes,
            subgraph_edges=subgraph_edges,
            warnings=tuple(warnings),
            stop_reason=stop_reason,
            tool_calls=self._budget.usage.tool_calls - start_tool_calls,
            graph_expansions=self._budget.usage.graph_expansions - start_graph_expansions,
        )
