from typing import Dict, Any
from agentos_mvp.core.llm_adapter import LLMAdapter  # 导入 LLMAdapter

class DirectorAgent:
    def generate_director_output(self, task, llm: LLMAdapter):
        prompt = self._build_prompt(task)
        result = llm.generate(task_type="director", prompt=prompt)
        return self._parse_result(result)

    def _build_prompt(self, task) -> str:
        return f"Goal: {task['goal']}\nProduct: {task['product_name']}\nContent Planning"

    def _parse_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        parsed = result.get("parsed", {})

        # Debugging output to check what's being returned from LLM
        print(f"Debugging parsed result: {parsed}")

        hooks = parsed.get("hooks", [])
        primary_hook = parsed.get("primary_hook", hooks[0] if hooks else "default hook")

        return {
            "video_angle": parsed.get("video_angle", ""),
            "hooks": hooks,
            "primary_hook": primary_hook,  # Ensure primary_hook is handled
            "selling_points": parsed.get("selling_points", []),
            "script_outline": parsed.get("script_outline", []),
            "script": "；".join(parsed.get("script_outline", [])),
            "storyboard": parsed.get("storyboard", []),
        }
