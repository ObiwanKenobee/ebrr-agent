import json
from pathlib import Path

from ebrr.budget import BudgetLedger, ResourceBudget
from ebrr.retrieval import EBRRRetriever, RetrievalConfig
from ebrr.symbols import RepositorySymbolIndex


class FakeGraphTools:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def search_similar_code(self, query: str, k: int = 10) -> str:
        self.calls.append(("similar", query))
        return json.dumps(
            {
                "status": "ok",
                "query": query,
                "results": [
                    {"node_name": "pkg.client.retry_request", "similarity": 0.88},
                    {"node_name": query, "similarity": 1.0},
                ][:k],
                "is_truncated": False,
            }
        )

    def get_code_neighbors(
        self, node: str, edge_type: str | None = None, max_neighbors: int = 50
    ) -> str:
        self.calls.append(("neighbors", node))
        return json.dumps(
            {
                "status": "ok",
                "node": node,
                "neighbors": [
                    "pkg.client.parse_response",
                    "pkg.client.retry_request",
                ][:max_neighbors],
                "is_truncated": False,
            }
        )

    def get_code_subgraph(self, nodes: list[str]) -> str:
        self.calls.append(("subgraph", tuple(nodes)))
        return json.dumps(
            {
                "status": "ok",
                "nodes": nodes,
                "edges": [{"from": nodes[0], "to": nodes[1], "type": "CALLS"}],
                "is_truncated": False,
            }
        )


def make_index(tmp_path: Path) -> RepositorySymbolIndex:
    (tmp_path / "client.py").write_text(
        "class HTTPClient:\n"
        "    def parse_response(self, payload):\n"
        "        return payload\n"
        "    def retry_request(self, request):\n"
        "        return request\n",
        encoding="utf-8",
    )
    return RepositorySymbolIndex.from_repository(tmp_path)


def make_ledger(tool_calls: int = 20, graph_expansions: int = 10) -> BudgetLedger:
    return BudgetLedger(
        ResourceBudget(
            max_tokens=1000,
            max_tool_calls=tool_calls,
            max_graph_expansions=graph_expansions,
            max_verification_actions=5,
        )
    )


def test_retriever_grounds_issue_then_calls_graph_tools(tmp_path: Path) -> None:
    index = make_index(tmp_path)
    tools = FakeGraphTools()
    ledger = make_ledger()
    retriever = EBRRRetriever(
        index,
        tools,
        ledger,
        RetrievalConfig(max_seed_symbols=1, similar_k=3, max_neighbors_per_seed=5),
    )

    result = retriever.retrieve("HTTP client fails parsing response")

    assert result.seeds[0].symbol.qualified_name == "client.HTTPClient.parse_response"
    assert result.similar_nodes[0].node_name == "pkg.client.retry_request"
    assert result.neighbor_map[0][1][0] == "pkg.client.parse_response"
    assert len(result.subgraph_nodes) >= 2
    assert result.tool_calls == 3
    assert result.graph_expansions == 2
    assert ledger.usage.tool_calls == 3
    assert [call[0] for call in tools.calls] == ["similar", "neighbors", "subgraph"]


def test_missing_graph_tools_returns_lexical_candidates_without_failure(tmp_path: Path) -> None:
    index = make_index(tmp_path)
    result = EBRRRetriever(index, None, make_ledger()).retrieve("HTTP client response")

    assert result.seeds
    assert result.stop_reason == "graph_tools_unavailable"
    assert result.tool_calls == 0
    assert result.warnings


def test_no_symbol_candidates_do_not_spend_graph_budget(tmp_path: Path) -> None:
    index = make_index(tmp_path)
    tools = FakeGraphTools()
    ledger = make_ledger()
    result = EBRRRetriever(index, tools, ledger).retrieve("unrelated terminology")

    assert result.stop_reason == "no_symbol_candidates"
    assert tools.calls == []
    assert ledger.usage.tool_calls == 0


def test_tool_call_budget_stops_safely(tmp_path: Path) -> None:
    index = make_index(tmp_path)
    tools = FakeGraphTools()
    ledger = make_ledger(tool_calls=1)
    result = EBRRRetriever(
        index,
        tools,
        ledger,
        RetrievalConfig(max_seed_symbols=1, similar_k=3, max_neighbors_per_seed=5),
    ).retrieve("HTTP client fails parsing response")

    assert result.tool_calls == 1
    assert result.stop_reason == "tool_call_budget_exhausted"
    assert ledger.usage.tool_calls == 1
    assert ledger.usage.graph_expansions == 0
    assert not result.neighbor_map


def test_graph_expansion_budget_stops_before_neighbor_tool(tmp_path: Path) -> None:
    index = make_index(tmp_path)
    tools = FakeGraphTools()
    ledger = make_ledger(graph_expansions=0)
    result = EBRRRetriever(
        index,
        tools,
        ledger,
        RetrievalConfig(max_seed_symbols=1, similar_k=2, max_neighbors_per_seed=5),
    ).retrieve("HTTP client response")

    assert result.stop_reason == "graph_expansion_budget_exhausted"
    assert [call[0] for call in tools.calls] == ["similar"]
    assert ledger.usage.graph_expansions == 0


def test_tool_errors_are_recorded_and_do_not_crash_run(tmp_path: Path) -> None:
    class BrokenGraphTools(FakeGraphTools):
        def search_similar_code(self, query: str, k: int = 10) -> str:
            return '{"status":"error","error_message":"graph unavailable"}'

    index = make_index(tmp_path)
    result = EBRRRetriever(
        index,
        BrokenGraphTools(),
        make_ledger(),
        RetrievalConfig(max_seed_symbols=1, similar_k=2, max_neighbors_per_seed=0),
    ).retrieve("HTTP client response")

    assert result.seeds
    assert any("graph unavailable" in warning for warning in result.warnings)
