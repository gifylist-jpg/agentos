from agentos.execution.openclaw_adapter import OpenClawAdapter

class ExecutionAdapter:
    def __init__(self):
        self.openclaw = OpenClawAdapter()

    def execute(self, request: dict) -> dict:
        payload = request.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("Execution request must contain a dict payload")

        execution_mode = payload.get("execution_mode", "auto")
        task_id = payload.get("task_id")

        logging.info(f"Task {task_id} started with execution mode: {execution_mode}")

        try:
            if execution_mode == "auto":
                result = self._handle_auto(payload)
            elif execution_mode == "manual":
                result = self._handle_manual_execution(payload)
            elif execution_mode == "retry":
                result = self._handle_retry(payload)
            elif execution_mode == "delayed":
                result = self._handle_delayed(payload)
            elif execution_mode == "scheduled":
                result = self._handle_scheduled(payload)
            else:
                result = {"status": "failed", "message": "Unknown execution mode"}

            normalized = self._normalize_execution_result(result)
            logging.info(f"Task {task_id} completed with result: {normalized}")
            return normalized

        except Exception as e:
            logging.error(f"Task {task_id} failed: {str(e)}")
            return {"status": "failed", "message": f"Execution failed: {str(e)}"}

    def _normalize_execution_result(self, result: dict) -> dict:
        if isinstance(result, dict) and "execution_result" in result and "status" in result:
            return result
        raw_status = result.get("status") if isinstance(result, dict) else None
        status_map = {
            "success": "SUCCESS",
            "failed": "FAILED",
            "rolled_back": "ROLLED_BACK",
        }
        return {
            "status": status_map.get(raw_status, "SUCCESS"),
            "execution_result": result,
        }

    def _handle_manual_execution(self, payload):
        return {
            "status": "failed",
            "message": "Manual execution requires human approval before running tools",
            "payload": payload,
        }

    def _handle_retry(self, payload):
        retries = payload.get("retries", 3)
        retry_interval = payload.get("retry_interval", 5)
        task_id = payload.get("task_id")

        for attempt in range(retries):
            try:
                return self.openclaw.execute(payload)
            except Exception as e:
                logging.error(f"Attempt {attempt+1} failed for task {task_id}: {str(e)}")
                if attempt < retries - 1:
                    logging.info(f"Retrying... Attempt {attempt + 2}")
                    time.sleep(retry_interval)
                else:
                    logging.info(f"Max retries reached, rolling back task {task_id}.")
                    return self.rollback_task(task_id)

    def _handle_delayed(self, payload):
        delay_time = payload.get("delay_time", 10)
        time.sleep(delay_time)
        return self.openclaw.execute(payload)

    def _handle_scheduled(self, payload):
        schedule_time = payload.get("schedule_time")
        current_time = time.time()
        time_diff = schedule_time - current_time
        if time_diff > 0:
            time.sleep(time_diff)
        return self.openclaw.execute(payload)

    def _handle_auto(self, payload):
        return self.openclaw.execute(payload)

    def rollback_task(self, task_id):
        logging.info(f"Rolling back task {task_id} to previous state.")
        return {"status": "rolled_back", "message": "Task rolled back to previous state"}
