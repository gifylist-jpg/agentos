from pathlib import Path

from audit.audit_logger import AuditLogger
from storage.db import DatabaseManager


TEST_DB_PATH = Path("runtime/state/test_audit_logger.db")


def setup_db() -> DatabaseManager:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    db = DatabaseManager(TEST_DB_PATH)
    db.initialize()
    return db


def test_log_generic_event() -> None:
    db = setup_db()
    logger = AuditLogger(db)

    log_id = logger.log_event(
        task_id="task_audit_001",
        event_type="custom_event",
        event_data={"message": "hello audit"},
    )
    assert log_id

    rows = db.fetch_all("SELECT * FROM audit_logs WHERE task_id = ?", ("task_audit_001",))
    assert len(rows) == 1

    print("Generic audit event test passed.")
    db.close()


def test_log_state_change() -> None:
    db = setup_db()
    logger = AuditLogger(db)

    logger.log_state_change(
        task_id="task_audit_002",
        from_state="planning",
        to_state="script_ready",
        trigger="worker",
        reason="script generated",
    )

    rows = db.fetch_all("SELECT * FROM audit_logs WHERE task_id = ?", ("task_audit_002",))
    assert len(rows) == 1
    assert rows[0]["event_type"] == "state_change"

    print("State change audit test passed.")
    db.close()


def test_log_review_event() -> None:
    db = setup_db()
    logger = AuditLogger(db)

    logger.log_review_event(
        task_id="task_audit_003",
        review_id="review_001",
        gate_type="script",
        review_status="approved",
        reviewer="gpt",
    )

    rows = db.fetch_all("SELECT * FROM audit_logs WHERE task_id = ?", ("task_audit_003",))
    assert len(rows) == 1
    assert rows[0]["event_type"] == "review"

    print("Review audit test passed.")
    db.close()


def test_log_guard_failure() -> None:
    db = setup_db()
    logger = AuditLogger(db)

    logger.log_guard_failure(
        task_id="task_audit_004",
        guard_type="state",
        severity="L3",
        reason="illegal state transition",
        action_taken="block",
    )

    rows = db.fetch_all("SELECT * FROM audit_logs WHERE task_id = ?", ("task_audit_004",))
    assert len(rows) == 1
    assert rows[0]["event_type"] == "guard_failure"

    print("Guard failure audit test passed.")
    db.close()


def test_log_recovery() -> None:
    db = setup_db()
    logger = AuditLogger(db)

    logger.log_recovery(
        task_id="task_audit_005",
        from_state="executing",
        to_state="approved",
        triggered_by="system",
        reason="worker recoverable failure",
    )

    rows = db.fetch_all("SELECT * FROM audit_logs WHERE task_id = ?", ("task_audit_005",))
    assert len(rows) == 1
    assert rows[0]["event_type"] == "recovery"

    print("Recovery audit test passed.")
    db.close()


if __name__ == "__main__":
    test_log_generic_event()
    test_log_state_change()
    test_log_review_event()
    test_log_guard_failure()
    test_log_recovery()
    print("\nAll audit logger tests passed.")
