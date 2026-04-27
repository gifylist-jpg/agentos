from typing import Dict, List


def build_future_execution_package(composition_plan, execution_request) -> Dict:
    """
    从 CompositionPlan + ExecutionRequest 构建 FutureExecutionPackage
    用于剪映 / OpenClaw / 其他剪辑工具
    """

    clips: List[Dict] = []

    for clip in composition_plan.clip_order:
        role = "content"

        if clip.get("emphasis") == "hook_emphasis":
            role = "hook"
        elif clip.get("emphasis") == "cta_emphasis":
            role = "cta"

        source_type = "ai_video"
        if clip.get("source") == "human_real_footage":
            source_type = "real"

        clips.append(
            {
                "scene_id": clip["scene_id"],
                "asset_uri": clip["asset_uri"],
                "duration": clip["duration"],
                "role": role,
                "source_type": source_type,
            }
        )

    package = {
        "execution_id": composition_plan.execution_id,
        "platform": execution_request.output_spec.get("platform"),
        "aspect_ratio": execution_request.output_spec.get("aspect_ratio"),
        "total_duration": execution_request.output_spec.get("target_duration"),
        "clips": clips,
        "global_edit": {
            "pace": execution_request.edit_plan.get("pace"),
            "transition": execution_request.edit_plan.get("transition_style"),
            "bgm_style": execution_request.edit_plan.get("bgm_style"),
            "subtitle": execution_request.edit_plan.get("subtitle_strategy"),
        },
    }

    return package
