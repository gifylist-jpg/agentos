from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class ExecutionStatus:
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class ExecutionRecord:
    execution_id: str
    task_id: str
    module_id: str
    module_version: str
    status: str
    started_at: str
    ended_at: Optional[str] = None
    input_payload_id: Optional[str] = None
    output_payload_id: Optional[str] = None
    duration_ms: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    # 预留字段
    confidence: Optional[float] = None
    data_trust: Optional[str] = None
    failure_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def start(
        cls,
        task_id: str,
        module_id: str,
        module_version: str,
        input_payload_id: Optional[str] = None,
    ) -> "ExecutionRecord":
        return cls(
            execution_id=new_id("exec"),
            task_id=task_id,
            module_id=module_id,
            module_version=module_version,
            status=ExecutionStatus.RUNNING,
            started_at=now_iso(),
            input_payload_id=input_payload_id,
        )

    def finish_success(
        self,
        output_payload_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.status = ExecutionStatus.SUCCESS
        self.ended_at = now_iso()
        self.output_payload_id = output_payload_id
        if metadata:
            self.metadata.update(metadata)

    def finish_failed(self, error_code: str, error_message: str) -> None:
        self.status = ExecutionStatus.FAILED
        self.ended_at = now_iso()
        self.error_code = error_code
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
