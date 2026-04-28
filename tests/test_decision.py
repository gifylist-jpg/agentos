import sys
sys.path.append('/home/gifylist/agentos_workspace')  # 确保 Python 能找到 agentos_mvp 模块

from typing import Any, Dict, List
from agentos_mvp.core.llm_adapter import LLMAdapter


def _ensure_list_of_str(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _ensure_list_of_dict(value: Any) -> List[Dict[str, Any]]:
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    return []


def _safe_parsed(result: Dict[str, Any]) -> Dict[str, Any]:
    parsed = result.get("parsed", {})
    if isinstance(parsed, dict):
        return parsed
    return {}


def _build_director_output(task: Dict[str, Any], llm: LLMAdapter) -> Dict[str, Any]:
    prompt = (
        f"goal={task.get('goal', '')}\n"
        f"product_name={task.get('product_name', '')}\n"
        "请输出 video_angle, hooks, selling_points, script_outline, storyboard"
    )

    result = llm.generate(task_type="director", prompt=prompt)
    parsed = _safe_parsed(result)

    hooks = _ensure_list_of_str(parsed.get("hooks"))
    primary_hook = hooks[0] if hooks else ""

    selling_points = _ensure_list_of_str(parsed.get("selling_points"))
    script_outline = _ensure_list_of_str(parsed.get("script_outline"))
    storyboard = _ensure_list_of_str(parsed.get("storyboard"))

    script = "；".join(script_outline) if script_outline else ""

    return {
        "video_angle": str(parsed.get("video_angle", "")).strip(),
        "hooks": hooks,
        "primary_hook": primary_hook,
        "hook": primary_hook,  # 添加 'hook' 字段
        "selling_points": selling_points,
        "script_outline": script_outline,
        "script": script,  # 兼容字段
        "storyboard": storyboard,
    }


def _build_editor_output(task: Dict[str, Any], director_output: Dict[str, Any], llm: LLMAdapter) -> Dict[str, Any]:
    prompt = (
        f"goal={task.get('goal', '')}\n"
        f"product_name={task.get('product_name', '')}\n"
        f"director_output={director_output}\n"
        "请输出 asset_plan, edit_plan, execution_plan"
    )

    result = llm.generate(task_type="editor", prompt=prompt)
    parsed = _safe_parsed(result)

    asset_plan = _ensure_list_of_dict(parsed.get("asset_plan"))
    edit_plan = _ensure_list_of_str(parsed.get("edit_plan"))
    execution_plan = _ensure_list_of_str(parsed.get("execution_plan"))

    return {
        "asset_plan": asset_plan,
        "edit_plan": edit_plan,
        "execution_plan": execution_plan,
    }


def make_decision(task: Dict[str, Any]) -> Dict[str, Any]:
    llm = LLMAdapter()

    director_output = _build_director_output(task, llm)
    editor_output = _build_editor_output(task, director_output, llm)

    return {
        "video_angle": director_output["video_angle"],
        "hooks": director_output["hooks"],
        "primary_hook": director_output["primary_hook"],
        "hook": director_output["hook"],  # 兼容字段
        "selling_points": director_output["selling_points"],
        "script_outline": director_output["script_outline"],
        "script": director_output["script"],  # 兼容字段
        "storyboard": director_output["storyboard"],
        "asset_plan": editor_output["asset_plan"],
        "edit_plan": editor_output["edit_plan"],
        "execution_plan": editor_output["execution_plan"],
    }
