from typing import List

from schemas.execution_request import VideoExecutionRequest
from schemas.manual_generation_package import ManualGenerationPackage
from schemas.generated_asset_record import GeneratedAssetRecord


def build_manual_generation_package(request: VideoExecutionRequest) -> ManualGenerationPackage:
    """
    根据 VideoExecutionRequest 生成给人类执行的即梦官网操作包。
    """

    generation_tasks = []

    for item in request.generation_plan:
        generation_tasks.append(
            {
                "scene_id": item["scene_id"],
                "prompt": item["prompt"],
                "asset_type": item["asset_type"],
                "fallback": item["fallback"],
                "target_duration": _find_scene_duration(request, item["scene_id"]),
                "provider": "Jimeng Seedance 2.0",
            }
        )

    instructions = (
        "请人工打开即梦官网，选择 Seedance 2.0，"
        "按 generation_tasks 中每个 scene 的 prompt 逐条生成视频，"
        "生成完成后记录每个 scene 对应的素材 URI 或本地路径，再回填到系统。"
    )

    return ManualGenerationPackage(
        execution_id=request.execution_id,
        task_id=request.task_id,
        provider_name="Jimeng Seedance 2.0",
        instructions=instructions,
        generation_tasks=generation_tasks,
    )


def build_demo_generated_assets(pkg: ManualGenerationPackage) -> List[GeneratedAssetRecord]:
    """
    当前阶段的演示回填函数：
    先用占位 URI 模拟人工已经生成并回填。
    后续再改成真正的人工填写输入。
    """

    assets = []

    for task in pkg.generation_tasks:
        scene_id = task["scene_id"]
        assets.append(
            GeneratedAssetRecord(
                asset_id=f"manual_asset_{scene_id}",
                scene_id=scene_id,
                source="jimeng_manual",
                uri=f"manual://{scene_id}",
                status="success",
                operator="human",
            )
        )

    return assets


def _find_scene_duration(request: VideoExecutionRequest, scene_id: str) -> int:
    for scene in request.scenes:
        if scene["scene_id"] == scene_id:
            return scene["duration"]
    return 0
