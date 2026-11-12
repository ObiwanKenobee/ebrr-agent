from pathlib import Path

from ebrr.symbols import RepositorySymbolIndex, tokenize_identifier


def test_tokenizer_splits_snake_case_and_camel_case() -> None:
    assert tokenize_identifier("HTTPConnection.get_response") == (
        "http", "connection", "get", "response"
    )


def test_index_builds_qualified_symbols_and_line_ranges(tmp_path: Path) -> None:
    package = tmp_path / "src" / "sample"
    package.mkdir(parents=True)
    (package / "client.py").write_text(
        'class HTTPConnection:\n'
        '    """Manage HTTP connections."""\n'
        '    def get_response(self, status_code):\n'
        '        return status_code\n',
        encoding="utf-8",
    )

    index = RepositorySymbolIndex.from_repository(tmp_path)

    assert [symbol.qualified_name for symbol in index.symbols] == [
        "sample.client.HTTPConnection",
        "sample.client.HTTPConnection.get_response",
    ]
    method = index.symbols[1]
    assert method.ref.path == "src/sample/client.py"
    assert method.ref.start_line == 3
    assert method.ref.end_line == 4


def test_rank_finds_http_connection_method_deterministically(tmp_path: Path) -> None:
    (tmp_path / "client.py").write_text(
        "class HTTPConnection:\n"
        "    def get_response(self):\n"
        "        pass\n"
        "\n"
        "def parse_cookie(value):\n"
        "    pass\n",
        encoding="utf-8",
    )
    index = RepositorySymbolIndex.from_repository(tmp_path)

    first = index.rank("HTTP connection response failed", limit=10)
    second = index.rank("HTTP connection response failed", limit=10)

    assert first == second
    assert first[0].symbol.qualified_name == "client.HTTPConnection.get_response"
    assert first[0].matched_terms == ("connection", "http", "response")


def test_index_skips_syntax_errors_and_excluded_directories(tmp_path: Path) -> None:
    (tmp_path / "valid.py").write_text("def useful_function():\n    pass\n", encoding="utf-8")
    (tmp_path / "broken.py").write_text("def unfinished(:\n", encoding="utf-8")
    cache = tmp_path / ".venv"
    cache.mkdir()
    (cache / "noise.py").write_text("def unrelated():\n    pass\n", encoding="utf-8")

    index = RepositorySymbolIndex.from_repository(tmp_path)

    assert [symbol.qualified_name for symbol in index.symbols] == ["valid.useful_function"]


def test_tests_can_be_excluded_or_retained(tmp_path: Path) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_api.py").write_text("def test_timeout():\n    pass\n", encoding="utf-8")

    included = RepositorySymbolIndex.from_repository(tmp_path)
    excluded = RepositorySymbolIndex.from_repository(tmp_path, include_tests=False)

    assert len(included.symbols) == 1
    assert included.symbols[0].is_test is True
    assert excluded.symbols == ()


def test_empty_or_stopword_only_query_returns_no_matches(tmp_path: Path) -> None:
    (tmp_path / "api.py").write_text("def get_response():\n    pass\n", encoding="utf-8")
    index = RepositorySymbolIndex.from_repository(tmp_path)

    assert index.rank("the and is") == ()
    assert index.rank(" ") == ()
