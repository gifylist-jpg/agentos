from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ManualGenerationPackage:
    """
    人工执行包：
    系统把 generation_plan 翻译成人类可执行的即梦官网操作包。
    """

    execution_id: str
    task_id: str
    provider_name: str
    instructions: str
    generation_tasks: List[Dict]
