from typing import List, Tuple

from schemas.execution_request import VideoExecutionRequest
from schemas.generated_asset_record import GeneratedAssetRecord
from schemas.composition_plan import CompositionPlan
from schemas.composition_result import CompositionResult


def build_composition_plan(
    request: VideoExecutionRequest,
    assets: List[GeneratedAssetRecord],
) -> CompositionPlan:
    """
    根据 edit_plan + assets 顺序，生成最小 CompositionPlan。
    关键规则：
    - clip_order 以传入的 assets 顺序为准
    - 不再强制按 request.scenes 默认顺序展开
    """

    scene_map = {scene["scene_id"]: scene for scene in request.scenes}
    clip_order = []
    asset_count = len(assets)

    for index, asset in enumerate(assets):
        scene_id = asset.scene_id

        if scene_id not in scene_map:
            raise ValueError(f"缺少 asset 对应的 scene 定义: {scene_id}")

        scene = scene_map[scene_id]

        clip_order.append(
            {
                "scene_id": scene_id,
                "asset_id": asset.asset_id,
                "asset_uri": asset.uri,
                "duration": scene["duration"],
                "source": asset.source,
                "pace_tag": _build_pace_tag(request.edit_plan),
                "transition_after": _build_transition_after(
                    index=index,
                    total=asset_count,
                    edit_plan=request.edit_plan,
                ),
                "subtitle_mode": _build_subtitle_mode(request.edit_plan),
                "emphasis": _build_emphasis(
                    index=index,
                    total=asset_count,
                    edit_plan=request.edit_plan,
                ),
                "cta_slot": _build_cta_slot(
                    index=index,
                    total=asset_count,
                    edit_plan=request.edit_plan,
                ),
            }
        )

    return CompositionPlan(
        composition_id=f"comp_{request.execution_id}",
        execution_id=request.execution_id,
        clip_order=clip_order,
        subtitle_strategy=request.edit_plan.get("subtitle_strategy", "default"),
        bgm_style=request.edit_plan.get("bgm_style", "default"),
        transition_style=request.edit_plan.get("transition_style", "cut"),
        cta_position=request.edit_plan.get("cta_position", "end"),
    )


def compose_video(
    request: VideoExecutionRequest,
    assets: List[GeneratedAssetRecord],
) -> Tuple[CompositionPlan, CompositionResult]:
    """
    最小 Video Composition：
    先生成 CompositionPlan，再生成 CompositionResult。
    当前阶段不做真实视频拼接逻辑，只输出结构对象。
    """

    plan = build_composition_plan(request, assets)

    result = CompositionResult(
        composition_id=plan.composition_id,
        execution_id=plan.execution_id,
        asset_ids=[clip["asset_id"] for clip in plan.clip_order],
        ordered_scene_ids=[clip["scene_id"] for clip in plan.clip_order],
        final_video_uri=f"composed://{request.execution_id}",
        status="success",
    )

    return plan, result


def _build_pace_tag(edit_plan: dict) -> str:
    pace = edit_plan.get("pace", "normal")
    cut_frequency = edit_plan.get("cut_frequency", "medium")
    return f"{pace}_{cut_frequency}"


def _build_transition_after(index: int, total: int, edit_plan: dict) -> str:
    if index == total - 1:
        return "end"
    return edit_plan.get("transition_style", "cut")


def _build_subtitle_mode(edit_plan: dict) -> str:
    return edit_plan.get("subtitle_strategy", "default")


def _build_emphasis(index: int, total: int, edit_plan: dict) -> str:
    pace = edit_plan.get("pace", "normal")
    if index == 0 and pace == "fast":
        return "hook_emphasis"
    if index == total - 1:
        return "cta_emphasis"
    return "normal"


def _build_cta_slot(index: int, total: int, edit_plan: dict) -> str:
    cta_position = edit_plan.get("cta_position", "end")

    if cta_position == "last_3_seconds" and index == total - 1:
        return "cta_insert_here"

    return "no_cta"
