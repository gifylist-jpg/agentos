from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict


@dataclass
class PerformanceSnapshot:
    snapshot_id: str
    publish_id: str
    captured_at: datetime
    age_hours: int

    impressions: int
    clicks: int
    ctr: float
    cvr: float
    watch_time: float
    completion_rate: float
    orders: int

    traffic_split: Dict = field(default_factory=dict)
    source_metadata: Dict = field(default_factory=dict)
