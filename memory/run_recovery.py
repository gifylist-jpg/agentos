import json
import os


def find_latest_recoverable_run(outputs_dir="outputs"):
    if not os.path.exists(outputs_dir):
        return None

    run_dirs = []
    for name in os.listdir(outputs_dir):
        full_path = os.path.join(outputs_dir, name)
        if os.path.isdir(full_path):
            run_dirs.append(full_path)

    if not run_dirs:
        return None

    run_dirs.sort(key=lambda p: os.path.getmtime(p), reverse=True)

    for run_dir in run_dirs:
        checkpoint_path = os.path.join(run_dir, "checkpoint.json")
        if not os.path.exists(checkpoint_path):
            continue

        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            pending = data.get("pending", [])
            running = data.get("running", [])
            completed = data.get("completed", [])
            failed = data.get("failed", [])

            # 只要还有 pending 或 running，就认为可恢复
            if pending or running:
                return run_dir

            # 也可以放宽条件：有 completed 但没 summary，也可恢复
            summary_path = os.path.join(run_dir, "summary.md")
            if completed and not os.path.exists(summary_path):
                return run_dir

        except Exception:
            continue

    return NoneO
