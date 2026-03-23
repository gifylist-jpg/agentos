class OpenClawAdapter:
    def run(self, payload: dict) -> dict:
        return {
            "status": "success",
            "result": {
                "executed_action": payload.get("action"),
                "steps_completed": payload.get("steps", []),
                "note": "当前为模拟 OpenClaw 执行，后续替换成真实本地调用",
            },
            "metrics": {
                "latency": 1.2,
            },
            "artifacts": [],
        }
