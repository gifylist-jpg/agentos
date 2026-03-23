import time
from typing import Any, Dict, List


class ProjectStateManager:
    def __init__(self) -> None:
        self.projects: Dict[str, Dict[str, Any]] = {}

    # ===============================
    # 初始化项目
    # ===============================
    def init_project(self, project_id: str, project_type: str, goal: str) -> None:
        self.projects[project_id] = {
            "project_id": project_id,
            "project_type": project_type,
            "goal": goal,

            "status": "running",
            "current_stage": "init",
            "current_owner": "coordinator_agent",
            "coordinator": "coordinator_agent",

            "active_roles": [
                "research_agent",
                "content_agent",
                "ops_agent"
            ],

            "workflow_state": {
                "current_step": "init",
                "previous_steps": [],
                "next_steps": ["research", "content", "ops"]
            },

            "task_board": {
                "pending": [],
                "running": [],
                "blocked": [],
                "completed": []
            },

            "role_outputs": {
                "research": {},
                "content": {},
                "ops": {},
                "data": {}
            },

            "artifacts": [],
            "handoff_history": [],
            "message_history": [],

            "blockers": [],
            "approvals": [],

            "metrics": {
                "cost": 0,
                "tokens": 0,
                "latency": 0
            },

            "next_action": "",
            "last_update": time.time()
        }

        print(f"[State][INIT] project_id={project_id} goal={goal}")

    # ===============================
    # 获取状态
    # ===============================
    def get(self, project_id: str) -> Dict[str, Any]:
        return self.projects[project_id]

    # ===============================
    # 通用更新
    # ===============================
    def update(self, project_id: str, **kwargs: Any) -> None:
        self.projects[project_id].update(kwargs)
        self.projects[project_id]["last_update"] = time.time()

        print(f"[State][UPDATE] project_id={project_id} fields={list(kwargs.keys())}")

    # ===============================
    # 更新角色输出
    # ===============================
    def update_role_output(self, project_id: str, role_key: str, output: Dict[str, Any]) -> None:
        self.projects[project_id]["role_outputs"][role_key] = output
        self.projects[project_id]["last_update"] = time.time()

        print(f"[State][OUTPUT] role={role_key} keys={list(output.keys())}")

    # ===============================
    # Message 记录
    # ===============================
    def append_message_history(self, project_id: str, message_id: str) -> None:
        self.projects[project_id]["message_history"].append(message_id)
        self.projects[project_id]["last_update"] = time.time()

        print(f"[State][MESSAGE] message_id={message_id}")

    # ===============================
    # Handoff 记录
    # ===============================
    def append_handoff(self, project_id: str, record: Dict[str, Any]) -> None:
        self.projects[project_id]["handoff_history"].append(record)
        self.projects[project_id]["last_update"] = time.time()

        print(f"[State][HANDOFF] {record['from_role']} -> {record['to_role']}")

    # ===============================
    # Artifact 记录
    # ===============================
    def append_artifact(self, project_id: str, artifact_id: str) -> None:
        self.projects[project_id]["artifacts"].append(artifact_id)
        self.projects[project_id]["last_update"] = time.time()

        print(f"[State][ARTIFACT] {artifact_id}")

    # ===============================
    # 设置阶段（核心）
    # ===============================
    def set_stage(self, project_id: str, stage: str, owner: str, next_action: str = "") -> None:
        state = self.projects[project_id]

        state["current_stage"] = stage
        state["current_owner"] = owner
        state["next_action"] = next_action
        state["last_update"] = time.time()

        print(f"[State][STAGE] stage={stage} owner={owner}")

    # ===============================
    # 🔥 Task Board 同步（关键）
    # ===============================
    def sync_task_board(self, project_id: str, tasks: List[Any]) -> None:
        board = {
            "pending": [],
            "running": [],
            "blocked": [],
            "completed": []
        }

        for task in tasks:
            if task.status in ["created", "queued", "assigned"]:
                board["pending"].append(task.task_id)

            elif task.status == "running":
                board["running"].append(task.task_id)

            elif task.status in ["failed", "blocked"]:
                board["blocked"].append(task.task_id)

            elif task.status == "success":
                board["completed"].append(task.task_id)

        self.projects[project_id]["task_board"] = board
        self.projects[project_id]["last_update"] = time.time()

        print(f"[State][TASK_BOARD] {board}")

    # ===============================
    # 🔥 Workflow 同步（关键）
    # ===============================
    # ===============================
    # Workflow 同步（关键）
    # ===============================
    def sync_workflow(self, project_id: str, current_stage: str) -> None:
        sequence = ["research", "content", "ops"]

        previous_steps = []
        next_steps = []

        if current_stage in sequence:
            idx = sequence.index(current_stage)
            previous_steps = sequence[:idx]
            next_steps = sequence[idx + 1:]
        elif current_stage == "done":
            previous_steps = sequence
            next_steps = []

        workflow_state = {
            "current_step": current_stage,
            "previous_steps": previous_steps,
            "next_steps": next_steps
        }

        self.projects[project_id]["workflow_state"] = workflow_state
        self.projects[project_id]["last_update"] = time.time()

        print(f"[State][WORKFLOW] {workflow_state}")
