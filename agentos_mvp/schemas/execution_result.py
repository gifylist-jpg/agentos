from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ExecutionResult:
    """
    最小 ExecutionResult：
    第一阶段用于承载统一执行结果对象。
    """

    execution_id: str
    task_id: str
    status: str
    video_url: Optional[str]
    scene_status: List[dict]
    future_execution_package: Optional[Any] = None
