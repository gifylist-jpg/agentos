from pathlib import Path

from core.guard_exceptions import GuardValidationError
from models.review import ReviewRecord
from services.task_service import TaskService
from storage.db import DatabaseManager


TEST_DB_PATH = Path("runtime/state/test_task_service.db")


def setup_db() -> DatabaseManager:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    db = DatabaseManager(TEST_DB_PATH)
    db.initialize()
    return db


def test_create_task() -> None:
    db = setup_db()
    task_service = TaskService(db)

    task = task_service.create_task(
        task_id="task_service_001",
        task_type="video_production",
        priority=5,
        context={"topic": "pink bag"},
        assigned_worker="planner_01",
    )

    row = task_service.get_task(task.task_id)
    assert row is not None
    assert row["task_id"] == "task_service_001"
    assert row["priority"] == 5

    print("Create task test passed.")
    db.close()


def test_transition_task() -> None:
    db = setup_db()
    task_service = TaskService(db)

    task = task_service.create_task(
        task_id="task_service_002",
        task_type="video_production",
    )

    task_service.transition_task(
        task=task,
        new_state="script_ready",
        trigger="worker",
        reason="script generated",
    )
    assert task.current_state == "script_ready"

    task_service.transition_task(
        task=task,
        new_state="waiting_review",
        trigger="system",
        reason="submitted for review",
        new_substate="waiting_script_review",
    )
    assert task.current_state == "waiting_review"
    assert task.current_substate == "waiting_script_review"

    print("Transition task test passed.")
    db.close()


def test_illegal_transition_blocked_by_guard() -> None:
    db = setup_db()
    task_service = TaskService(db)

    task = task_service.create_task(
        task_id="task_service_003",
        task_type="video_production",
    )

    try:
        task_service.transition_task(
            task=task,
            new_state="completed",
            trigger="worker",
            reason="skip all states",
        )
    except GuardValidationError as exc:
        print("Illegal transition blocked by guard:", exc)
    else:
        raise AssertionError("Illegal transition was not blocked")

    rows = db.fetch_all(
        "SELECT * FROM guard_failures WHERE task_id = ?",
        (task.task_id,),
    )
    assert len(rows) == 1

    print("Illegal transition guard test passed.")
    db.close()


def test_submit_review_via_unified_entry() -> None:
    db = setup_db()
    task_service = TaskService(db)

    task = task_service.create_task(
        task_id="task_service_004",
        task_type="video_production",
    )

    task_service.transition_task(
        task=task,
        new_state="script_ready",
        trigger="worker",
        reason="script generated",
    )
    task_service.transition_task(
        task=task,
        new_state="waiting_review",
        trigger="system",
        reason="submitted for script review",
        new_substate="waiting_script_review",
    )

    script_asset = task_service.create_asset(
        task_id=task.task_id,
        asset_type="script",
        status="draft",
    )
    task_service.create_asset_version(
        asset_id=script_asset.asset_id,
        version=1,
        data={"text": "sample script"},
        created_by="worker_script",
    )

    review = ReviewRecord(
        task_id=task.task_id,
        asset_id=script_asset.asset_id,
        gate_type="script",
        review_mode="ai",
        review_status="approved",
        score=91.0,
        reason="script passed",
        suggestions="",
        reviewer="gpt",
        state_before="waiting_review",
        state_after="approved",
        rollback_target="",
    )

    task_service.submit_review(task, review)
    assert task.current_state == "approved"

    rows = db.fetch_all(
        "SELECT * FROM reviews WHERE task_id = ?",
        (task.task_id,),
    )
    assert len(rows) == 1

    print("Submit review via unified entry test passed.")
    db.close()


def test_asset_dependency_via_unified_entry() -> None:
    db = setup_db()
    task_service = TaskService(db)

    task = task_service.create_task(
        task_id="task_service_005",
        task_type="video_production",
    )

    script_asset = task_service.create_asset(
        task_id=task.task_id,
        asset_type="script",
        status="approved",
    )
    clip_asset = task_service.create_asset(
        task_id=task.task_id,
        asset_type="clip",
        status="draft",
    )

    dependency = task_service.add_asset_dependency(
        task_id=task.task_id,
        asset_id=clip_asset.asset_id,
        depends_on=script_asset.asset_id,
        relation_type="derived_from",
    )
    assert dependency.relation_type == "derived_from"

    rows = db.fetch_all(
        "SELECT * FROM asset_dependencies WHERE asset_id = ?",
        (clip_asset.asset_id,),
    )
    assert len(rows) == 1

    print("Asset dependency via unified entry test passed.")
    db.close()


if __name__ == "__main__":
    test_create_task()
    test_transition_task()
    test_illegal_transition_blocked_by_guard()
    test_submit_review_via_unified_entry()
    test_asset_dependency_via_unified_entry()
    print("\nAll task service tests passed.")
