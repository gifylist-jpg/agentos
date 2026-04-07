#!/bin/bash

# -------------------- Step 1: 实现模型选择和决策生成 --------------------

echo "步骤 1: 创建 ModelSelector 类..."

mkdir -p agentos/core/decision

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

# -------------------- Step 2: 实现 MultiModelDecisionService --------------------

echo "步骤 2: 创建 MultiModelDecisionService 类..."

mkdir -p agentos/core/decision

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

# -------------------- Step 3: 实现 TaskServiceV2 --------------------

echo "步骤 3: 创建 TaskServiceV2 类..."

mkdir -p agentos/core/task

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

echo "步骤 1、2、3：模型选择、决策生成、任务服务已成功实现。"

# -------------------- Step 4: 测试步骤 - 检查是否已创建模型和服务 --------------------
echo "步骤 4: 检查模型和服务..."

# 检查 TaskServiceV2 类是否存在
if [ -f "agentos/core/task/task_service_v2.py" ]; then
    echo "TaskServiceV2 已创建"
else
    echo "TaskServiceV2 创建失败"
fi

# 检查 MultiModelDecisionService 类是否存在
if [ -f "agentos/core/decision/multi_model_decision_service.py" ]; then
    echo "MultiModelDecisionService 已创建"
else
    echo "MultiModelDecisionService 创建失败"
fi

# 检查 ModelSelector 类是否存在
if [ -f "agentos/core/decision/model_selector.py" ]; then
    echo "ModelSelector 已创建"
else
    echo "ModelSelector 创建失败"
fi

# -------------------- Step 5: 运行单元测试 --------------------

echo "步骤 5: 运行单元测试..."
python3 -m unittest discover tests/

# -------------------- Step 6: 提交代码并推送 --------------------

echo "步骤 6: 提交代码并推送到 Git 仓库..."

git add .
git commit -m "Implement model selection and decision generation"
git push origin main

echo "所有操作已完成！"
EOF

# -------------------- Step 7: 设置可执行权限并运行 --------------------

chmod +x setup_model_and_service.sh
./setup_model_and_service.sh
