from agentos.models.message import Message


class Coordinator:
    role_id = "coordinator_agent"

    def __init__(self, messaging_hub, state_manager, task_queue, workflow_engine) -> None:
        self.messaging_hub = messaging_hub
        self.state_manager = state_manager
        self.task_queue = task_queue
        self.workflow_engine = workflow_engine

    def start_project(self, project_id: str, goal: str, tasks: list) -> None:
        self.task_queue.add_tasks(tasks)

        first_task = tasks[0]
        self.task_queue.update_status(first_task.task_id, "assigned")

        self.state_manager.set_stage(
            project_id,
            stage="research",
            owner="research_agent",
            next_action="等待 research_agent 处理",
        )

        msg = Message.create(
            message_type="task_assign",
            project_id=project_id,
            task_id=first_task.task_id,
            from_role=self.role_id,
            to_role="research_agent",
            summary="开始选品调研",
            required_action="run_research",
            payload=first_task.payload,
        )

        self.messaging_hub.send(msg)
        self.state_manager.append_message_history(project_id, msg.message_id)

    def handoff(
        self,
        project_id: str,
        from_role: str,
        current_task_id: str,
        payload: dict,
        summary: str,
        artifact_ids: list[str] | None = None,
    ) -> None:
        next_role = self.workflow_engine.get_next_role(from_role)
        if not next_role:
            self.state_manager.set_stage(
                project_id,
                stage="done",
                owner="coordinator_agent",
                next_action="主链流程已完成",
            )
            self.state_manager.update(project_id, status="completed")
            return

        next_task = None
        for task in self.task_queue.list_all():
            if task.project_id == project_id and task.target_role == next_role:
                next_task = task
                break

        if next_task is None:
            raise ValueError(f"No next task found for role={next_role}")

        self.task_queue.update_status(next_task.task_id, "assigned")

        msg = Message.create(
            message_type="handoff",
            project_id=project_id,
            task_id=next_task.task_id,
            from_role=from_role,
            to_role=next_role,
            summary=summary,
            required_action="continue_workflow",
            payload=payload,
            artifacts=artifact_ids or [],
        )

        self.messaging_hub.send(msg)
        self.state_manager.append_message_history(project_id, msg.message_id)
        self.state_manager.append_handoff(
            project_id,
            {
                "from_role": from_role,
                "to_role": next_role,
                "from_task_id": current_task_id,
                "to_task_id": next_task.task_id,
                "summary": summary,
            },
        )

        stage_map = {
            "research_agent": "research",
            "content_agent": "content",
            "ops_agent": "ops",
            "data_agent": "data",
        }
        self.state_manager.set_stage(
            project_id,
            stage=stage_map.get(next_role, "unknown"),
            owner=next_role,
            next_action=f"等待 {next_role} 处理",
        )
