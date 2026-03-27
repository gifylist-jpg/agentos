from __future__ import annotations

from typing import Any, Dict, List

from core.payload import PayloadWrapper


MODULE_ID = "creative_strategy_agent"
MODULE_VERSION = "0.1.0"


def _build_variant(variant_id: str, hook_type: str, angle: str, cta: str) -> Dict[str, Any]:
    return {
        "variant_id": variant_id,
        "hook_type": hook_type,
        "angle": angle,
        "opening_line": f"{hook_type} opening for {angle}",
        "scene_structure": [
            "hook",
            "problem_or_desire",
            "product_showcase",
            "capacity_or_usage",
            "cta",
        ],
        "cta": cta,
        "variable_tags": {
            "hook_type": hook_type,
            "angle": angle,
            "cta": cta,
        },
    }


def run_strategy(context_payload: PayloadWrapper) -> PayloadWrapper:
    context = context_payload.data
    product_id = context["product_id"]

    variants: List[Dict[str, Any]] = [
        _build_variant("var_001", "problem_opening", "cute_but_practical", "comment BAG"),
        _build_variant("var_002", "gift_opening", "giftable", "shop now"),
        _build_variant("var_003", "showcase_opening", "daily_use", "comment PINK"),
    ]

    data = {
        "strategy_id": f"strategy_{product_id}",
        "product_id": product_id,
        "objective_type": "hook_test",
        "hypothesis": "problem_opening may outperform other hooks for this product",
        "global_constraints": context.get("creative_constraints", []),
        "variant_plans": variants,
        "recommended_experiment_type": "hook_ab_test",
        "confidence": 0.55,
        "uncertainty_sources": ["no_real_performance_feedback_yet"],
    }

    return PayloadWrapper.create(
        schema_name="creative_strategy_output_v1",
        schema_version="1.0",
        producer=f"{MODULE_ID}:{MODULE_VERSION}",
        data=data,
    )
