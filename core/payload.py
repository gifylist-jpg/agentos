from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass
class PayloadWrapper:
    payload_id: str
    schema_name: str
    schema_version: str
    producer: str
    data: Dict[str, Any]
    created_at: str = field(default_factory=now_iso)

    @classmethod
    def create(
        cls,
        schema_name: str,
        schema_version: str,
        producer: str,
        data: Dict[str, Any],
    ) -> "PayloadWrapper":
        return cls(
            payload_id=new_id("payload"),
            schema_name=schema_name,
            schema_version=schema_version,
            producer=producer,
            data=data,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
