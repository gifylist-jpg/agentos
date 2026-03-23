class MemoryManager:
    def __init__(self) -> None:
        self.latest = {}

    def save(self, key: str, value: dict) -> None:
        self.latest[key] = value

    def get(self, key: str) -> dict:
        return self.latest.get(key, {})
