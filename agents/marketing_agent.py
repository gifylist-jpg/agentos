
from monitor.token_tracker import tracker


def execute(task, llm, tool_registry):
    task_id = getattr(task, "id", None)
    task_type = getattr(task, "type", "marketing")
    task_text = getattr(task, "task", "") or getattr(task, "name", "")

    messages = [
        {
            "role": "system",
            "content": "You are a professional marketing agent. Produce practical, strategic, and execution-oriented marketing outputs."
        },
        {
            "role": "user",
            "content": f"""Task: {task_text}

Please provide:
1. Marketing strategy
2. Promotion plan
3. Audience targeting suggestions
4. Execution recommendations
"""
        }
    ]

    llm_result = llm.call_with_metadata(task_type, messages, task_id=task_id)
    result_text = llm_result["content"]

    try:
        real_token_usage = tracker.get_total_tokens_by_task_id(task_id)
    except Exception:
        real_token_usage = 0

    return {
        "task_id": task_id,
        "task_type": task_type,
        "agent": "marketing",
        "result": result_text,
        "summary": result_text[:300] if isinstance(result_text, str) else str(result_text),
        "model": llm_result["provider"],
        "model_name": llm_result["model_name"],
        "token_usage": real_token_usage,
        "status": "completed",
    }
