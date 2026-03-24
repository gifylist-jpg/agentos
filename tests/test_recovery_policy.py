from __future__ import annotations

from services.recovery_policy import RecoveryPolicy


def test_l1_returns_retry() -> None:
    policy = RecoveryPolicy()
    action = policy.get_action(severity="L1", error_type="tool_error")
    assert action == "retry"


def test_l2_returns_rollback() -> None:
    policy = RecoveryPolicy()
    action = policy.get_action(severity="L2", error_type="guard_error")
    assert action == "rollback"


def test_l3_returns_human_intervention() -> None:
    policy = RecoveryPolicy()
    action = policy.get_action(severity="L3", error_type="system_error")
    assert action == "human_intervention"


def test_invalid_severity_raises_value_error() -> None:
    policy = RecoveryPolicy()

    try:
        policy.get_action(severity="L4", error_type="unknown_error")
        raise AssertionError("Expected ValueError was not raised")
    except ValueError as exc:
        assert "Invalid severity" in str(exc)


if __name__ == "__main__":
    test_l1_returns_retry()
    test_l2_returns_rollback()
    test_l3_returns_human_intervention()
    test_invalid_severity_raises_value_error()
    print("\nAll recovery policy tests passed.")
