from pathlib import Path

from models.task import Task, TaskStateHistory
from models.review import ReviewRecord
from models.asset import Asset, AssetVersion, AssetDependency
from models.guard import GuardFailure
from models.recovery import RecoveryRecord
from storage.db import DatabaseManager


TEST_DB_PATH = Path("runtime/state/test_agentos.db")


def main() -> None:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    db = DatabaseManager(TEST_DB_PATH)
    db.initialize()

    task = Task(task_id="task_001", task_type="video_production")
    db.save_task(task)

    history = TaskStateHistory(
        task_id=task.task_id,
        from_state="planning",
        to_state="script_ready",
        trigger="worker",
        reason="script generated"
    )
    db.save_task_state_history(history)

    asset = Asset(task_id=task.task_id, asset_type="script")
    db.save_asset(asset)

    asset_version = AssetVersion(
        asset_id=asset.asset_id,
        version=1,
        data={"text": "sample script"},
        created_by="worker_script"
    )
    db.save_asset_version(asset_version)

    dependency = AssetDependency(
        asset_id="asset_clip_001",
        depends_on=asset.asset_id,
        relation_type="derived_from"
    )
    db.save_asset_dependency(dependency)

    review = ReviewRecord(
        task_id=task.task_id,
        asset_id=asset.asset_id,
        gate_type="script",
        review_mode="ai",
        review_status="approved",
        score=95.0,
        reason="good script",
        suggestions="no change",
        reviewer="gpt",
        state_before="waiting_review",
        state_after="approved",
        rollback_target=""
    )
    db.save_review(review)

    guard = GuardFailure(
        task_id=task.task_id,
        guard_type="state",
        severity="L2",
        reason="minor state mismatch",
        details="test details",
        action_taken="rollback"
    )
    db.save_guard_failure(guard)

    recovery = RecoveryRecord(
        task_id=task.task_id,
        from_state="executing",
        to_state="approved",
        reason="recoverable worker failure",
        triggered_by="system"
    )
    db.save_recovery_record(recovery)

    task_row = db.fetch_one("SELECT * FROM tasks WHERE task_id = ?", (task.task_id,))
    review_row = db.fetch_one("SELECT * FROM reviews WHERE review_id = ?", (review.review_id,))
    asset_row = db.fetch_one("SELECT * FROM assets WHERE asset_id = ?", (asset.asset_id,))

    assert task_row is not None
    assert review_row is not None
    assert asset_row is not None

    print("Task saved:", dict(task_row))
    print("Review saved:", dict(review_row))
    print("Asset saved:", dict(asset_row))
    print("\nDatabase test passed.")

    db.close()


if __name__ == "__main__":
    main()
