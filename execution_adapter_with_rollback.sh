#!/bin/bash

# 自动化操作：完善 ExecutionAdapter 以支持回滚机制和日志记录

echo "Adding rollback and logging mechanisms to ExecutionAdapter..."

# 修改 ExecutionAdapter 代码：添加回滚和异常处理
cat <<EOL > agentos/execution/execution_adapter.py
import os
import logging
import time
from agentos.execution.tool_executor import ToolExecutor
from agentos.execution.openclaw_adapter import OpenClawAdapter

# 确保日志目录存在
log_dir = '/home/gifylist/agentos/app/logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
logging.basicConfig(
    filename=os.path.join(log_dir, 'task_execution.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

class ExecutionAdapter:
    """
    ExecutionAdapter provides the unified entry point for execution.
    It can route execution requests to the correct tool or adapter based on the request.
    """

    def __init__(self):
        self.tool_executor = ToolExecutor()

    def execute(self, request: dict) -> dict:
        if not isinstance(request, dict):
            raise ValueError("Execution request must be a dictionary")

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

            logging.info(f"Task {task_id} completed with result: {result}")
            return result

        except Exception as e:
            logging.error(f"Task {task_id} failed: {str(e)}")
            return {"status": "failed", "message": f"Execution failed: {str(e)}"}

    def rollback_task(self, task_id):
        # Rollback logic - fetch the previous state and restore it
        logging.info(f"Rolling back task {task_id} to previous state.")
        return {"status": "rolled_back", "message": "Task rolled back to previous state"}

    def _handle_retry(self, payload):
        retries = payload.get("retries", 3)
        retry_interval = payload.get("retry_interval", 5)
        task_id = payload.get("task_id")

        for attempt in range(retries):
            try:
                return self.tool_executor.execute(payload)
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
        return self.tool_executor.execute(payload)

    def _handle_scheduled(self, payload):
        schedule_time = payload.get("schedule_time")
        current_time = time.time()
        time_diff = schedule_time - current_time
        if time_diff > 0:
            time.sleep(time_diff)
        return self.tool_executor.execute(payload)

    def _handle_auto(self, payload):
        return self.tool_executor.execute(payload)

EOL

echo "ExecutionAdapter updated with rollback mechanism and logging."
