from schemas.task_request import TaskRequest
from schemas.new_task_proposal import NewTaskProposal
from schemas.execution_result import ExecutionResult
from schemas.video_task_feedback import VideoTaskFeedback


def build_new_task_proposal(
    task: TaskRequest,
    result: ExecutionResult,
    feedback: VideoTaskFeedback,
    human_action: str,
    human_reason: str,
) -> NewTaskProposal | None:
    """
    根据本次任务结果 + 人工判断，生成新的任务提案。
    不会自动执行，只负责形成下一轮入口对象。
    """

    action = human_action.strip().lower()

    if action == "stop":
        return None

    if action == "retry":
        goal = f"{task.goal}（基于上一轮结果重试）"
    elif action == "refine":
        goal = f"{task.goal}（基于上一轮结果优化后重做）"
    else:
        goal = f"{task.goal}（基于上一轮结果继续迭代）"

    return NewTaskProposal(
        source_task_id=task.task_id,
        source_execution_id=result.execution_id,
        action=action,
        reason=human_reason,
        goal=goal,
        product_name=task.product_name,
        target_platform=task.target_platform,
        target_duration=task.target_duration,
        objective=task.objective,
        has_real_footage=task.has_real_footage,
        ai_generation_needed=task.ai_generation_needed,
        output_type=task.output_type,
    )


def intake_from_proposal(proposal: NewTaskProposal) -> TaskRequest:
    """
    最小 Task Intake 回流：
    把 NewTaskProposal 收敛成新的 TaskRequest。
    当前阶段只做最小字段映射，不做自动执行。
    """

    suffix = proposal.action if proposal.action else "next"

    return TaskRequest(
        task_id=f"{proposal.source_task_id}_{suffix}_v2",
        goal=proposal.goal,
        product_name=proposal.product_name,
        target_platform=proposal.target_platform,
        target_duration=proposal.target_duration,
        objective=proposal.objective,
        has_real_footage=proposal.has_real_footage,
        ai_generation_needed=proposal.ai_generation_needed,
        output_type=proposal.output_type,
    )
