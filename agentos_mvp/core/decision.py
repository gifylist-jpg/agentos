from typing import Any, Dict
from agentos_mvp.core.llm_adapter import LLMAdapter
from agentos_mvp.agents.director_agent import DirectorAgent
from agentos_mvp.agents.editor_agent import EditorAgent

def _build_director_output(task: Dict[str, Any], llm: LLMAdapter) -> Dict[str, Any]:
    director_agent = DirectorAgent()
    return director_agent.generate_director_output(task, llm)

def _build_editor_output(task: Dict[str, Any], director_output: Dict[str, Any], llm: LLMAdapter) -> Dict[str, Any]:
    editor_agent = EditorAgent()
    return editor_agent.generate_editor_output(task, director_output, llm)

def make_decision(task: Dict[str, Any]) -> Dict[str, Any]:
    llm = LLMAdapter()

    director_output = _build_director_output(task, llm)
    editor_output = _build_editor_output(task, director_output, llm)

    # 只保留决策相关的字段，去掉多余的兼容字段
    return {
        "video_angle": director_output["video_angle"],
        "hooks": director_output["hooks"],
        "primary_hook": director_output["primary_hook"],
        "selling_points": director_output["selling_points"],
        "script_outline": director_output["script_outline"],
        "script": director_output["script"],  # 保留script，作为兼容字段
        "storyboard": director_output["storyboard"],
        "asset_plan": editor_output["asset_plan"],
        "edit_plan": editor_output["edit_plan"],
        "execution_plan": editor_output["execution_plan"],
    }
