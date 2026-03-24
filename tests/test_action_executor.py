from __future__ import annotations

from services.action_executor import ActionExecutor


def test_retry_action_interpretation() -> None:
    executor = ActionExecutor()

    result = executor.interpret(
        task_id="task_001",
        action="retry",
        context={"reason": "temporary failure"},
    )

    assert result["task_id"] == "task_001"
    assert result["action"] == "retry"
    assert result["execute"] is False
    assert "Retry is recommended" in result["message"]
    assert result["context"]["reason"] == "temporary failure"


def test_rollback_action_interpretation() -> None:
    executor = ActionExecutor()

    result = executor.interpret(
        task_id="task_002",
        action="rollback",
        context={"from_state": "executing"},
    )

    assert result["task_id"] == "task_002"
    assert result["action"] == "rollback"
    assert result["execute"] is False
    assert "Rollback is recommended" in result["message"]
    assert result["context"]["from_state"] == "executing"


def test_human_intervention_action_interpretation() -> None:
    executor = ActionExecutor()

    result = executor.interpret(
        task_id="task_003",
        action="human_intervention",
        context={"severity": "L3"},
    )

    assert result["task_id"] == "task_003"
    assert result["action"] == "human_intervention"
    assert result["execute"] is False
    assert "Human intervention is required" in result["message"]
    assert result["context"]["severity"] == "L3"


def test_invalid_action_raises_value_error() -> None:
    executor = ActionExecutor()

    try:
        executor.interpret(task_id="task_004", action="invalid_action")
        raise AssertionError("Expected ValueError was not raised")
    except ValueError as exc:
        assert "Invalid action" in str(exc)


if __name__ == "__main__":
    test_retry_action_interpretation()
    test_rollback_action_interpretation()
    test_human_intervention_action_interpretation()
    test_invalid_action_raises_value_error()
    print("\nAll action executor tests passed.")
