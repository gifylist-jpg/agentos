from agentos.models.artifact import Artifact
from agentos.core.model_router import ModelRouter
from agentos.core.safe_llm_caller import SafeLLMCaller
from agentos.core.json_utils import extract_json_block


class ResearchAgent:
    role_id = "research_agent"

    def __init__(self) -> None:
        self.router = ModelRouter()
        self.llm = SafeLLMCaller()

    def run(self, task, message, state_manager, artifact_store):
        print(f"[Agent][RUN] role={self.role_id} task_id={task.task_id} msg_id={message.message_id}")

        goal = message.payload.get("goal", "")

        prompt = f"""
你是 TikTok 美区电商选品与趋势研究员。

任务目标：
{goal}

请输出严格 JSON，不要输出 markdown，不要输出解释文字，不要输出示例占位词。
内容必须具体，必须贴合“TikTok 美区 + 日系双肩包”这个业务场景。

输出格式：
{{
  "product_direction": "一句话写清楚推荐卖什么样的包，必须具体，不准写泛泛的词",
  "trend_summary": "2-4句写清楚为什么这个方向适合 TikTok 美区，必须具体，不准写空话",
  "angles": [
    "具体内容角度1",
    "具体内容角度2",
    "具体内容角度3"
  ]
}}

要求：
1. 不要写“推荐的产品方向”“趋势总结”“角度1”这类占位内容
2. 必须给出真实可用的业务内容
3. angles 必须是可以直接拿去拍视频的方向
"""

        provider_chain = self.router.get_provider_chain("research")
        llm_result = self.llm.call_with_fallback(
            task_type="research",
            prompt=prompt,
            provider_chain=provider_chain,
        )

        parsed = extract_json_block(llm_result["content"])

        result = {
            "provider_used": llm_result["provider"],
            "model_used": llm_result["model"],
            "raw_content": llm_result["content"],
            "parsed": parsed,
        }

        artifact = Artifact.create(
            project_id=task.project_id,
            task_id=task.task_id,
            artifact_type="research_report",
            name="research_output",
            content=result,
            created_by=self.role_id,
        )

        artifact_id = artifact_store.save(artifact)
        state_manager.update_role_output(task.project_id, "research", result)
        state_manager.append_artifact(task.project_id, artifact_id)

        return {
            "status": "success",
            "result": result,
            "artifact_ids": [artifact_id],
            "summary": "研究完成，已交接内容岗位",
        }
