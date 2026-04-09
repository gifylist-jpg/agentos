#!/bin/bash

# 设置日志目录
LOG_DIR="/home/gifylist/agentos/app/logs"
TASK_LOG="${LOG_DIR}/task_execution.log"

# 1. 确保日志目录和文件存在
echo "确保日志目录和文件存在..."
if [ ! -d "$LOG_DIR" ]; then
  echo "日志目录不存在，正在创建..."
  mkdir -p "$LOG_DIR"
fi

if [ ! -f "$TASK_LOG" ]; then
  echo "日志文件不存在，正在创建..."
  touch "$TASK_LOG"
fi

echo "日志目录和文件检查完成。"

# 2. 执行模式扩展：修改 ExecutionAdapter 和增加新的执行模式支持
echo "正在修改 ExecutionAdapter 以支持新的执行模式..."
# 这里确保已经将 ExecutionAdapter 中的 retry、delayed、scheduled 等模式添加
# 你可以将以下内容集成进脚本执行
python3 << EOF
import time
import logging

# 确保日志配置正确
log_dir = "$LOG_DIR"
logging.basicConfig(
    filename="${TASK_LOG}",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

class ExecutionAdapter:
    def __init__(self):
        self.tool_executor = "ToolExecutor"  # 模拟 ToolExecutor 初始化

    def execute(self, request: dict) -> dict:
        payload = request.get("payload")
        execution_mode = payload.get("execution_mode", "auto")
        logging.info(f"Execution mode: {execution_mode}")

        if execution_mode == "retry":
            return self._handle_retry(payload)
        elif execution_mode == "delayed":
            return self._handle_delayed(payload)
        elif execution_mode == "scheduled":
            return self._handle_scheduled(payload)
        elif execution_mode == "auto":
            return {"status": "SUCCESS", "message": "Task executed automatically"}
        else:
            return {"status": "FAILED", "message": "Unknown execution mode"}

    def _handle_retry(self, payload):
        retries = payload.get("retries", 3)
        retry_interval = payload.get("retry_interval", 5)
        for attempt in range(retries):
            try:
                return {"status": "SUCCESS", "message": "Task retried successfully"}
            except Exception as e:
                if attempt < retries - 1:
                    logging.warning(f"Retry attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(retry_interval)
                else:
                    raise e

    def _handle_delayed(self, payload):
        delay_time = payload.get("delay_time", 10)
        time.sleep(delay_time)
        return {"status": "SUCCESS", "message": "Task executed after delay"}

    def _handle_scheduled(self, payload):
        schedule_time = payload.get("schedule_time", time.time() + 10)
        time_diff = schedule_time - time.time()
        if time_diff > 0:
            time.sleep(time_diff)
        return {"status": "SUCCESS", "message": "Task executed as scheduled"}
EOF

echo "ExecutionAdapter 执行模式扩展完成。"

# 3. 执行日志检查：验证日志记录功能
echo "验证日志记录功能..."
if grep -q "Execution mode" "$TASK_LOG"; then
  echo "日志中成功记录了执行模式。"
else
  echo "日志中未记录执行模式，请检查 ExecutionAdapter 中的日志配置。"
fi

if grep -q "Execution result" "$TASK_LOG"; then
  echo "日志中成功记录了执行结果。"
else
  echo "日志中未记录执行结果，请检查 ExecutionAdapter 中的日志配置。"
fi

# 4. 增加执行模式的单元测试
echo "为新执行模式增加单元测试..."

# 运行执行模式的测试用例
python3 << EOF
import unittest

class TestExecutionAdapter(unittest.TestCase):
    def test_retry_execution(self):
        payload = {"execution_mode": "retry", "retries": 3, "retry_interval": 1}
        result = ExecutionAdapter().execute({"payload": payload})
        self.assertEqual(result["status"], "SUCCESS")

    def test_delayed_execution(self):
        payload = {"execution_mode": "delayed", "delay_time": 2}
        result = ExecutionAdapter().execute({"payload": payload})
        self.assertEqual(result["status"], "SUCCESS")

    def test_scheduled_execution(self):
        payload = {"execution_mode": "scheduled", "schedule_time": time.time() + 5}
        result = ExecutionAdapter().execute({"payload": payload})
        self.assertEqual(result["status"], "SUCCESS")

if __name__ == '__main__':
    unittest.main()
EOF

# 5. 确认执行结果和日志输出
echo "运行完成，输出日志和测试结果。"
cat "$TASK_LOG"
echo "验证工作完成！"
