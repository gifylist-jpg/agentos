from pathlib import Path

from models.review import ReviewRecord
from models.task import Task
from services.review_service import ReviewService
from services.state_manager import StateManager
from storage.db import DatabaseManager


TEST_DB_PATH = Path("runtime/state/test_review_service.db")


def setup_db() -> DatabaseManager:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    db = DatabaseManager(TEST_DB_PATH)
    db.initialize()
    return db


def move_task_to_waiting_script_review(
    task: Task,
    state_manager: StateManager,
) -> Task:
    state_manager.transition_task(
        task=task,
        new_state="script_ready",
        trigger="worker",
        reason="script generated",
    )
    state_manager.transition_task(
        task=task,
        new_state="waiting_review",
        trigger="system",
        reason="submitted for script review",
        new_substate="waiting_script_review",
    )
    return task


def move_task_to_approved(task: Task, state_manager: StateManager) -> Task:
    state_manager.transition_task(
        task=task,
        new_state="script_ready",
        trigger="worker",
        reason="script generated",
    )
    state_manager.transition_task(
        task=task,
        new_state="waiting_review",
        trigger="system",
        reason="submitted for script review",
        new_substate="waiting_script_review",
    )
    state_manager.transition_task(
        task=task,
        new_state="approved",
        trigger="review",
        reason="script approved",
    )
    return task


def test_script_review_approved() -> None:
    db = setup_db()
    state_manager = StateManager(db)
    review_service = ReviewService(db, state_manager)

    task = Task(task_id="task_review_001", task_type="video_production")
    db.save_task(task)
    move_task_to_waiting_script_review(task, state_manager)

    review = ReviewRecord(
        task_id=task.task_id,
        asset_id="asset_script_001",
        gate_type="script",
        review_mode="ai",
        review_status="approved",
        score=93.0,
        reason="script is good",
        suggestions="",
        reviewer="gpt",
        state_before="waiting_review",
        state_after="approved",
        rollback_target="",
    )

    review_service.submit_review(task, review)
    assert task.current_state == "approved"

    review_rows = db.fetch_all("SELECT * FROM reviews WHERE task_id = ?", (task.task_id,))
    assert len(review_rows) == 1

    print("Script approved test passed.")
    db.close()


def test_script_review_rejected() -> None:
    db = setup_db()
    state_manager = StateManager(db)
    review_service = ReviewService(db, state_manager)

    task = Task(task_id="task_review_002", task_type="video_production")
    db.save_task(task)
    move_task_to_waiting_script_review(task, state_manager)

    review = ReviewRecord(
        task_id=task.task_id,
        asset_id="asset_script_002",
        gate_type="script",
        review_mode="human",
        review_status="rejected",
        score=45.0,
        reason="script weak structure",
        suggestions="rewrite opening hook",
        reviewer="human_reviewer",
        state_before="waiting_review",
        state_after="planning",
        rollback_target="planning",
    )

    review_service.submit_review(task, review)
    assert task.current_state == "planning"

    recovery_rows = db.fetch_all(
        "SELECT * FROM recovery_records WHERE task_id = ?",
        (task.task_id,),
    )
    assert len(recovery_rows) == 1

    print("Script rejected rollback test passed.")
    db.close()


def test_final_review_approved() -> None:
    db = setup_db()
    state_manager = StateManager(db)
    review_service = ReviewService(db, state_manager)

    task = Task(task_id="task_review_003", task_type="video_production")
    db.save_task(task)
    move_task_to_approved(task, state_manager)

    state_manager.transition_task(
        task=task,
        new_state="executing",
        trigger="system",
        reason="start final execution",
    )

    review = ReviewRecord(
        task_id=task.task_id,
        asset_id="asset_final_001",
        gate_type="final",
        review_mode="hybrid",
        review_status="approved",
        score=98.0,
        reason="final video passed",
        suggestions="",
        reviewer="hybrid_pipeline",
        state_before="executing",
        state_after="completed",
        rollback_target="",
    )

    review_service.submit_review(task, review)
    assert task.current_state == "completed"

    print("Final approved test passed.")
    db.close()


def test_final_review_rejected() -> None:
    db = setup_db()
    state_manager = StateManager(db)
    review_service = ReviewService(db, state_manager)

    task = Task(task_id="task_review_004", task_type="video_production")
    db.save_task(task)
    move_task_to_approved(task, state_manager)

    state_manager.transition_task(
        task=task,
        new_state="executing",
        trigger="system",
        reason="start final execution",
    )

    review = ReviewRecord(
        task_id=task.task_id,
        asset_id="asset_final_002",
        gate_type="final",
        review_mode="human",
        review_status="rejected",
        score=52.0,
        reason="final cut pacing poor",
        suggestions="re-edit middle section",
        reviewer="editor_01",
        state_before="executing",
        state_after="approved",
        rollback_target="approved",
    )

    review_service.submit_review(task, review)
    assert task.current_state == "approved"

    recovery_rows = db.fetch_all(
        "SELECT * FROM recovery_records WHERE task_id = ?",
        (task.task_id,),
    )
    assert len(recovery_rows) == 1

    print("Final rejected rollback test passed.")
    db.close()


if __name__ == "__main__":
    test_script_review_approved()
    test_script_review_rejected()
    test_final_review_approved()
    test_final_review_rejected()
    print("\nAll review service tests passed.")
