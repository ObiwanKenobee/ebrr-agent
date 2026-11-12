"""Typed, defensive adapter for the Gemma developer-agent graph tools."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol


class GraphToolError(RuntimeError):
    """Raised when a harness graph tool reports an error or invalid response."""


class GraphTools(Protocol):
    """Call surface implemented by the competition's injected graph tools."""

    def search_similar_code(self, query: str, k: int = 10) -> str: ...

    def get_code_neighbors(
        self, node: str, edge_type: str | None = None, max_neighbors: int = 50
    ) -> str: ...

    def get_code_subgraph(self, nodes: list[str]) -> str: ...


@dataclass(frozen=True, slots=True)
class SimilarCodeNode:
    node_name: str
    similarity: float | None = None
    code: str | None = None


@dataclass(frozen=True, slots=True)
class SimilarCodeResponse:
    query: str
    results: tuple[SimilarCodeNode, ...]
    is_truncated: bool = False


@dataclass(frozen=True, slots=True)
class NeighborsResponse:
    node: str
    neighbors: tuple[str, ...]
    is_truncated: bool = False


@dataclass(frozen=True, slots=True)
class SubgraphEdge:
    source: str
    target: str
    edge_type: str | None = None


@dataclass(frozen=True, slots=True)
class SubgraphResponse:
    nodes: tuple[str, ...]
    edges: tuple[SubgraphEdge, ...]
    is_truncated: bool = False


def _decode_response(raw: str | Mapping[str, object]) -> Mapping[str, object]:
    if isinstance(raw, Mapping):
        payload = raw
    elif isinstance(raw, str):
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GraphToolError(f"graph tool returned invalid JSON: {exc.msg}") from exc
        if not isinstance(decoded, Mapping):
            raise GraphToolError("graph tool response must be a JSON object")
        payload = decoded
    else:
        raise GraphToolError(f"unsupported graph tool response type: {type(raw).__name__}")

    status = payload.get("status")
    if status == "error":
        message = payload.get("error_message", payload.get("error", "unspecified graph error"))
        raise GraphToolError(str(message))
    if status not in (None, "ok"):
        raise GraphToolError(f"unexpected graph tool status: {status!r}")
    return payload


def parse_similar_code_response(raw: str | Mapping[str, object]) -> SimilarCodeResponse:
    payload = _decode_response(raw)
    query = payload.get("query", "")
    results = payload.get("results", [])
    if not isinstance(query, str) or not isinstance(results, Sequence) or isinstance(results, str):
        raise GraphToolError("similar-code response has invalid 'query' or 'results' fields")

    parsed: list[SimilarCodeNode] = []
    for index, item in enumerate(results):
        if not isinstance(item, Mapping):
            raise GraphToolError(f"similar-code result {index} must be an object")
        node_name = item.get("node_name")
        if not isinstance(node_name, str) or not node_name.strip():
            raise GraphToolError(f"similar-code result {index} is missing a valid node_name")
        similarity_value = item.get("similarity")
        if similarity_value is None:
            similarity = None
        else:
            try:
                similarity = float(similarity_value)
            except (TypeError, ValueError) as exc:
                raise GraphToolError(f"similarity for {node_name!r} is not numeric") from exc
        code_value = item.get("code")
        parsed.append(
            SimilarCodeNode(
                node_name=node_name,
                similarity=similarity,
                code=code_value if isinstance(code_value, str) else None,
            )
        )

    return SimilarCodeResponse(
        query=query,
        results=tuple(parsed),
        is_truncated=bool(payload.get("is_truncated", False)),
    )


def parse_neighbors_response(raw: str | Mapping[str, object]) -> NeighborsResponse:
    payload = _decode_response(raw)
    node = payload.get("node", "")
    neighbors = payload.get("neighbors", [])
    if (
        not isinstance(node, str)
        or not isinstance(neighbors, Sequence)
        or isinstance(neighbors, str)
    ):
        raise GraphToolError("neighbor response has invalid 'node' or 'neighbors' fields")
    if any(not isinstance(item, str) for item in neighbors):
        raise GraphToolError("neighbor names must all be strings")
    return NeighborsResponse(
        node=node,
        neighbors=tuple(dict.fromkeys(neighbors)),
        is_truncated=bool(payload.get("is_truncated", False)),
    )


def parse_subgraph_response(raw: str | Mapping[str, object]) -> SubgraphResponse:
    payload = _decode_response(raw)
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])
    if (
        not isinstance(nodes, Sequence)
        or isinstance(nodes, str)
        or not isinstance(edges, Sequence)
        or isinstance(edges, str)
    ):
        raise GraphToolError("subgraph response has invalid 'nodes' or 'edges' fields")
    if any(not isinstance(node, str) for node in nodes):
        raise GraphToolError("subgraph node names must all be strings")

    parsed_edges: list[SubgraphEdge] = []
    for index, item in enumerate(edges):
        if not isinstance(item, Mapping):
            raise GraphToolError(f"subgraph edge {index} must be an object")
        source = item.get("from", item.get("source"))
        target = item.get("to", item.get("target"))
        edge_type = item.get("type")
        if not isinstance(source, str) or not isinstance(target, str):
            raise GraphToolError(f"subgraph edge {index} must contain string endpoints")
        parsed_edges.append(
            SubgraphEdge(source, target, edge_type if isinstance(edge_type, str) else None)
        )

    return SubgraphResponse(
        nodes=tuple(dict.fromkeys(nodes)),
        edges=tuple(parsed_edges),
        is_truncated=bool(payload.get("is_truncated", False)),
    )
