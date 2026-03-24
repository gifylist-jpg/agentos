class CostManager:
    def __init__(self) -> None:
        self.total_cost = 0.0
        self.total_tokens = 0

    def record(self, cost: float = 0.0, tokens: int = 0) -> None:
        self.total_cost += cost
        self.total_tokens += tokens
