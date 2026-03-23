from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


DB_PATH = Path("runtime/state/agentos.db")


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _to_serializable_dict(obj: Any) -> Dict[str, Any]:
    if is_dataclass(obj):
        data = asdict(obj)
    elif isinstance(obj, dict):
        data = obj
    else:
        raise TypeError(f"Unsupported object type for serialization: {type(obj)}")

    result: Dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(v, datetime):
            result[k] = v.isoformat()
        elif isinstance(v, (dict, list, tuple)):
            result[k] = json.dumps(v, ensure_ascii=False, default=_json_default)
        else:
            result[k] = v
    return result


class DatabaseManager:
    def __init__(self, db_path: Path | str = DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self) -> None:
        self.conn.close()

    def initialize(self) -> None:
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            task_type TEXT NOT NULL,
            workflow_type TEXT NOT NULL,
            current_state TEXT NOT NULL,
            current_substate TEXT NOT NULL,
            status TEXT NOT NULL,
            priority INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            context TEXT NOT NULL,
            assigned_worker TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_state_history (
            record_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            from_state TEXT NOT NULL,
            to_state TEXT NOT NULL,
            trigger TEXT NOT NULL,
            reason TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            asset_id TEXT NOT NULL,
            gate_type TEXT NOT NULL,
            review_mode TEXT NOT NULL,
            review_status TEXT NOT NULL,
            score REAL NOT NULL,
            reason TEXT NOT NULL,
            suggestions TEXT NOT NULL,
            reviewer TEXT NOT NULL,
            state_before TEXT NOT NULL,
            state_after TEXT NOT NULL,
            rollback_target TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            asset_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            current_version INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS asset_versions (
            version_id TEXT PRIMARY KEY,
            asset_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            data TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS asset_dependencies (
            dependency_id TEXT PRIMARY KEY,
            asset_id TEXT NOT NULL,
            depends_on TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS guard_failures (
            guard_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            guard_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            reason TEXT NOT NULL,
            details TEXT NOT NULL,
            action_taken TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recovery_records (
            recovery_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            from_state TEXT NOT NULL,
            to_state TEXT NOT NULL,
            reason TEXT NOT NULL,
            triggered_by TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        self.conn.commit()

    def insert(self, table: str, record: Dict[str, Any]) -> None:
        keys = list(record.keys())
        placeholders = ", ".join(["?"] * len(keys))
        columns = ", ".join(keys)
        values = [record[k] for k in keys]

        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.conn.execute(sql, values)
        self.conn.commit()

    def upsert_task(self, record: Dict[str, Any]) -> None:
        self.conn.execute("""
        INSERT INTO tasks (
            task_id, task_type, workflow_type, current_state, current_substate,
            status, priority, created_at, updated_at, context, assigned_worker
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(task_id) DO UPDATE SET
            task_type=excluded.task_type,
            workflow_type=excluded.workflow_type,
            current_state=excluded.current_state,
            current_substate=excluded.current_substate,
            status=excluded.status,
            priority=excluded.priority,
            created_at=excluded.created_at,
            updated_at=excluded.updated_at,
            context=excluded.context,
            assigned_worker=excluded.assigned_worker
        """, (
            record["task_id"],
            record["task_type"],
            record["workflow_type"],
            record["current_state"],
            record["current_substate"],
            record["status"],
            record["priority"],
            record["created_at"],
            record["updated_at"],
            record["context"],
            record["assigned_worker"],
        ))
        self.conn.commit()

    def fetch_one(self, sql: str, params: Iterable[Any] = ()) -> Optional[sqlite3.Row]:
        cursor = self.conn.execute(sql, tuple(params))
        return cursor.fetchone()

    def fetch_all(self, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        cursor = self.conn.execute(sql, tuple(params))
        return cursor.fetchall()

    def save_task(self, task: Any) -> None:
        self.upsert_task(_to_serializable_dict(task))

    def save_task_state_history(self, history: Any) -> None:
        self.insert("task_state_history", _to_serializable_dict(history))

    def save_review(self, review: Any) -> None:
        self.insert("reviews", _to_serializable_dict(review))

    def save_asset(self, asset: Any) -> None:
        self.insert("assets", _to_serializable_dict(asset))

    def save_asset_version(self, version: Any) -> None:
        self.insert("asset_versions", _to_serializable_dict(version))

    def save_asset_dependency(self, dependency: Any) -> None:
        self.insert("asset_dependencies", _to_serializable_dict(dependency))

    def save_guard_failure(self, guard_failure: Any) -> None:
        self.insert("guard_failures", _to_serializable_dict(guard_failure))

    def save_recovery_record(self, recovery: Any) -> None:
        self.insert("recovery_records", _to_serializable_dict(recovery))

    def save_audit_log(
        self,
        log_id: str,
        task_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        created_at: str,
    ) -> None:
        self.insert("audit_logs", {
            "log_id": log_id,
            "task_id": task_id,
            "event_type": event_type,
            "event_data": json.dumps(event_data, ensure_ascii=False, default=_json_default),
            "created_at": created_at,
        })
