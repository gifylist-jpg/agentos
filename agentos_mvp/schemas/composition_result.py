from dataclasses import dataclass
from typing import List


@dataclass
class CompositionResult:
    """
    最小 CompositionResult：
    表示视频合成后的结构结果（当前阶段不包含真实视频文件）。
    """

    composition_id: str
    execution_id: str
    asset_ids: List[str]
    ordered_scene_ids: List[str]
    final_video_uri: str
    status: str
