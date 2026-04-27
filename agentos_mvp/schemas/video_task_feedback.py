from dataclasses import dataclass


@dataclass
class VideoTaskFeedback:
    """
    最小 VideoTaskFeedback：
    第一阶段只承载结果摘要和下一步建议，
    不直接驱动再次执行。
    """

    task_id: str
    execution_id: str
    production_feedback: str
    business_feedback: str
    next_action: str
