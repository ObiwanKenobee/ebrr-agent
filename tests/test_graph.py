import pytest

from ebrr.graph import (
    GraphToolError,
    parse_neighbors_response,
    parse_similar_code_response,
    parse_subgraph_response,
)


def test_parse_similar_code_response() -> None:
    parsed = parse_similar_code_response(
        '{"status":"ok","query":"pkg.Client.get","results":['
        '{"node_name":"pkg.Client.request","similarity":0.91,"code":"def request(): pass"}],'
        '"count":1,"is_truncated":false}'
    )

    assert parsed.query == "pkg.Client.get"
    assert parsed.results[0].node_name == "pkg.Client.request"
    assert parsed.results[0].similarity == pytest.approx(0.91)


def test_parse_neighbors_deduplicates_without_reordering() -> None:
    parsed = parse_neighbors_response(
        '{"status":"ok","node":"pkg.Client.get",'
        '"neighbors":["pkg.parse","pkg.parse","pkg.retry"],"count":3}'
    )
    assert parsed.neighbors == ("pkg.parse", "pkg.retry")


def test_parse_subgraph_accepts_from_to_and_source_target_endpoints() -> None:
    parsed = parse_subgraph_response(
        '{"status":"ok","nodes":["a","b","a"],"edges":['
        '{"from":"a","to":"b","type":"CALLS"},'
        '{"source":"b","target":"a","type":"IMPORTS"}]}'
    )
    assert parsed.nodes == ("a", "b")
    assert [(edge.source, edge.target) for edge in parsed.edges] == [("a", "b"), ("b", "a")]


@pytest.mark.parametrize(
    "raw",
    [
        "not json",
        "[]",
        '{"status":"error","error_message":"missing graph"}',
    ],
)
def test_tool_errors_are_explicit(raw: str) -> None:
    with pytest.raises(GraphToolError):
        parse_similar_code_response(raw)


def test_invalid_neighbor_shape_is_rejected() -> None:
    with pytest.raises(GraphToolError):
        parse_neighbors_response('{"status":"ok","node":"a","neighbors":[1]}')
