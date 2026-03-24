from pathlib import Path

from core.guard_exceptions import GuardValidationError
from guards.guard_manager import GuardManager
from models.asset import Asset
from models.review import ReviewRecord
from models.task import Task
from storage.db import DatabaseManager


TEST_DB_PATH = Path("runtime/state/test_guard_manager.db")


def setup_db() -> DatabaseManager:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    db = DatabaseManager(TEST_DB_PATH)
    db.initialize()
    return db


def test_valid_review_contract() -> None:
    db = setup_db()
    guard = GuardManager(db)

    task = Task(task_id="task_guard_001", task_type="video_production")
    db.save_task(task)

    review = ReviewRecord(
        task_id=task.task_id,
        asset_id="asset_001",
        gate_type="script",
        review_mode="ai",
        review_status="approved",
        reason="ok",
    )

    guard.validate_review_contract(task, review)
    print("Valid review contract test passed.")
    db.close()


def test_invalid_review_contract_blocked() -> None:
    db = setup_db()
    guard = GuardManager(db)

    task = Task(task_id="task_guard_002", task_type="video_production")
    db.save_task(task)

    review = ReviewRecord(
        task_id=task.task_id,
        asset_id="asset_002",
        gate_type="bad_gate",
        review_mode="ai",
        review_status="approved",
        reason="invalid gate test",
    )

    try:
        guard.validate_review_contract(task, review)
    except GuardValidationError as exc:
        print("Invalid review contract blocked:", exc)
    else:
        raise AssertionError("Invalid review contract was not blocked")

    rows = db.fetch_all(
        "SELECT * FROM guard_failures WHERE task_id = ?",
        (task.task_id,),
    )
    assert len(rows) == 1
    db.close()


def test_invalid_state_transition_blocked() -> None:
    db = setup_db()
    guard = GuardManager(db)

    task = Task(task_id="task_guard_003", task_type="video_production")
    db.save_task(task)

    try:
        guard.validate_state_transition(
            task=task,
            from_state="planning",
            to_state="completed",
            allowed=False,
        )
    except GuardValidationError as exc:
        print("Invalid state transition blocked:", exc)
    else:
        raise AssertionError("Invalid state transition was not blocked")

    rows = db.fetch_all(
        "SELECT * FROM guard_failures WHERE task_id = ?",
        (task.task_id,),
    )
    assert len(rows) == 1
    db.close()


def test_asset_exists_validation() -> None:
    db = setup_db()
    guard = GuardManager(db)

    task = Task(task_id="task_guard_004", task_type="video_production")
    db.save_task(task)

    asset = Asset(task_id=task.task_id, asset_type="script")
    db.save_asset(asset)

    guard.validate_asset_exists(task.task_id, asset.asset_id)
    print("Asset exists validation test passed.")
    db.close()


def test_missing_asset_blocked() -> None:
    db = setup_db()
    guard = GuardManager(db)

    task = Task(task_id="task_guard_005", task_type="video_production")
    db.save_task(task)

    try:
        guard.validate_asset_exists(task.task_id, "missing_asset_id")
    except GuardValidationError as exc:
        print("Missing asset blocked:", exc)
    else:
        raise AssertionError("Missing asset was not blocked")

    rows = db.fetch_all(
        "SELECT * FROM guard_failures WHERE task_id = ?",
        (task.task_id,),
    )
    assert len(rows) == 1
    db.close()


if __name__ == "__main__":
    test_valid_review_contract()
    test_invalid_review_contract_blocked()
    test_invalid_state_transition_blocked()
    test_asset_exists_validation()
    test_missing_asset_blocked()
    print("\nAll guard manager tests passed.")
