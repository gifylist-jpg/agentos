from agentos.models.task import Task


class Planner:
    def plan(self, project_id: str, goal: str) -> list[Task]:
        research_task = Task.create(
            project_id=project_id,
            task_type="research",
            title=f"Research for: {goal}",
            owner_role="coordinator_agent",
            target_role="research_agent",
            payload={"goal": goal},
        )

        content_task = Task.create(
            project_id=project_id,
            task_type="content",
            title="Create content plan",
            owner_role="coordinator_agent",
            target_role="content_agent",
            payload={"goal": goal},
            depends_on=[research_task.task_id],
        )

        ops_task = Task.create(
            project_id=project_id,
            task_type="execution",
            title="Execute with OpenClaw",
            owner_role="coordinator_agent",
            target_role="ops_agent",
            payload={"goal": goal},
            depends_on=[content_task.task_id],
        )

        return [research_task, content_task, ops_task]
