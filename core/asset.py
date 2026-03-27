from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass
class Asset:
    asset_id: str
    asset_type: str
    file_uri: str
    format: str
    version: int
    producer_module_id: str
    related_task_id: Optional[str] = None
    created_at: str = field(default_factory=now_iso)
    tags: Dict[str, Any] = field(default_factory=dict)

    # 预留字段：后面接发布和回流
    variant_id: Optional[str] = None
    strategy_id: Optional[str] = None
    lifecycle_status: str = "produced"
    source_tool: Optional[str] = None
    source_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        asset_type: str,
        file_uri: str,
        format: str,
        producer_module_id: str,
        related_task_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        variant_id: Optional[str] = None,
        strategy_id: Optional[str] = None,
    ) -> "Asset":
        return cls(
            asset_id=new_id("asset"),
            asset_type=asset_type,
            file_uri=file_uri,
            format=format,
            version=1,
            producer_module_id=producer_module_id,
            related_task_id=related_task_id,
            tags=tags or {},
            variant_id=variant_id,
            strategy_id=strategy_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
