from agentos.core.decision.model_selector import ModelSelector

class MultiModelDecisionService:
    def __init__(self, model_selector: ModelSelector):
        self.model_selector = model_selector

    def generate_decision(self, task_data):
        task_type = task_data.get("task_type", "complex_task")
        model = self.model_selector.select_model(task_type)

        decision = model.evaluate(task_data)
        return decision
