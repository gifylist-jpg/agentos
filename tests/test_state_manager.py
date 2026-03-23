from pathlib import Path

from core.exceptions import StateTransitionError
from models.task import Task
from services.state_manager import StateManager
from storage.db import DatabaseManager


TEST_DB_PATH = Path("runtime/state/test_state_manager.db")


def setup_db() -> DatabaseManager:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    db = DatabaseManager(TEST_DB_PATH)
    db.initialize()
    return db


def test_valid_transitions() -> None:
    db = setup_db()
    manager = StateManager(db)

    task = Task(task_id="task_state_001", task_type="video_production")
    db.save_task(task)

    manager.transition_task(
        task,
        new_state="script_ready",
        trigger="worker",
        reason="script generated",
    )
    assert task.current_state == "script_ready"

    manager.transition_task(
        task,
        new_state="waiting_review",
        trigger="system",
        reason="submitted for review",
        new_substate="waiting_script_review",
    )
    assert task.current_state == "waiting_review"
    assert task.current_substate == "waiting_script_review"

    manager.transition_task(
        task,
        new_state="approved",
        trigger="review",
        reason="script approved",
    )
    assert task.current_state == "approved"

    manager.transition_task(
        task,
        new_state="executing",
        trigger="system",
        reason="execution started",
    )
    assert task.current_state == "executing"

    manager.transition_task(
        task,
        new_state="completed",
        trigger="worker",
        reason="execution done",
    )
    assert task.current_state == "completed"

    rows = db.fetch_all(
        "SELECT * FROM task_state_history WHERE task_id = ? ORDER BY created_at ASC",
        (task.task_id,),
    )
    assert len(rows) == 5

    print("Valid transition test passed.")
    db.close()


def test_illegal_transition_blocked() -> None:
    db = setup_db()
    manager = StateManager(db)

    task = Task(task_id="task_state_002", task_type="video_production")
    db.save_task(task)

    try:
        manager.transition_task(
            task,
            new_state="completed",
            trigger="worker",
            reason="skip all steps",
        )
    except StateTransitionError as exc:
        print("Illegal transition blocked:", exc)
    else:
        raise AssertionError("Illegal transition was not blocked")

    db.close()


def test_rollback() -> None:
    db = setup_db()
    manager = StateManager(db)

    task = Task(task_id="task_state_003", task_type="video_production")
    db.save_task(task)

    manager.transition_task(task, "script_ready", "worker", "script generated")
    manager.transition_task(task, "waiting_review", "system", "submitted for review")
    manager.transition_task(task, "approved", "review", "review approved")
    manager.transition_task(task, "executing", "system", "execution started")

    manager.rollback_task(
        task,
        rollback_to="approved",
        reason="worker recoverable failure",
        triggered_by="system",
    )

    assert task.current_state == "approved"

    recovery_rows = db.fetch_all(
        "SELECT * FROM recovery_records WHERE task_id = ?",
        (task.task_id,),
    )
    assert len(recovery_rows) == 1

    print("Rollback test passed.")
    db.close()


if __name__ == "__main__":
    test_valid_transitions()
    test_illegal_transition_blocked()
    test_rollback()
    print("\nAll state manager tests passed.")
