class ExecutionFlowRecord:
    def __init__(self):
        self.flow = ["detect", "alert", "policy", "interpret"]
        self.current_step = None

    def set_step(self, step):
        if step not in self.flow:
            raise Exception(f"INVALID_STEP: {step}")
        self.current_step = step
