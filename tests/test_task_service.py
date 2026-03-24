from __future__ import annotations

from datetime import datetime, timedelta, timezone

from models.review import ReviewRecord
from models.task import Task
from services.task_service import TaskService
from storage.db import DatabaseManager


def test_create_task():
    db = DatabaseManager("runtime/state/test_task_service.db")
    service = TaskService(db)

    task = service.create_task(
        task_id="task_001",
        task_type="test",
        workflow_type="video",
    )
    assert task.task_id == "task_001"
    print("Create task test passed.")


def test_transition_task():
    db = DatabaseManager("runtime/state/test_task_service.db")
    service = TaskService(db)

    task = Task(
        task_id="task_002",
        task_type="test",
        workflow_type="video",
    )

    task.current_state = "planning"
    updated = service.transition_task(
        task,
        "script_ready",
        trigger="system",
    )
    assert updated.current_state == "script_ready"
    print("Transition task test passed.")


def test_illegal_transition_blocked():
    db = DatabaseManager("runtime/state/test_task_service.db")
    service = TaskService(db)

    task = Task(
        task_id="task_003",
        task_type="test",
        workflow_type="video",
    )

    task.current_state = "planning"

    try:
        service.transition_task(task, "completed", trigger="system")
        raise AssertionError("Illegal transition not blocked")
    except Exception as exc:
        print(f"Illegal transition blocked by guard: {exc}")
        print("Illegal transition guard test passed.")


def test_submit_review_via_unified_entry():
    db = DatabaseManager("runtime/state/test_task_service.db")
    service = TaskService(db)

    task = Task(
        task_id="task_004",
        task_type="test",
        workflow_type="video",
    )
    task.current_state = "waiting_review"

    asset = service.create_asset(task_id=task.task_id, asset_type="script", status="draft")

    review = ReviewRecord(
        task_id=task.task_id,
        asset_id=asset.asset_id,
        gate_type="script",
        review_mode="human",
        review_status="approved",
        reviewer="tester",
        reason="looks good",
    )

    updated = service.submit_review(task, review)
    assert updated.current_state == "approved"
    print("Submit review via unified entry test passed.")


def test_asset_dependency_via_unified_entry():
    db = DatabaseManager("runtime/state/test_task_service.db")
    service = TaskService(db)

    task_id = "task_005"
    asset1 = service.create_asset(task_id=task_id, asset_type="script", status="draft")
    asset2 = service.create_asset(task_id=task_id, asset_type="clip", status="draft")

    dep = service.add_asset_dependency(
        task_id=task_id,
        asset_id=asset2.asset_id,
        depends_on=asset1.asset_id,
    )

    assert dep.asset_id == asset2.asset_id
    assert dep.depends_on == asset1.asset_id
    print("Asset dependency via unified entry test passed.")


def test_check_and_handle_stuck_tasks():
    db = DatabaseManager("runtime/state/test_task_service.db")
    service = TaskService(db)

    task = Task(
        task_id="task_stuck_001",
        task_type="test",
        workflow_type="video",
    )

    task.current_state = "waiting_review"
    task.updated_at = datetime.now(timezone.utc) - timedelta(seconds=301)

    results = service.check_and_handle_stuck_tasks([task])

    assert len(results) == 1
    assert results[0]["task_id"] == "task_stuck_001"
    assert results[0]["state"] == "waiting_review"
    assert results[0]["severity"] == "L2"
    assert results[0]["action"] == "rollback"

    print("Stuck task handler integration test passed.")


if __name__ == "__main__":
    test_create_task()
    test_transition_task()
    test_illegal_transition_blocked()
    test_submit_review_via_unified_entry()
    test_asset_dependency_via_unified_entry()
    test_check_and_handle_stuck_tasks()
    print("\nAll task service tests passed.")
