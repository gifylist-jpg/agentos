from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Asset:
    task_id: str
    asset_type: str  # script | clip | video | audio
    current_version: int = 1
    status: str = "draft"  # draft | reviewed | approved | rejected | deprecated
    created_at: datetime = field(default_factory=utc_now)
    asset_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class AssetVersion:
    asset_id: str
    version: int
    data: Dict[str, Any] = field(default_factory=dict)
    created_by: str = ""  # worker | tool | user
    created_at: datetime = field(default_factory=utc_now)
    version_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class AssetDependency:
    asset_id: str
    depends_on: str
    relation_type: str  # derived_from | uses | reference
    created_at: datetime = field(default_factory=utc_now)
    dependency_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)
