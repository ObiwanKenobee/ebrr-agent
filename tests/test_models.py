import pytest

from ebrr.models import (
    EvidenceKind,
    EvidenceRecord,
    EpistemicStatus,
    IssueSpec,
    SymbolRef,
)


def test_issue_spec_requires_title_and_description() -> None:
    with pytest.raises(ValueError):
        IssueSpec(title=" ", description="description")


def test_symbol_ref_validates_line_range() -> None:
    with pytest.raises(ValueError):
        SymbolRef(path="src/app.py", qualified_name="App.run", start_line=12, end_line=8)


def test_evidence_record_keeps_kind_and_epistemic_status_separate() -> None:
    record = EvidenceRecord(
        evidence_id="ev-001",
        claim_id="claim-001",
        kind=EvidenceKind.TEST,
        status=EpistemicStatus.OBSERVED,
        locator="tests/test_api.py::test_timeout",
        rationale="The test fails with the reported timeout exception.",
        content_sha256="a" * 64,
    )

    assert record.kind is EvidenceKind.TEST
    assert record.status is EpistemicStatus.OBSERVED


def test_evidence_record_rejects_invalid_digest() -> None:
    with pytest.raises(ValueError):
        EvidenceRecord(
            evidence_id="ev-001",
            claim_id="claim-001",
            kind=EvidenceKind.SOURCE,
            status=EpistemicStatus.HYPOTHESIS,
            locator="src/api.py:20-30",
            rationale="Candidate function may be involved.",
            content_sha256="not-a-sha256",
        )
