"""Explicit resource accounting for bounded repository exploration."""

from __future__ import annotations

from dataclasses import dataclass


class BudgetExceeded(RuntimeError):
    """Raised when an action would exceed a configured resource limit."""


@dataclass(frozen=True, slots=True)
class ResourceBudget:
    """Maximum resources available to one agent run."""

    max_tokens: int
    max_tool_calls: int
    max_graph_expansions: int
    max_verification_actions: int

    def __post_init__(self) -> None:
        for name in (
            "max_tokens",
            "max_tool_calls",
            "max_graph_expansions",
            "max_verification_actions",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")


@dataclass(frozen=True, slots=True)
class BudgetUsage:
    tokens: int = 0
    tool_calls: int = 0
    graph_expansions: int = 0
    verification_actions: int = 0


class BudgetLedger:
    """Mutable per-run ledger with fail-closed reservation methods."""

    def __init__(self, budget: ResourceBudget) -> None:
        self._budget = budget
        self._usage = BudgetUsage()

    @property
    def budget(self) -> ResourceBudget:
        return self._budget

    @property
    def usage(self) -> BudgetUsage:
        return self._usage

    def remaining(self) -> BudgetUsage:
        """Return remaining capacity for each tracked resource."""
        return BudgetUsage(
            tokens=self._budget.max_tokens - self._usage.tokens,
            tool_calls=self._budget.max_tool_calls - self._usage.tool_calls,
            graph_expansions=(
                self._budget.max_graph_expansions - self._usage.graph_expansions
            ),
            verification_actions=(
                self._budget.max_verification_actions - self._usage.verification_actions
            ),
        )

    def consume_tokens(self, amount: int) -> None:
        self._consume("tokens", amount, self._budget.max_tokens)

    def consume_tool_call(self, amount: int = 1) -> None:
        self._consume("tool_calls", amount, self._budget.max_tool_calls)

    def consume_graph_expansion(self, amount: int = 1) -> None:
        self._consume("graph_expansions", amount, self._budget.max_graph_expansions)

    def consume_verification_action(self, amount: int = 1) -> None:
        self._consume(
            "verification_actions", amount, self._budget.max_verification_actions
        )

    def _consume(self, resource: str, amount: int, limit: int) -> None:
        if amount < 0:
            raise ValueError("consumption amount must be non-negative")
        current = getattr(self._usage, resource)
        requested = current + amount
        if requested > limit:
            raise BudgetExceeded(
                f"{resource} budget exceeded: requested total {requested}, limit {limit}"
            )
        values = {
            "tokens": self._usage.tokens,
            "tool_calls": self._usage.tool_calls,
            "graph_expansions": self._usage.graph_expansions,
            "verification_actions": self._usage.verification_actions,
        }
        values[resource] = requested
        self._usage = BudgetUsage(**values)
