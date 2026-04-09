#!/bin/bash

# 设定项目的根目录路径
PROJECT_DIR=$(pwd)

# 目标文件路径
EXECUTION_ADAPTER_FILE="$PROJECT_DIR/agentos/execution/execution_adapter.py"
TASK_SERVICE_FILE="$PROJECT_DIR/agentos/core/task/task_service_v2.py"
OPS_AGENT_FILE="$PROJECT_DIR/agentos/agents/ops_agent.py"

# 检查执行路径是否存在
if [[ ! -f "$EXECUTION_ADAPTER_FILE" || ! -f "$TASK_SERVICE_FILE" || ! -f "$OPS_AGENT_FILE" ]]; then
  echo "Error: One or more files are missing!"
  exit 1
fi

echo "Expanding ExecutionAdapter to support new execution modes..."

# 在 ExecutionAdapter 中增加新的执行模式支持
cat >> "$EXECUTION_ADAPTER_FILE" <<EOF

    def _handle_retry(self, payload):
        retries = payload.get("retries", 3)
        retry_interval = payload.get("retry_interval", 5)
        for attempt in range(retries):
            try:
                return self.tool_executor.execute(payload)
            except Exception as e:
                if attempt < retries - 1:
                    print(f"Retrying... Attempt {attempt + 1}")
                    time.sleep(retry_interval)
                else:
                    raise e

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
EOF

echo "Added retry, delayed, and scheduled execution modes to ExecutionAdapter."

# 在 TaskServiceV2 中添加执行模式
cat >> "$TASK_SERVICE_FILE" <<EOF

# Ensure that ExecutionAdapter is called with the right execution mode
task_request = {
    "payload": {
        "execution_mode": "retry",  # Could be retry, delayed, scheduled
        "retries": 3,
        "retry_interval": 5,
    }
}
execution_adapter.execute(task_request)
EOF

echo "Updated TaskServiceV2 to support new execution modes."

# 在 OpsAgent 中添加执行模式支持
cat >> "$OPS_AGENT_FILE" <<EOF

# Ensure that OpsAgent passes the correct execution mode to ExecutionAdapter
ops_agent_request = {
    "payload": {
        "execution_mode": "delayed",  # Could be retry, delayed, scheduled
        "delay_time": 10,
    }
}
execution_adapter.execute(ops_agent_request)
EOF

echo "Updated OpsAgent to support new execution modes."

echo "Execution modes expanded and implemented. Please check the code for the changes."

# 提示修改已完成
echo "Please review and test the changes to ensure compatibility with your system."
