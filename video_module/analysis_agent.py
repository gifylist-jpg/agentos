from __future__ import annotations

from typing import Any, Dict, List

from core.decision_record import DecisionRecord
from core.performance_snapshot import PerformanceAggregate


MODULE_ID = "performance_analysis_agent"
MODULE_VERSION = "0.1.0"


def analyze_performance(
    task_id: str,
    strategy_payload: Dict[str, Any],
    aggregates: List[PerformanceAggregate],
) -> Dict[str, Any]:
    """
    第一版规则分析：
    不追求复杂智能，只输出：
    keep / drop / retest / wait_more_data
    """
    variant_plans = strategy_payload["data"]["variant_plans"]
    variant_by_id = {v["variant_id"]: v for v in variant_plans}

    asset_results: List[Dict[str, Any]] = []
    best_item = None

    for aggregate in aggregates:
        latest = aggregate.latest_metrics
        ctr = latest.get("ctr", 0.0)
        cvr = latest.get("cvr", 0.0)
        views = latest.get("views", 0)

        # 简单建议规则
        if aggregate.signal_quality == "low" or views < 900:
            suggestion = "wait_more_data"
            score = 0.0
        else:
            score = ctr * 0.7 + cvr * 0.3
            if score >= 0.03:
                suggestion = "keep"
            elif score >= 0.02:
                suggestion = "retest"
            else:
                suggestion = "drop"

        result = {
            "asset_id": aggregate.asset_id,
            "publish_id": aggregate.publish_id,
            "score": round(score, 4),
            "suggestion": suggestion,
            "latest_metrics": latest,
            "signal_quality": aggregate.signal_quality,
            "growth_curve_type": aggregate.growth_curve_type,
        }
        asset_results.append(result)

        if best_item is None or result["score"] > best_item["score"]:
            best_item = result

    recommended_next_action = "wait_more_data"
    reason = "insufficient signal"
    confidence = 0.4

    if best_item:
        if best_item["suggestion"] == "keep":
            recommended_next_action = "keep_best_and_prepare_next_batch"
            reason = f"best asset {best_item['asset_id']} has strongest early combined score"
            confidence = 0.65
        elif best_item["suggestion"] == "retest":
            recommended_next_action = "retest_with_same_angle_and_new_hook"
            reason = f"best asset {best_item['asset_id']} shows some promise but not enough"
            confidence = 0.55
        elif best_item["suggestion"] == "drop":
            recommended_next_action = "drop_current_batch_and_try_new_angle"
            reason = "all current assets are weak in early-stage signal"
            confidence = 0.5

    decision = DecisionRecord.create(
        task_id=task_id,
        decision_type="performance_feedback_decision",
        decider=f"{MODULE_ID}:{MODULE_VERSION}",
        input_refs=[agg.aggregate_id for agg in aggregates],
        decision_result={
            "recommended_next_action": recommended_next_action,
            "best_asset_id": best_item["asset_id"] if best_item else None,
            "asset_results": asset_results,
        },
        reason=reason,
        confidence=confidence,
    )

    return {
        "analysis_summary": {
            "recommended_next_action": recommended_next_action,
            "best_asset_id": best_item["asset_id"] if best_item else None,
            "asset_results": asset_results,
        },
        "decision_record": decision,
    }
