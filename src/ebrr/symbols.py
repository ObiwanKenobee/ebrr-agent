"""Deterministic Python symbol indexing and issue-to-symbol grounding."""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from ebrr.models import SymbolRef

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*")
_CAMEL_BOUNDARY_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")

_STOP_WORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "been", "being", "by",
        "for", "from", "has", "have", "if", "in", "into", "is", "it", "its",
        "of", "on", "or", "our", "should", "that", "the", "their", "then",
        "there", "this", "to", "was", "were", "when", "where", "which", "with",
    }
)
_DEFAULT_EXCLUDED_DIRS = frozenset(
    {
        ".git", ".hg", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv",
        "__pycache__", "build", "dist", "node_modules", "site-packages", "venv",
    }
)


def tokenize_identifier(value: str) -> tuple[str, ...]:
    """Split natural-language text and Python identifiers into normalized tokens."""
    separated = _CAMEL_BOUNDARY_RE.sub(" ", value.replace("_", " ").replace("-", " "))
    return tuple(token.lower() for token in _TOKEN_RE.findall(separated))


def _module_name(relative_path: Path) -> str:
    parts = list(relative_path.with_suffix("").parts)
    if parts and parts[0] == "src":
        parts.pop(0)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


@dataclass(frozen=True, slots=True)
class IndexedSymbol:
    """A symbol and the source location from which it was indexed."""

    ref: SymbolRef
    kind: str
    docstring: str | None = None
    is_test: bool = False

    @property
    def qualified_name(self) -> str:
        return self.ref.qualified_name


@dataclass(frozen=True, slots=True)
class SymbolMatch:
    """A candidate symbol ranked against an issue description."""

    symbol: IndexedSymbol
    score: float
    matched_terms: tuple[str, ...]


class _SymbolVisitor(ast.NodeVisitor):
    def __init__(self, path: str, module: str, language: str, is_test: bool) -> None:
        self.path = path
        self.module = module
        self.language = language
        self.is_test = is_test
        self.scope: list[str] = []
        self.symbols: list[IndexedSymbol] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._visit_named_scope(node, "class")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_named_scope(node, "function")

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_named_scope(node, "async_function")

    def _visit_named_scope(self, node: ast.AST, kind: str) -> None:
        name = getattr(node, "name")
        self.scope.append(name)
        qualified_name = ".".join(part for part in (self.module, *self.scope) if part)
        self.symbols.append(
            IndexedSymbol(
                ref=SymbolRef(
                    path=self.path,
                    qualified_name=qualified_name,
                    language=self.language,
                    start_line=getattr(node, "lineno", None),
                    end_line=getattr(node, "end_lineno", None),
                ),
                kind=kind,
                docstring=ast.get_docstring(node),
                is_test=self.is_test,
            )
        )
        self.generic_visit(node)
        self.scope.pop()


class RepositorySymbolIndex:
    """An in-memory index of Python classes and functions under a repository root."""

    def __init__(self, symbols: Iterable[IndexedSymbol]) -> None:
        unique: dict[tuple[str, str, int | None], IndexedSymbol] = {}
        for symbol in symbols:
            key = (symbol.ref.path, symbol.qualified_name, symbol.ref.start_line)
            unique[key] = symbol
        self._symbols = tuple(
            sorted(
                unique.values(),
                key=lambda item: (
                    item.qualified_name.casefold(),
                    item.ref.path,
                    item.ref.start_line or 0,
                ),
            )
        )

    @classmethod
    def from_repository(
        cls,
        root: str | Path,
        *,
        excluded_dirs: Iterable[str] = _DEFAULT_EXCLUDED_DIRS,
        include_tests: bool = True,
    ) -> RepositorySymbolIndex:
        """Parse Python files below root; malformed files are skipped, not fatal."""
        repository_root = Path(root).resolve()
        if not repository_root.is_dir():
            raise NotADirectoryError(repository_root)

        excluded = set(excluded_dirs)
        indexed: list[IndexedSymbol] = []
        for source_path in sorted(repository_root.rglob("*.py")):
            relative = source_path.relative_to(repository_root)
            if any(part in excluded for part in relative.parts):
                continue
            is_test = (
                source_path.name.startswith("test_")
                or source_path.name.endswith("_test.py")
                or "tests" in relative.parts
                or "test" in relative.parts
            )
            if is_test and not include_tests:
                continue
            try:
                source = source_path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(relative))
            except (OSError, UnicodeError, SyntaxError, ValueError):
                continue

            visitor = _SymbolVisitor(
                path=relative.as_posix(),
                module=_module_name(relative),
                language="python",
                is_test=is_test,
            )
            visitor.visit(tree)
            indexed.extend(visitor.symbols)
        return cls(indexed)

    @classmethod
    def from_paths(
        cls,
        paths: Sequence[str | Path],
        *,
        root: str | Path,
        include_tests: bool = True,
    ) -> RepositorySymbolIndex:
        """Build an index from an explicit list of paths (useful for controlled tests)."""
        repository_root = Path(root).resolve()
        indexed: list[IndexedSymbol] = []
        for item in sorted((Path(path) for path in paths), key=lambda path: str(path)):
            source_path = item if item.is_absolute() else repository_root / item
            try:
                relative = source_path.resolve().relative_to(repository_root)
                source = source_path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(relative))
            except (OSError, UnicodeError, SyntaxError, ValueError):
                continue
            is_test = (
                source_path.name.startswith("test_")
                or source_path.name.endswith("_test.py")
                or "tests" in relative.parts
                or "test" in relative.parts
            )
            if is_test and not include_tests:
                continue
            visitor = _SymbolVisitor(
                path=relative.as_posix(),
                module=_module_name(relative),
                language="python",
                is_test=is_test,
            )
            visitor.visit(tree)
            indexed.extend(visitor.symbols)
        return cls(indexed)

    @property
    def symbols(self) -> tuple[IndexedSymbol, ...]:
        return self._symbols

    def rank(
        self, query: str, *, limit: int = 20, include_tests: bool = True
    ) -> tuple[SymbolMatch, ...]:
        """Rank symbols using deterministic token overlap; no model or network call."""
        if limit < 0:
            raise ValueError("limit must be non-negative")
        if limit == 0:
            return ()

        query_terms = frozenset(
            token for token in tokenize_identifier(query) if token not in _STOP_WORDS
        )
        if not query_terms:
            return ()

        matches: list[SymbolMatch] = []
        for symbol in self._symbols:
            if symbol.is_test and not include_tests:
                continue
            candidate_text = " ".join(
                part
                for part in (
                    symbol.qualified_name,
                    symbol.ref.path,
                    symbol.docstring or "",
                )
                if part
            )
            candidate_terms = frozenset(
                token
                for token in tokenize_identifier(candidate_text)
                if token not in _STOP_WORDS
            )
            overlap = tuple(sorted(query_terms & candidate_terms))
            if not overlap:
                continue

            # Coverage is the baseline score. Exact normalized qualified-name matches
            # receive a small deterministic bonus, not an uncalibrated probability.
            score = len(overlap) / len(query_terms)
            normalized_query = " ".join(sorted(query_terms))
            normalized_name = " ".join(sorted(tokenize_identifier(symbol.qualified_name)))
            if normalized_query == normalized_name:
                score += 0.25
            if symbol.is_test:
                score *= 0.85
            matches.append(SymbolMatch(symbol, score, overlap))

        matches.sort(
            key=lambda match: (
                -match.score,
                -len(match.matched_terms),
                match.symbol.qualified_name.casefold(),
                match.symbol.ref.path,
                match.symbol.ref.start_line or 0,
            )
        )
        return tuple(matches[:limit])
