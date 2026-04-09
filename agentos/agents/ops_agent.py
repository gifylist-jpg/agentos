# 🚨 EXECUTION PATH VIOLATION - MUST MIGRATE TO ExecutionAdapter
from agentos.execution.execution_adapter import ExecutionAdapter
from agentos.models.artifact import Artifact


class OpsAgent:
    role_id = "ops_agent"

    def __init__(self) -> None:
        # Replacing ToolExecutor with ExecutionAdapter
        self.execution_adapter = ExecutionAdapter()

    def run(self, task, message, state_manager, artifact_store):
        print(f"[Agent][RUN] role={self.role_id} task_id={task.task_id} msg_id={message.message_id}")

        content_output = message.payload
        parsed = content_output.get("parsed", {}) if isinstance(content_output, dict) else {}
        execution_plan = parsed.get("execution_plan", [])

        payload = {
            "action": "openclaw_execute_video_workflow",
            "steps": execution_plan if execution_plan else [
                "打开素材网站",
                "准备视频素材",
                "整理剪辑步骤",
                "输出执行结果",
            ],
            "content_output": content_output,
        }

        # Using ExecutionAdapter to execute the task
        execution_result = self.execution_adapter.execute({"payload": payload})

        artifact = Artifact.create(
            project_id=task.project_id,
            task_id=task.task_id,
            artifact_type="execution_result",
            name="ops_execution_output",
            content=execution_result,
            created_by=self.role_id,
        )

        artifact_id = artifact_store.save(artifact)
        state_manager.update_role_output(task.project_id, "ops", execution_result)
        state_manager.append_artifact(task.project_id, artifact_id)

        return {
            "status": execution_result.get("status", "failed"),
            "result": execution_result,
            "artifact_ids": [artifact_id],
            "summary": "执行岗位已完成本地任务",
        }

# Ensure that OpsAgent passes the correct execution mode to ExecutionAdapter
ops_agent_request = {
    "payload": {
        "execution_mode": "delayed",  # Could be retry, delayed, scheduled
        "delay_time": 10,
    }
}
execution_adapter.execute(ops_agent_request)
execution_adapter = ExecutionAdapter()
