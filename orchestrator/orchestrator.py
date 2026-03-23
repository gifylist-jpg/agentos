from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from core.safe_llm import SafeLLMCaller
from core.checkpoint import CheckpointManager

from planner.planner import Planner
from task_queue.task_queue import TaskQueue
from router.model_router import ModelRouter
from memory.memory_manager import MemoryManager
from memory.run_archive import create_run_dir, save_json, save_text
from memory.run_recovery import find_latest_recoverable_run
from supervisor.supervisor import Supervisor

from agents import research_agent, content_agent, marketing_agent, data_agent


AGENT_MAP = {
    "research": research_agent,
    "content": content_agent,
    "marketing": marketing_agent,
    "data": data_agent,
}


class Orchestrator:
    def __init__(self, tool_registry):
        self.planner = Planner()
        self.task_queue = TaskQueue()
        self.model_router = ModelRouter()
        self.memory = MemoryManager()
        self.supervisor = Supervisor()
        self.tool_registry = tool_registry

        self.safe_llm = SafeLLMCaller(self.model_router)
        self.run_dir = None
        self.checkpoint = None

    def _task_to_dict(self, task):
        return {
            "id": getattr(task, "id", None),
            "name": getattr(task, "name", None),
            "task": getattr(task, "task", None),
            "type": getattr(task, "type", None),
            "agent": getattr(task, "agent", None),
            "status": getattr(task, "status", None),
            "retries": getattr(task, "retries", 0),
            "depends_on": getattr(task, "depends_on", []),
            "result": getattr(task, "result", None),
            "model": getattr(task, "model", None),
            "model_name": getattr(task, "model_name", None),
            "token_usage": getattr(task, "token_usage", None),
        }

    def _build_summary(self, goal, completed_tasks, failed_tasks):
        lines = []
        lines.append("# Goal")
        lines.append(str(goal))
        lines.append("")

        lines.append("# Completed Tasks")
        if completed_tasks:
            for task in completed_tasks:
                lines.append(
                    f"- [{getattr(task, 'type', 'unknown')}] "
                    f"{getattr(task, 'name', '')} | agent={getattr(task, 'agent', '')} | "
                    f"model={getattr(task, 'model', '')} | tokens={getattr(task, 'token_usage', 0)}"
                )
        else:
            lines.append("- None")

        lines.append("")
        lines.append("# Failed Tasks")

        if failed_tasks:
            for task in failed_tasks:
                lines.append(
                    f"- [{getattr(task, 'type', 'unknown')}] "
                    f"{getattr(task, 'name', '')} | agent={getattr(task, 'agent', '')} | "
                    f"status={getattr(task, 'status', '')} | result={getattr(task, 'result', '')}"
                )
        else:
            lines.append("- None")

        return "\n".join(lines)

    def _restore_running_tasks_to_pending(self):
        running_tasks = getattr(self.task_queue, "running_tasks", [])
        pending_tasks = getattr(self.task_queue, "pending_tasks", [])

        while running_tasks:
            task = running_tasks.pop()
            task.status = "pending"
            pending_tasks.append(task)

    def run(self, goal):
        self.supervisor.reset()
        step_count = 0

        recoverable_run_dir = find_latest_recoverable_run("outputs")

        if recoverable_run_dir:
            self.run_dir = Path(recoverable_run_dir)
            print(f"[Recovery] Reusing previous run_dir: {self.run_dir}")
        else:
            self.run_dir = create_run_dir(goal)

        self.checkpoint = CheckpointManager(self.run_dir)

        checkpoint_data = self.checkpoint.load()
        restored_from_checkpoint = False

        if checkpoint_data:
            print("[Recovery] Found checkpoint, restoring...")
            if hasattr(self.task_queue, "load_from_dict"):
                self.task_queue.load_from_dict(checkpoint_data)
                restored_from_checkpoint = True

        history = self.memory.search_similar_goals(goal)
        memory_summary = self.memory.build_goal_memory_summary(goal)

        save_json(self.run_dir, "history.json", history)
        save_text(self.run_dir, "memory_summary.txt", memory_summary)

        if not restored_from_checkpoint:
            tasks = self.planner.plan(goal, history)
            save_json(self.run_dir, "plan.json", [self._task_to_dict(task) for task in tasks])

            self.supervisor.check_task_count(tasks)

            filtered_tasks = []
            for task in tasks:
                if not self.supervisor.is_duplicate_task(task):
                    filtered_tasks.append(task)

            save_json(
                self.run_dir,
                "filtered_tasks.json",
                [self._task_to_dict(task) for task in filtered_tasks],
            )

            self.task_queue.add_tasks(filtered_tasks)
            self.checkpoint.save(self.task_queue)

        try:
            while True:
                step_count += 1
                self.supervisor.check_step_limit(step_count)

                ready_tasks = self.task_queue.get_ready_tasks()
                if not ready_tasks:
                    break

                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = []

                    for task in ready_tasks:
                        self.task_queue.mark_running(task)
                        agent_module = AGENT_MAP[task.agent]

                        futures.append(
                            (
                                task,
                                executor.submit(
                                    agent_module.execute,
                                    task,
                                    self.safe_llm,
                                    self.tool_registry,
                                ),
                            )
                        )

                    for task, future in futures:
                        try:
                            result = future.result(timeout=60)

                            self.task_queue.mark_completed(
                                task,
                                result=result["result"],
                                model=result["model"],
                                token_usage=result["token_usage"],
                            )

                            if "model_name" in result:
                                task.model_name = result["model_name"]

                            self.supervisor.check_token_limit(task)
                            self.memory.store_task_result(goal, task)

                        except KeyboardInterrupt:
                            print("\n[Interrupt] KeyboardInterrupt received. Saving checkpoint before exit...")
                            self._restore_running_tasks_to_pending()
                            self.checkpoint.save(self.task_queue)
                            print("[Checkpoint] Saved successfully.")
                            raise

                        except Exception as e:
                            print(
                                f"[Task Error] {task.id} "
                                f"error_type={type(e).__name__} error={repr(e)}"
                            )

                            task.retries += 1
                            if self.supervisor.can_retry(task):
                                task.status = "pending"
                                self.task_queue.pending_tasks.append(task)
                            else:
                                self.task_queue.mark_failed(task, result=str(e))

                self.checkpoint.save(self.task_queue)

        except KeyboardInterrupt:
            print("[Exit] Run interrupted by user.")
            return getattr(self.task_queue, "completed_tasks", [])

        completed = getattr(self.task_queue, "completed_tasks", [])
        failed = getattr(self.task_queue, "failed_tasks", [])

        save_json(
            self.run_dir,
            "completed_tasks.json",
            [self._task_to_dict(task) for task in completed],
        )
        save_json(
            self.run_dir,
            "failed_tasks.json",
            [self._task_to_dict(task) for task in failed],
        )

        summary_text = self._build_summary(goal, completed, failed)
        save_text(self.run_dir, "summary.md", summary_text)

        return completed
