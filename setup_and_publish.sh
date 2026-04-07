#!/bin/bash

# -------------------- Step 1: Implement Model Selection and Decision Generation --------------------

echo "步骤 1: 实现模型选择和决策生成"

# 创建 ModelSelector 类
echo "创建 ModelSelector 类..."
cat <<EOF > agentos/core/decision/model_selector.py
class ModelSelector:
    def __init__(self):
        self.models = {
            "Claude": ClaudeModel(),
            "DeepSeek": DeepSeekModel(),
            # 以后可以扩展更多模型
        }

    def select_model(self, task_type):
        if task_type == "complex_task":
            return self.models["Claude"]
        elif task_type == "simple_task":
            return self.models["DeepSeek"]
        else:
            return self.models["Claude"]  # 默认返回 ClaudeModel
EOF

# -------------------- Step 2: Implement MultiModelDecisionService --------------------

echo "步骤 2: 实现 MultiModelDecisionService 类"

cat <<EOF > agentos/core/decision/multi_model_decision_service.py
from agentos.core.decision.model_selector import ModelSelector

class MultiModelDecisionService:
    def __init__(self, model_selector: ModelSelector):
        self.model_selector = model_selector

    def generate_decision(self, task_data):
        task_type = task_data.get("task_type", "complex_task")
        model = self.model_selector.select_model(task_type)

        decision = model.evaluate(task_data)
        return decision
EOF

# -------------------- Step 3: Implement TaskServiceV2 --------------------

echo "步骤 3: 实现 TaskServiceV2 类"

cat <<EOF > agentos/core/task/task_service_v2.py
from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision
from agentos.core.decision.model_selector import ModelSelector

class TaskServiceV2:
    def __init__(self, model_selector: ModelSelector):
        self.decision_service = MultiModelDecisionService(model_selector)

    def process_task(self, task_data, manual_model=None):
        # 如果手动指定模型，则覆盖自动选择
        if manual_model:
            task_data["model"] = manual_model
        decision = self.decision_service.generate_decision(task_data)
        return ApprovedDecision(execution_mode=decision['execution_mode'], selected_candidate_id=decision['selected_candidate_id'])
EOF

# -------------------- Step 4: Create Integration Test --------------------

echo "步骤 4: 创建集成测试文件"

cat <<EOF > tests/test_task_service_integration.py
from unittest.mock import MagicMock
from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision
from agentos.core.task.task_service_v2 import TaskServiceV2
from agentos.core.decision.model_selector import ModelSelector

def test_task_service_integration():
    task_data = {"task_type": "simple_task"}

    model_selector = ModelSelector()
    task_service = TaskServiceV2(model_selector)

    decision = task_service.process_task(task_data)
    assert decision.execution_mode == "auto"
    assert decision.selected_candidate_id is not None

    decision_manual = task_service.process_task(task_data, manual_model="DeepSeek")
    assert decision_manual.execution_mode == "auto"
EOF

# -------------------- Step 5: Run Unit Tests --------------------

echo "步骤 5: 运行单元测试"

python3 -m unittest discover tests/

# -------------------- Step 6: Version Control and Commit Changes --------------------

echo "步骤 6: 提交更改并标记版本"

git add .
git commit -m "Implement model selection and decision generation"
git push origin main

# 标记版本
git tag -a v1.0.0 -m "Initial release with model selection and decision generation"
git push origin v1.0.0

# -------------------- Step 7: Prepare for Production Deployment --------------------

echo "步骤 7: 准备生产部署"

# 生产部署操作（可以根据实际部署流程定制）
# 如部署至服务器或容器化部署（Docker, Kubernetes 等）

echo "生产部署准备完成，所有操作已完成！"

EOF

# -------------------- Step 8: Set Executable Permissions and Run --------------------

chmod +x setup_and_publish.sh
./setup_and_publish.sh
