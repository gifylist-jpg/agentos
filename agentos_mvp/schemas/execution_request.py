from dataclasses import dataclass
from typing import Dict, List


@dataclass
class VideoExecutionRequest:
    """
    最小 VideoExecutionRequest：
    第一阶段作为 Execution OS 的唯一合法输入对象。
    """

    execution_id: str
    task_id: str
    plan_id: str
    scenes: List[Dict]
    generation_plan: List[Dict]
    edit_plan: Dict
    output_spec: Dict
