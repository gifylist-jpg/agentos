from dataclasses import dataclass


@dataclass
class NewTaskProposal:
    """
    最小 NewTaskProposal：
    表示由 ExecutionResult + Human Review 生成的新任务提案。
    该对象不会直接执行，只能重新进入 Task Intake。
    """

    source_task_id: str
    source_execution_id: str
    action: str
    reason: str
    goal: str
    product_name: str
    target_platform: str
    target_duration: int
    objective: str
    has_real_footage: bool
    ai_generation_needed: bool
    output_type: str
