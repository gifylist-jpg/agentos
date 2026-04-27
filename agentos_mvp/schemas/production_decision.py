from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ProductionDecision:
    """
    最小 ProductionDecision：
    第一阶段先承载 Director + Editor 汇总后的统一方案对象。
    当前这一轮先只由 Director 填充部分字段。
    """

    task_id: str
    selling_points: List[str]
    hook: str
    script: str
    storyboard: List[Dict]
    asset_plan: List[Dict]
    edit_plan: Dict
