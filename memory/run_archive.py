import json
import re
import time
from pathlib import Path
from typing import Any


def _safe_name(text: str, max_len: int = 80) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-zA-Z0-9_\-\u4e00-\u9fff]", "", text)
    text = text[:max_len].strip("_")
    return text or "goal"


def create_run_dir(goal: str) -> Path:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    goal_name = _safe_name(goal)
    run_dir = Path("outputs") / f"{goal_name}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    with (run_dir / "goal.txt").open("w", encoding="utf-8") as f:
        f.write(goal)

    return run_dir


def save_json(run_dir: Path, filename: str, data: Any) -> Path:
    path = run_dir / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def save_text(run_dir: Path, filename: str, content: str) -> Path:
    path = run_dir / filename
    with path.open("w", encoding="utf-8") as f:
        f.write(content if isinstance(content, str) else str(content))
    return path
