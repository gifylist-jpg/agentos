from monitor.token_tracker import tracker


def execute(task, llm, tool_registry):
    task_id = getattr(task, "id", None)
    task_type = getattr(task, "type", "research")
    task_text = getattr(task, "task", "") or getattr(task, "name", "")

    # ✅ 调用工具（保留你原有逻辑）
    web_search = tool_registry.get_tool("web_search")
    search_result = web_search(task_text) if web_search else ""

    # ✅ 构造消息
    messages = [
        {
            "role": "system",
            "content": "You are a professional research agent. Produce concise, useful research outputs."
        },
        {
            "role": "user",
            "content": f"""Task: {task_text}

Context from tools:
{search_result}

Please provide:
1. Key findings
2. Important signals
3. Actionable summary
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
        "agent": "research",
        "result": result_text,
        "summary": result_text[:300] if isinstance(result_text, str) else str(result_text),
        "model": llm_result["provider"],
        "model_name": llm_result["model_name"],
        "token_usage": real_token_usage,
        "status": "completed",
    }
