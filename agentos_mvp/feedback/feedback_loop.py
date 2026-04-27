from schemas.video_task_feedback import VideoTaskFeedback


def build_feedback(execution_result) -> VideoTaskFeedback:
    """
    最小反馈构建：
    根据 ExecutionResult.status 返回结构化反馈。
    """

    if execution_result.status == "success":
        production_feedback = "素材已生成并完成最小收尾，执行链路成立。"
        business_feedback = "样片结果已可进入人工质量判断，当前尚未自动判断业务价值。"
        next_action = "human_review_sample"

    elif execution_result.status == "pending_manual_execution":
        production_feedback = "已生成未来执行包，等待人工或工具执行。"
        business_feedback = "当前尚未产生最终成片，暂不能做业务判断。"
        next_action = "manual_execute_future_package"

    else:
        production_feedback = "执行未成功，需检查主链结构或执行层。"
        business_feedback = "当前结果不可用于业务判断。"
        next_action = "fix_and_retry"

    return VideoTaskFeedback(
        task_id=execution_result.task_id,
        execution_id=execution_result.execution_id,
        production_feedback=production_feedback,
        business_feedback=business_feedback,
        next_action=next_action,
    )
