from orchestrator.orchestrator import Orchestrator
from tools.registry import ToolRegistry
from tools.web_search import web_search
from tools.file_system import save_text


def main():
    tool_registry = ToolRegistry()
    tool_registry.register_tool("web_search", web_search)
    tool_registry.register_tool("save_text", save_text)

    orchestrator = Orchestrator(tool_registry)

    goal = "Build TikTok marketing strategy"
    results = orchestrator.run(goal)

    print("\n=== COMPLETED TASKS ===")
    for task in orchestrator.task_queue.completed_tasks:
        print(f"{task.id} | {task.type} | {task.status} | model={task.model}")
        print(task.result)
        print("-" * 60)

    print("\n=== FAILED TASKS ===")
    for task in orchestrator.task_queue.failed_tasks:
        print(f"{task.id} | {task.type} | {task.status}")
        print(task.result)
        print("-" * 60)


if __name__ == "__main__":
    main()
