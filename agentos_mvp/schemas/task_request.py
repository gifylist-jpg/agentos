from dataclasses import dataclass


@dataclass
class TaskRequest:
    """
    最小 TaskRequest：
    第一阶段只承载一条带货视频任务进入主链所需的最小信息。
    """

    task_id: str
    goal: str
    product_name: str
    target_platform: str = "TikTok"
    target_duration: int = 15
    objective: str = "带货转化"
    has_real_footage: bool = False
    ai_generation_needed: bool = True
    output_type: str = "video_sample"
