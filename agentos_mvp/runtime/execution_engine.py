from typing import List

from schemas.generated_asset_record import GeneratedAssetRecord
from schemas.execution_result import ExecutionResult
from runtime.executors.ffmpeg_executor import run_ffmpeg_executor
from runtime.executors.future_executor import run_future_executor
from runtime.executors.ffmpeg_from_future import run_ffmpeg_from_future
from runtime.future_package_builder import build_future_execution_package


def run_execution(
    execution_request,
    assets: List[GeneratedAssetRecord],
    executor_name: str = "ffmpeg",
    composition_plan=None,
) -> ExecutionResult:
    """
    Execution Engine：
    根据 executor_name 调度具体执行器。
    """

    if executor_name == "ffmpeg":
        return run_ffmpeg_executor(execution_request, assets)

    if executor_name == "future":
        return run_future_executor(
            execution_request=execution_request,
            assets=assets,
            composition_plan=composition_plan,
        )

    if executor_name == "ffmpeg_future":
        package = build_future_execution_package(
            execution_request=execution_request,
            assets=assets,
            composition_plan=composition_plan,
        )

        video_path = run_ffmpeg_from_future(package)

        return ExecutionResult(
            execution_id=execution_request.execution_id,
            task_id=execution_request.task_id,
            status="success" if video_path else "failed",
            video_url=video_path,
            scene_status=[],
            future_execution_package=package,
        )

    raise ValueError(f"未知执行器: {executor_name}")
