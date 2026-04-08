from agentos.core.models.claude_model import ClaudeModel
from agentos.core.models.deepseek_model import DeepSeekModel


class ModelSelector:
    def __init__(self):
        self.models = {
            "Claude": ClaudeModel(),
            "DeepSeek": DeepSeekModel(),
        }

    def select_model(self, task_type):
        print(f"Selecting model for task_type: {task_type}")
        if task_type == "complex_task":
            return self.models["Claude"]
        elif task_type == "simple_task":
            return self.models["DeepSeek"]
        else:
            return self.models["Claude"]
