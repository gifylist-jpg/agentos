class ModelSelector:
    def __init__(self):
        self.models = {
            "Claude": ClaudeModel(),
            "DeepSeek": DeepSeekModel(),
            # 以后可以扩展更多模型
        }

    def select_model(self, task_type):
        if task_type == "complex_task":
            return self.models["Claude"]
        elif task_type == "simple_task":
            return self.models["DeepSeek"]
        else:
            return self.models["Claude"]  # 默认返回 ClaudeModel
