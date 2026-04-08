class MultiModelDecisionService:
    def __init__(self, model_selector=None):
        from agentos.core.decision.model_selector import ModelSelector
        self.selector = model_selector or ModelSelector()

    def generate_decision(self, task_data):
        model = self.selector.select_model(task_data["task_type"])
        return model.evaluate(task_data)
