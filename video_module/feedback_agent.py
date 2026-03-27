from __future__ import annotations

from typing import Any, Dict, List

from core.performance_snapshot import PerformanceSnapshot, PerformanceAggregate
from core.publish_record import PublishRecord


MODULE_ID = "feedback_agent"
MODULE_VERSION = "0.1.0"


def create_publish_records(task_id: str, product_id: str, assets: List[Dict[str, Any]]) -> List[PublishRecord]:
    records: List[PublishRecord] = []

    for asset in assets:
        record = PublishRecord.create(
            asset_id=asset["asset_id"],
            variant_id=asset.get("variant_id"),
            task_id=task_id,
            product_id=product_id,
            account_id="demo_account_001",
            publish_mode="organic",
            platform="tiktok",
        )
        records.append(record)

    return records


def collect_performance_snapshots(publish_records: List[PublishRecord]) -> List[PerformanceSnapshot]:
    """
    最小自动回流版：
    不接真实平台，直接生成可复用的结构化 snapshot
    后面接 TikTok 抓取时，只替换这个函数内部即可。
    """
    snapshots: List[PerformanceSnapshot] = []

    for idx, record in enumerate(publish_records, start=1):
        # 简单做一点差异，模拟不同视频表现
        views = 800 + idx * 250
        clicks = 20 + idx * 8
        orders = 0 if idx == 2 else 1
        ctr = round(clicks / views, 4)
        cvr = round(orders / clicks, 4) if clicks > 0 else 0.0

        metrics = {
            "views": views,
            "clicks": clicks,
            "ctr": ctr,
            "cvr": cvr,
            "orders": orders,
            "likes": 30 + idx * 10,
            "comments": 2 + idx,
            "shares": idx,
            "watch_rate": round(0.14 + idx * 0.03, 4),
            "avg_watch_time": round(4.5 + idx * 0.8, 2),
            "gmv": float(orders * 29.99),
            "spend": 0.0,
            "roas": None,
        }

        snapshot = PerformanceSnapshot.create(
            publish_id=record.publish_id,
            asset_id=record.asset_id,
            metrics=metrics,
            source=f"{MODULE_ID}:{MODULE_VERSION}",
            video_stage="early_stage",
        )
        snapshots.append(snapshot)

    return snapshots


def build_aggregates(
    publish_records: List[PublishRecord],
    snapshots: List[PerformanceSnapshot],
) -> List[PerformanceAggregate]:
    by_publish: Dict[str, List[PerformanceSnapshot]] = {}

    for snapshot in snapshots:
        by_publish.setdefault(snapshot.publish_id, []).append(snapshot)

    publish_map = {r.publish_id: r for r in publish_records}
    aggregates: List[PerformanceAggregate] = []

    for publish_id, group in by_publish.items():
        group_sorted = sorted(group, key=lambda x: x.captured_at)
        first_seen = group_sorted[0].captured_at
        last_seen = group_sorted[-1].captured_at
        latest_metrics = group_sorted[-1].metrics

        peak_views_snapshot = max(group_sorted, key=lambda x: x.metrics.get("views", 0))
        peak_metrics = peak_views_snapshot.metrics

        views = latest_metrics.get("views", 0)
        if views >= 1200:
            growth_curve_type = "early_spike"
            signal_quality = "medium"
        else:
            growth_curve_type = "flat"
            signal_quality = "low"

        aggregate = PerformanceAggregate.create(
            publish_id=publish_id,
            asset_id=publish_map[publish_id].asset_id,
            snapshot_count=len(group_sorted),
            first_seen_at=first_seen,
            last_seen_at=last_seen,
            latest_metrics=latest_metrics,
            peak_metrics=peak_metrics,
            growth_curve_type=growth_curve_type,
            signal_quality=signal_quality,
            analysis_ready=True,
        )
        aggregates.append(aggregate)

    return aggregates
