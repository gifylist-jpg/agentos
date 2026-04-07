#!/bin/bash

echo "正在创建 task_service_v2.py..."

# 创建目录
mkdir -p agentos/core/task

# 创建 task_service_v2.py 文件
cat > agentos/core/task/task_service_v2.py <<EOL
from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision

class TaskServiceV2:
    def __init__(self):
        self.decision_service = MultiModelDecisionService()

    def process_task(self, task_data):
        decision = self.decision_service.generate_decision(task_data)
        return ApprovedDecision(execution_mode=decision['execution_mode'], selected_candidate_id=decision['selected_candidate_id'])
EOL

echo "task_service_v2.py 文件创建完成！"
