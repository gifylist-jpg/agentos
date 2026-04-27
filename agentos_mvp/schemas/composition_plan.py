from dataclasses import dataclass
from typing import List, Dict


@dataclass
class CompositionPlan:
    """
    最小 CompositionPlan（升级版）：
    表示由 edit_plan 驱动生成的最终合成结构计划。
    当前阶段仍不做真实剪辑，但 edit_plan 会下沉到 clip 级控制。
    """

    composition_id: str
    execution_id: str
    clip_order: List[Dict]
    subtitle_strategy: str
    bgm_style: str
    transition_style: str
    cta_position: str
