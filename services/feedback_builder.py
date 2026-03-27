from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.publish_record import PublishRecord
from core.performance_snapshot import PerformanceSnapshot


@dataclass
class PerformanceAggregate:
    aggregate_id: str
    task_id: str
    variant_id: str
    publish_id: str

    stage: str
    age_hours: int

    metrics: Dict
    publish_context: Dict

    source_snapshot_ids: List[str] = field(default_factory=list)
    aggregate_metadata: Dict = field(default_factory=dict)


@dataclass
class BaselineReference:
    baseline_scope: str
    product_id: Optional[str] = None
    account_id: Optional[str] = None

    organic_baseline: Dict = field(default_factory=dict)
    ads_baseline: Dict = field(default_factory=dict)

    baseline_version: str = "v1"
    metadata: Dict = field(default_factory=dict)


@dataclass
class FeedbackBundle:
    publish_record: PublishRecord
    snapshots: List[PerformanceSnapshot]
    aggregate: PerformanceAggregate
    baseline: BaselineReference


class FeedbackBuilder:
    def build_feedback_bundle(
        self,
        publish_record: PublishRecord,
        snapshots: List[PerformanceSnapshot],
        baseline: BaselineReference,
    ) -> FeedbackBundle:
        if not snapshots:
            raise ValueError("snapshots must not be empty")

        latest = snapshots[-1]
        stage = self._derive_stage(latest.age_hours)

        aggregate = PerformanceAggregate(
            aggregate_id=f"agg_{publish_record.publish_id}",
            task_id=publish_record.task_id,
            variant_id=publish_record.variant_id,
            publish_id=publish_record.publish_id,
            stage=stage,
            age_hours=latest.age_hours,
            metrics={
                "impressions": latest.impressions,
                "clicks": latest.clicks,
                "ctr": latest.ctr,
                "cvr": latest.cvr,
                "watch_time": latest.watch_time,
                "completion_rate": latest.completion_rate,
                "orders": latest.orders,
            },
            publish_context={
                "publish_mode": publish_record.publish_mode,
                "account_id": publish_record.account_id,
                "product_id": publish_record.product_id,
                "traffic_mix": latest.traffic_split,
            },
            source_snapshot_ids=[s.snapshot_id for s in snapshots],
            aggregate_metadata={
                "snapshot_count": len(snapshots),
            },
        )

        return FeedbackBundle(
            publish_record=publish_record,
            snapshots=snapshots,
            aggregate=aggregate,
            baseline=baseline,
        )

    def _derive_stage(self, age_hours: int) -> str:
        if age_hours < 24:
            return "early"
        if age_hours < 72:
            return "mid"
        return "late"
