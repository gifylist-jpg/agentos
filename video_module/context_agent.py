from __future__ import annotations

from typing import Any, Dict

from core.payload import PayloadWrapper


MODULE_ID = "context_agent"
MODULE_VERSION = "0.1.0"


def run_context(task_input: Dict[str, Any]) -> PayloadWrapper:
    product_id = task_input.get("product_id", "unknown_product")
    product_name = task_input.get("product_name", "unknown_product_name")
    target_market = task_input.get("target_market", "US")
    target_audience = task_input.get("target_audience", "general")
    selling_points = task_input.get("selling_points", [])

    data = {
        "context_id": f"context_{product_id}",
        "product_id": product_id,
        "normalized_product_name": str(product_name).strip().lower(),
        "target_market": target_market,
        "target_audience": target_audience,
        "key_selling_points": selling_points,
        "key_risks": [],
        "creative_constraints": ["fast_hook", "native_style", "high_info_density"],
        "banned_elements": [],
        "recommended_angles": ["cute_but_practical", "daily_use", "giftable"],
        "historical_insights": {},
        "confidence": 0.6,
        "uncertainty_sources": ["historical_data_missing"],
    }

    return PayloadWrapper.create(
        schema_name="video_context_output_v1",
        schema_version="1.0",
        producer=f"{MODULE_ID}:{MODULE_VERSION}",
        data=data,
    )
