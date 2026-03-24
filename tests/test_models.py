from models.task import Task, TaskStateHistory
from models.review import ReviewRecord
from models.asset import Asset, AssetVersion, AssetDependency
from models.guard import GuardFailure
from models.recovery import RecoveryRecord


def test_task_creation() -> None:
    task = Task(task_id="task_001", task_type="video_production")
    assert task.task_id == "task_001"
    assert task.current_state == "planning"
    print("Task OK:", task.to_dict())


def test_task_state_history_creation() -> None:
    history = TaskStateHistory(
        task_id="task_001",
        from_state="planning",
        to_state="script_ready",
        trigger="worker",
        reason="script generated"
    )
    assert history.to_state == "script_ready"
    print("TaskStateHistory OK:", history.to_dict())


def test_review_creation() -> None:
    review = ReviewRecord(
        task_id="task_001",
        asset_id="asset_001",
        gate_type="script",
        review_mode="ai",
        review_status="approved",
        score=92.5,
        reason="script quality good",
        suggestions="minor wording polish",
        reviewer="gpt",
        state_before="waiting_review",
        state_after="approved",
        rollback_target=""
    )
    assert review.review_status == "approved"
    print("ReviewRecord OK:", review.to_dict())


def test_asset_creation() -> None:
    asset = Asset(task_id="task_001", asset_type="script")
    version = AssetVersion(
        asset_id=asset.asset_id,
        version=1,
        data={"text": "This is a sample script."},
        created_by="worker_script"
    )
    dependency = AssetDependency(
        asset_id="asset_clip_001",
        depends_on=asset.asset_id,
        relation_type="derived_from"
    )

    assert asset.asset_type == "script"
    assert version.version == 1
    assert dependency.relation_type == "derived_from"

    print("Asset OK:", asset.to_dict())
    print("AssetVersion OK:", version.to_dict())
    print("AssetDependency OK:", dependency.to_dict())


def test_guard_failure_creation() -> None:
    guard = GuardFailure(
        task_id="task_001",
        guard_type="state",
        severity="L3",
        reason="illegal state transition",
        details="executing -> completed without approved",
        action_taken="block"
    )
    assert guard.severity == "L3"
    print("GuardFailure OK:", guard.to_dict())


def test_recovery_record_creation() -> None:
    recovery = RecoveryRecord(
        task_id="task_001",
        from_state="executing",
        to_state="approved",
        reason="worker recoverable failure",
        triggered_by="system"
    )
    assert recovery.to_state == "approved"
    print("RecoveryRecord OK:", recovery.to_dict())


if __name__ == "__main__":
    test_task_creation()
    test_task_state_history_creation()
    test_review_creation()
    test_asset_creation()
    test_guard_failure_creation()
    test_recovery_record_creation()
    print("\nAll model tests passed.")
