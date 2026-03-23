import json
from agentos.core.orchestrator import Orchestrator


def main():
    goal = "做一个适合 TikTok 美区的日系双肩包爆款视频"
    orchestrator = Orchestrator()
    result = orchestrator.run(goal)

    print("\n=== PROJECT STATE ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
