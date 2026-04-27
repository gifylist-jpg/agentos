from typing import List

from schemas.execution_result import ExecutionResult
from schemas.generated_asset_record import GeneratedAssetRecord
from runtime.future_package_builder import build_future_execution_package


def run_future_executor(
    execution_request,
    assets: List[GeneratedAssetRecord],
    composition_plan=None,
) -> ExecutionResult:
    """
    未来执行器：
    当前阶段不做真实执行，只生成正式执行包，并返回占位 ExecutionResult。
    """

    if composition_plan is None:
        raise ValueError("future_executor 需要 composition_plan")

    package = build_future_execution_package(
        execution_request=execution_request,
        assets=assets,
        composition_plan=composition_plan,
    )

    return ExecutionResult(
        execution_id=execution_request.execution_id,
        task_id=execution_request.task_id,
        status="pending_manual_execution",
        video_url=None,
        scene_status=[
            {
                "scene_id": a.scene_id,
                "asset_id": a.asset_id,
                "uri": a.uri,
                "status": a.status,
                "source": a.source,
                "operator": a.operator,
            }
            for a in assets
        ],
        future_execution_package=package,
    )
