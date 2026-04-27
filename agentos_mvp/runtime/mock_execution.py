from typing import List

from schemas.generated_asset_record import GeneratedAssetRecord
from schemas.execution_result import ExecutionResult
from runtime.execution_engine import run_execution


def run_mock_execution(
    execution_request,
    assets: List[GeneratedAssetRecord],
    executor_name: str = "ffmpeg",
    composition_plan=None,
) -> ExecutionResult:
    """
    兼容层：
    当前统一转发到 Execution Engine。
    """

    return run_execution(
        execution_request=execution_request,
        assets=assets,
        executor_name=executor_name,
        composition_plan=composition_plan,
    )
