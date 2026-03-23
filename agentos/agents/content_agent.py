from agentos.models.artifact import Artifact
from agentos.core.model_router import ModelRouter
from agentos.core.safe_llm_caller import SafeLLMCaller
from agentos.core.json_utils import extract_json_block


class ContentAgent:
    role_id = "content_agent"

    def __init__(self) -> None:
        self.router = ModelRouter()
        self.llm = SafeLLMCaller()

    def run(self, task, message, state_manager, artifact_store):
        print(f"[Agent][RUN] role={self.role_id} task_id={task.task_id} msg_id={message.message_id}")

        research_output = message.payload
        research_parsed = research_output.get("parsed", {}) if isinstance(research_output, dict) else {}

        prompt = f"""
你是 TikTok 美区电商视频内容策划。

请基于下面 research 结果，输出一个真正可执行的视频方案。
不要输出 markdown，不要输出解释，不要输出占位词。

research 结果：
{research_parsed}

输出严格 JSON：
{{
  "video_angle": "一句话写清楚这条视频的核心角度，必须具体",
  "script_outline": [
    "第1步具体拍什么",
    "第2步具体拍什么",
    "第3步具体拍什么",
    "第4步具体拍什么"
  ],
  "hooks": [
    "具体钩子1",
    "具体钩子2",
    "具体钩子3"
  ],
  "execution_plan": [
    "执行动作1，必须具体",
    "执行动作2，必须具体",
    "执行动作3，必须具体"
  ]
}}

要求：
1. 不准写“角度1”“步骤1”“钩子1”“执行动作1”这种占位内容
2. 必须围绕 TikTok 美区、日系双肩包、真实短视频拍法来写
3. script_outline 要能直接给剪辑/拍摄人员执行
4. execution_plan 要是 Ops 能直接照着做的动作
"""

        provider_chain = self.router.get_provider_chain("content")
        llm_result = self.llm.call_with_fallback(
            task_type="content",
            prompt=prompt,
            provider_chain=provider_chain,
        )

        parsed = extract_json_block(llm_result["content"])

        result = {
            "provider_used": llm_result["provider"],
            "model_used": llm_result["model"],
            "raw_content": llm_result["content"],
            "parsed": parsed,
            "based_on": research_output,
        }

        artifact = Artifact.create(
            project_id=task.project_id,
            task_id=task.task_id,
            artifact_type="content_plan",
            name="content_output",
            content=result,
            created_by=self.role_id,
        )

        artifact_id = artifact_store.save(artifact)
        state_manager.update_role_output(task.project_id, "content", result)
        state_manager.append_artifact(task.project_id, artifact_id)

        return {
            "status": "success",
            "result": result,
            "artifact_ids": [artifact_id],
            "summary": "内容创意与脚本完成，已交接执行岗位",
        }
