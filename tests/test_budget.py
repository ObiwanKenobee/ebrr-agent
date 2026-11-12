import pytest

from ebrr.budget import BudgetExceeded, BudgetLedger, ResourceBudget


def make_ledger() -> BudgetLedger:
    return BudgetLedger(
        ResourceBudget(
            max_tokens=100,
            max_tool_calls=3,
            max_graph_expansions=2,
            max_verification_actions=1,
        )
    )


def test_usage_and_remaining_are_tracked_independently() -> None:
    ledger = make_ledger()
    ledger.consume_tokens(25)
    ledger.consume_tool_call()
    ledger.consume_graph_expansion(2)
    ledger.consume_verification_action()

    assert ledger.usage.tokens == 25
    assert ledger.usage.tool_calls == 1
    assert ledger.remaining().tokens == 75
    assert ledger.remaining().graph_expansions == 0
    assert ledger.remaining().verification_actions == 0


def test_budget_excess_is_rejected_without_mutating_usage() -> None:
    ledger = make_ledger()
    ledger.consume_tool_call(3)

    with pytest.raises(BudgetExceeded):
        ledger.consume_tool_call()

    assert ledger.usage.tool_calls == 3


def test_negative_consumption_is_rejected() -> None:
    ledger = make_ledger()
    with pytest.raises(ValueError):
        ledger.consume_tokens(-1)


def test_negative_capacity_is_rejected() -> None:
    with pytest.raises(ValueError):
        ResourceBudget(-1, 0, 0, 0)
