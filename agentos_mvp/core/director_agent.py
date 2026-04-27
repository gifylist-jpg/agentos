from agentos_mvp.core.llm_adapter import LLMAdapter

class DirectorAgent:

    def generate_director_output(self, task):
        llm = LLMAdapter()
        prompt = f"Task: {task['goal']}, Product: {task['product_name']}\nPlease generate video angle, hooks, script outline, and storyboard."

        result = llm.generate(task_type="director", prompt=prompt)
        parsed = result.get("parsed", {})

        # Extract the relevant fields from LLM response
        video_angle = parsed.get("video_angle", "")
        hooks = parsed.get("hooks", [])
        script_outline = parsed.get("script_outline", [])
        storyboard = parsed.get("storyboard", [])

        primary_hook = hooks[0] if hooks else ""

        return {
            "video_angle": video_angle,
            "hooks": hooks,
            "primary_hook": primary_hook,
            "script_outline": script_outline,
            "storyboard": storyboard,
        }
