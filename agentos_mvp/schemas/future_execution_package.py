from dataclasses import dataclass
from typing import List, Dict


@dataclass
class FutureExecutionPackage:
    """
    未来执行器执行包：
    预留给 剪映 + OpenClaw / 其他本地工具执行器。
    """

    execution_id: str
    task_id: str
    executor_name: str
    composition_plan: Dict
    assets: List[Dict]
    instructions: List[str]
    expected_output: str
