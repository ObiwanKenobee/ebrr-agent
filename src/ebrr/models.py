"""Small, dependency-free domain types for EBRR."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EvidenceKind(StrEnum):
    """Where an evidence item originated."""

    SOURCE = "source"
    GRAPH = "graph"
    TEST = "test"
    DOCUMENTATION = "documentation"
    EXECUTION = "execution"


class EpistemicStatus(StrEnum):
    """How an evidence item relates to a claim."""

    OBSERVED = "observed"
    HYPOTHESIS = "hypothesis"
    CONTRADICTED = "contradicted"


@dataclass(frozen=True, slots=True)
class IssueSpec:
    """Normalized issue description; fields preserve the task's stated intent."""

    title: str
    description: str
    expected_behavior: str | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")


@dataclass(frozen=True, slots=True)
class SymbolRef:
    """Stable locator for a code symbol without embedding its source contents."""

    path: str
    qualified_name: str
    language: str = "python"
    start_line: int | None = None
    end_line: int | None = None

    def __post_init__(self) -> None:
        if not self.path.strip():
            raise ValueError("path must not be empty")
        if not self.qualified_name.strip():
            raise ValueError("qualified_name must not be empty")
        if self.start_line is not None and self.start_line < 1:
            raise ValueError("start_line must be >= 1")
        if self.end_line is not None and self.end_line < 1:
            raise ValueError("end_line must be >= 1")
        if (
            self.start_line is not None
            and self.end_line is not None
            and self.end_line < self.start_line
        ):
            raise ValueError("end_line must be >= start_line")


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """Traceable evidence linked to a claim under investigation.

    `locator` should identify a file/symbol/test/execution record. Store hashes or
    short excerpts only when necessary; avoid copying large third-party source files.
    """

    evidence_id: str
    claim_id: str
    kind: EvidenceKind
    status: EpistemicStatus
    locator: str
    rationale: str
    content_sha256: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("evidence_id", "claim_id", "locator", "rationale"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")
        if self.content_sha256 is not None:
            digest = self.content_sha256.lower()
            if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                raise ValueError("content_sha256 must be a 64-character hexadecimal SHA-256 digest")
