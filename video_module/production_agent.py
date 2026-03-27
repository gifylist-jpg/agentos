from __future__ import annotations

from typing import Any, Dict, List

from core.asset import Asset
from core.payload import PayloadWrapper


MODULE_ID = "video_production_agent"
MODULE_VERSION = "0.1.0"


def run_production(task_id: str, strategy_payload: PayloadWrapper) -> Dict[str, Any]:
    strategy = strategy_payload.data
    product_id = strategy["product_id"]
    strategy_id = strategy["strategy_id"]

    produced_assets: List[Dict[str, Any]] = []

    for idx, variant in enumerate(strategy["variant_plans"], start=1):
        asset = Asset.create(
            asset_type="final_video",
            file_uri=f"/tmp/{product_id}__{variant['variant_id']}__demo_{idx}.mp4",
            format="mp4",
            producer_module_id=f"{MODULE_ID}:{MODULE_VERSION}",
            related_task_id=task_id,
            tags=variant["variable_tags"],
            variant_id=variant["variant_id"],
            strategy_id=strategy_id,
        )
        asset.source_tool = "demo_stub"
        asset.source_type = "generated"

        produced_assets.append(asset.to_dict())

    output_data = {
        "production_batch_id": f"batch_{product_id}",
        "strategy_id": strategy_id,
        "product_id": product_id,
        "produced_assets": produced_assets,
        "failed_jobs": [],
        "confidence": 0.5,
        "uncertainty_sources": ["production_is_stubbed"],
    }

    output_payload = PayloadWrapper.create(
        schema_name="video_production_output_v1",
        schema_version="1.0",
        producer=f"{MODULE_ID}:{MODULE_VERSION}",
        data=output_data,
    )

    return {
        "output_payload": output_payload,
        "assets": produced_assets,
    }
