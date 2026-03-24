from agentos.config.settings import PROJECT_ID, PROJECT_TYPE
from agentos.organization.messaging_hub import MessagingHub
from agentos.organization.workflow_engine import WorkflowEngine
from agentos.core.project_state_manager import ProjectStateManager
from agentos.core.artifact_store import ArtifactStore
from agentos.core.task_queue import TaskQueue
from agentos.core.planner import Planner
from agentos.core.coordinator import Coordinator
from agentos.agents.research_agent import ResearchAgent
from agentos.agents.content_agent import ContentAgent
from agentos.agents.ops_agent import OpsAgent


class Orchestrator:
    def __init__(self) -> None:
        self.project_id = PROJECT_ID
        self.project_type = PROJECT_TYPE

        self.messaging_hub = MessagingHub()
        self.workflow_engine = WorkflowEngine()
        self.state_manager = ProjectStateManager()
        self.artifact_store = ArtifactStore()
        self.task_queue = TaskQueue()
        self.planner = Planner()

        self.coordinator = Coordinator(
            messaging_hub=self.messaging_hub,
            state_manager=self.state_manager,
            task_queue=self.task_queue,
            workflow_engine=self.workflow_engine,
        )

        self.research_agent = ResearchAgent()
        self.content_agent = ContentAgent()
        self.ops_agent = OpsAgent()

    def sync_task_board(self) -> None:
        self.state_manager.sync_task_board(
            self.project_id,
            self.task_queue.list_all()
        )

    def sync_workflow(self, stage: str) -> None:
        self.state_manager.sync_workflow(self.project_id, stage)

    def run(self, goal: str) -> dict:
        print(f"[Orchestrator][START] project_id={self.project_id} goal={goal}")

        # 1. 初始化项目
        self.state_manager.init_project(self.project_id, self.project_type, goal)

        # 2. 规划任务
        tasks = self.planner.plan(self.project_id, goal)

        # 3. Coordinator 发起第一条消息
        self.coordinator.start_project(self.project_id, goal, tasks)

        # 4. 初始状态同步
        self.sync_task_board()
        self.sync_workflow("research")

        while True:
            print("[Orchestrator][LOOP] checking pending messages...")
            done_any = False

            # =========================
            # Research
            # =========================
            research_msgs = self.messaging_hub.fetch_for_role("research_agent", self.project_id)
            for msg in research_msgs:
                task = self.task_queue.get_task(msg.task_id)

                print(f"[Orchestrator][DISPATCH] -> research_agent task_id={task.task_id}")

                self.task_queue.update_status(task.task_id, "running")
                self.sync_task_board()

                output = self.research_agent.run(
                    task,
                    msg,
                    self.state_manager,
                    self.artifact_store,
                )

                self.task_queue.update_status(task.task_id, "success")
                self.sync_task_board()

                self.messaging_hub.mark_processed(msg.message_id)

                self.coordinator.handoff(
                    project_id=self.project_id,
                    from_role="research_agent",
                    current_task_id=task.task_id,
                    payload=output["result"],
                    summary=output["summary"],
                    artifact_ids=output["artifact_ids"],
                )

                self.sync_workflow("content")
                done_any = True

            # =========================
            # Content
            # =========================
            content_msgs = self.messaging_hub.fetch_for_role("content_agent", self.project_id)
            for msg in content_msgs:
                task = self.task_queue.get_task(msg.task_id)

                print(f"[Orchestrator][DISPATCH] -> content_agent task_id={task.task_id}")

                self.task_queue.update_status(task.task_id, "running")
                self.sync_task_board()

                output = self.content_agent.run(
                    task,
                    msg,
                    self.state_manager,
                    self.artifact_store,
                )

                self.task_queue.update_status(task.task_id, "success")
                self.sync_task_board()

                self.messaging_hub.mark_processed(msg.message_id)

                self.coordinator.handoff(
                    project_id=self.project_id,
                    from_role="content_agent",
                    current_task_id=task.task_id,
                    payload=output["result"],
                    summary=output["summary"],
                    artifact_ids=output["artifact_ids"],
                )

                self.sync_workflow("ops")
                done_any = True

            # =========================
            # Ops
            # =========================
            ops_msgs = self.messaging_hub.fetch_for_role("ops_agent", self.project_id)
            for msg in ops_msgs:
                task = self.task_queue.get_task(msg.task_id)

                print(f"[Orchestrator][DISPATCH] -> ops_agent task_id={task.task_id}")

                self.task_queue.update_status(task.task_id, "running")
                self.sync_task_board()

                output = self.ops_agent.run(
                    task,
                    msg,
                    self.state_manager,
                    self.artifact_store,
                )

                final_status = "success" if output["status"] == "success" else "failed"
                self.task_queue.update_status(task.task_id, final_status)
                self.sync_task_board()

                self.messaging_hub.mark_processed(msg.message_id)

                self.coordinator.handoff(
                    project_id=self.project_id,
                    from_role="ops_agent",
                    current_task_id=task.task_id,
                    payload=output["result"],
                    summary=output["summary"],
                    artifact_ids=output["artifact_ids"],
                )

                self.sync_workflow("done")
                done_any = True

            # =========================
            # 结束判断
            # =========================
            state = self.state_manager.get(self.project_id)

            if state["status"] == "completed":
                print(f"[Orchestrator][DONE] project_id={self.project_id}")
                return state

            if not done_any:
                print(f"[Orchestrator][STOP] no more messages, project_id={self.project_id}")
                self.state_manager.update(
                    self.project_id,
                    status="failed",
                    next_action="流程停止：没有可处理消息",
                )
                return self.state_manager.get(self.project_id)
