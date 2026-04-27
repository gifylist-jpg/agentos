from schemas.production_decision import ProductionDecision
from schemas.execution_request import VideoExecutionRequest


def _build_execution_id(task_id: str) -> str:
    """
    最小唯一执行ID：
    直接基于 task_id 生成，避免多任务时覆盖。
    """
    return f"exec_{task_id}"


def _build_plan_id(task_id: str) -> str:
    """
    最小唯一方案ID：
    直接基于 task_id 生成。
    """
    return f"plan_{task_id}"


def compile_to_execution_request(decision: ProductionDecision) -> VideoExecutionRequest:
    """
    最小 Compiler（多任务安全版）：
    - scenes.asset_type 跟随 asset_plan.required_asset_type
    - output_spec.target_duration 跟随 storyboard 总时长
    - execution_id / plan_id 不再写死，避免多任务覆盖
    """

    asset_type_map = {
        item["scene_id"]: item["required_asset_type"]
        for item in decision.asset_plan
    }

    scenes = [
        {
            "scene_id": scene["scene_id"],
            "duration": scene["duration"],
            "visual_desc": scene["visual_desc"],
            "asset_type": asset_type_map.get(scene["scene_id"], "ai_video"),
        }
        for scene in decision.storyboard
    ]

    generation_plan = []
    for item in decision.asset_plan:
        if item["required_asset_type"] == "ai_video":
            generation_plan.append(
                {
                    "scene_id": item["scene_id"],
                    "asset_type": item["required_asset_type"],
                    "prompt": item["asset_prompt_brief"],
                    "fallback": item["fallback"],
                }
            )

    target_duration = sum(scene["duration"] for scene in decision.storyboard)

    execution_id = _build_execution_id(decision.task_id)
    plan_id = _build_plan_id(decision.task_id)

    return VideoExecutionRequest(
        execution_id=execution_id,
        task_id=decision.task_id,
        plan_id=plan_id,
        scenes=scenes,
        generation_plan=generation_plan,
        edit_plan=decision.edit_plan,
        output_spec={
            "platform": "TikTok",
            "target_duration": target_duration,
            "aspect_ratio": "9:16",
            "delivery_format": "video_sample",
        },
    )
