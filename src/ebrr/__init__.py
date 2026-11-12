"""Evidence-Budgeted Repository Reasoning research scaffold."""

from ebrr.budget import BudgetExceeded, BudgetLedger, ResourceBudget
from ebrr.models import EvidenceKind, EvidenceRecord, EpistemicStatus, IssueSpec, SymbolRef

__all__ = [
    "BudgetExceeded",
    "BudgetLedger",
    "EvidenceKind",
    "EvidenceRecord",
    "EpistemicStatus",
    "IssueSpec",
    "ResourceBudget",
    "SymbolRef",
]

__version__ = "0.1.0"
