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

    # Get director output
    director_output = _build_director_output(task, llm)
    # Get editor output
    editor_output = _build_editor_output(task, director_output, llm)

    # Return the required fields, ensuring the compatibility and default values.
    return {
        "video_angle": director_output.get("video_angle", ""),
        "hooks": director_output.get("hooks", []),
        "primary_hook": director_output.get("primary_hook", ""),
        "hook": director_output.get("hook", director_output.get("primary_hook", "")),  # Ensure compatibility with "hook"
        "selling_points": director_output.get("selling_points", []),
        "script_outline": director_output.get("script_outline", []),
        "script": director_output.get("script", ""),  # Retain "script" for compatibility
        "storyboard": director_output.get("storyboard", []),
        "asset_plan": editor_output.get("asset_plan", []),
        "edit_plan": editor_output.get("edit_plan", []),
        "execution_plan": editor_output.get("execution_plan", []),
    }
