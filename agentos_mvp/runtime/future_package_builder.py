from schemas.future_execution_package import FutureExecutionPackage


def build_future_execution_package(execution_request, assets, composition_plan) -> FutureExecutionPackage:
    """
    把当前执行请求 + 素材 + 合成计划
    收敛成未来执行器可消费的执行包。
    """

    asset_items = [
        {
            "asset_id": a.asset_id,
            "scene_id": a.scene_id,
            "uri": a.uri,
            "source": a.source,
            "status": a.status,
            "operator": a.operator,
        }
        for a in assets
    ]

    instructions = [
        "打开剪映项目或创建新项目",
        "按 composition_plan.clip_order 顺序导入素材",
        "按 clip_order 顺序排列片段",
        "按 composition_plan 中的 cta / emphasis / transition 信息进行人工或工具辅助执行",
        "导出最终成片为 mp4",
    ]

    composition_plan_dict = {
        "composition_id": composition_plan.composition_id,
        "execution_id": composition_plan.execution_id,
        "clip_order": composition_plan.clip_order,
        "subtitle_strategy": composition_plan.subtitle_strategy,
        "bgm_style": composition_plan.bgm_style,
        "transition_style": composition_plan.transition_style,
        "cta_position": composition_plan.cta_position,
    }

    return FutureExecutionPackage(
        execution_id=execution_request.execution_id,
        task_id=execution_request.task_id,
        executor_name="future",
        composition_plan=composition_plan_dict,
        assets=asset_items,
        instructions=instructions,
        expected_output="final_video.mp4",
    )
