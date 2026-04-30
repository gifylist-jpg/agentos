from typing import Any, Dict
from agentos_mvp.core.llm_adapter import LLMAdapter
from agentos_mvp.agents.director_agent import DirectorAgent
from agentos_mvp.agents.editor_agent import EditorAgent

def _build_director_output(task: Dict[str, Any], llm: LLMAdapter) -> Dict[str, Any]:
    prompt = (
        f"goal={task.get('goal', '')}\n"
        f"product_name={task.get('product_name', '')}\n"
        "请输出 video_angle, hooks, selling_points, script_outline, storyboard"
    )

    result = llm.generate(task_type="director", prompt=prompt)

    # 检查返回的结果是列表还是字典，确保数据格式正确
    if isinstance(result, list):
        if result:
            result = result[0]  # 取列表中的第一个元素
        else:
            result = {}  # 如果列表为空，返回一个空字典

    # 获取解析后的内容
    parsed = result.get("parsed", {}) if isinstance(result, dict) else {}

    hooks = parsed.get("hooks", ["默认钩子1", "默认钩子2"])  # 确保有钩子
    primary_hook = parsed.get("primary_hook", hooks[0])

    selling_points = parsed.get("selling_points", [])
    script_outline = parsed.get("script_outline", [])
    storyboard = parsed.get("storyboard", [])

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

    # 检查返回结果，确保是字典格式
    if isinstance(result, list):
        if result:
            result = result[0]
        else:
            result = {}

    parsed = result.get("parsed", {}) if isinstance(result, dict) else {}

    # 添加默认值
    asset_plan = parsed.get("asset_plan", [{"type": "default", "source": "unknown"}])  # 默认值
    edit_plan = parsed.get("edit_plan", ["默认编辑计划"])  # 添加默认值
    execution_plan = parsed.get("execution_plan", [])

    return {
        "asset_plan": asset_plan,
        "edit_plan": edit_plan,
        "execution_plan": execution_plan,
    }

def make_decision(task: Dict[str, Any], model_name: str = "deepseek") -> Dict[str, Any]:
    llm = LLMAdapter(model_name=model_name)

    director_output = _build_director_output(task, llm)
    editor_output = _build_editor_output(task, director_output, llm)

    primary_hook = director_output.get("primary_hook", "")
    hooks = director_output.get("hooks", [])
    hook = primary_hook if primary_hook else hooks[0] if hooks else "默认钩子"  # 兼容性

    return {
        "video_angle": director_output["video_angle"],
        "hooks": director_output["hooks"],
        "primary_hook": director_output["primary_hook"],
        "hook": hook,  # 兼容字段
        "selling_points": director_output["selling_points"],
        "script_outline": director_output["script_outline"],
        "script": director_output["script"],  # 兼容字段
        "storyboard": director_output["storyboard"],
        "asset_plan": editor_output["asset_plan"],
        "edit_plan": editor_output["edit_plan"],
        "execution_plan": editor_output["execution_plan"],
    }
