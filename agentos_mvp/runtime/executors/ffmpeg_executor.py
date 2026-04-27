from typing import List

from schemas.execution_result import ExecutionResult
from schemas.generated_asset_record import GeneratedAssetRecord
from runtime.video_composer_ffmpeg import compose_with_ffmpeg


def run_ffmpeg_executor(execution_request, assets: List[GeneratedAssetRecord]) -> ExecutionResult:
    """
    ffmpeg 执行器：
    负责把素材拼接成真实视频文件。
    """

    video_path = compose_with_ffmpeg(
        execution_id=execution_request.execution_id,
        assets=assets,
    )

    if video_path is None:
        status = "failed"
        video_url = None
    else:
        status = "success"
        video_url = video_path

    scene_status = [
        {
            "scene_id": a.scene_id,
            "asset_id": a.asset_id,
            "uri": a.uri,
            "status": a.status,
            "source": a.source,
            "operator": a.operator,
        }
        for a in assets
    ]

    return ExecutionResult(
        execution_id=execution_request.execution_id,
        task_id=execution_request.task_id,
        status=status,
        video_url=video_url,
        scene_status=scene_status,
    )
