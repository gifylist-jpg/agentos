#!/bin/bash

# Step 1: 创建基础框架文件

echo "创建 TaskRequest 类文件..."
cat > agentos/core/task/task_request.py << EOL
class TaskRequest:
    def __init__(self, task_type, task_data, risk_level="medium"):
        self.task_type = task_type  # 任务类型
        self.task_data = task_data  # 任务数据
        self.risk_level = risk_level  # 风险级别（默认：medium）
EOL

echo "创建 MultiModelDecisionService 类文件..."
cat > agentos/core/decision/multi_model_decision_service.py << EOL
class MultiModelDecisionService:
    def __init__(self):
        self.models = []  # 需要的模型列表

    def add_model(self, model):
        self.models.append(model)

    def generate_decision(self, task_data):
        decisions = []
        for model in self.models:
            decision = model.evaluate(task_data)  # 调用模型的 evaluate 方法
            decisions.append(decision)
        return self.combine_decisions(decisions)

    def combine_decisions(self, decisions):
        # 这里简单地返回第一个决策，未来可以做更复杂的决策融合逻辑
        return decisions[0] if decisions else None
EOL

echo "创建 ApprovedDecision 类文件..."
cat > agentos/core/decision/approved_decision.py << EOL
from datetime import datetime

class ApprovedDecision:
    def __init__(self, execution_mode, selected_candidate_id, timestamp=None, source='system'):
        self.execution_mode = execution_mode
        self.selected_candidate_id = selected_candidate_id
        self.timestamp = timestamp or datetime.utcnow()
        self.source = source

    def __repr__(self):
        return f'<ApprovedDecision(execution_mode={self.execution_mode}, selected_candidate_id={self.selected_candidate_id})>'
EOL

echo "创建 TaskServiceV2 类文件..."
cat > agentos/core/task/task_service_v2.py << EOL
from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision

class TaskServiceV2:
    def __init__(self):
        self.decision_service = MultiModelDecisionService()

    def process_task(self, task_data):
        decision = self.decision_service.generate_decision(task_data)
        return ApprovedDecision(execution_mode=decision['execution_mode'], selected_candidate_id=decision['selected_candidate_id'])
EOL

# Step 2: 创建模拟模型类并实现 evaluate 方法

echo "创建 ClaudeModel 模拟模型类..."
cat > agentos/core/models/claude_model.py << EOL
class ClaudeModel:
    def evaluate(self, task_data):
        # 模拟决策生成逻辑
        return {'execution_mode': 'auto', 'selected_candidate_id': '123'}
EOL

echo "创建 DeepSeekModel 模拟模型类..."
cat > agentos/core/models/deepseek_model.py << EOL
class DeepSeekModel:
    def evaluate(self, task_data):
        # 模拟决策生成逻辑
        return {'execution_mode': 'manual', 'selected_candidate_id': '456'}
EOL

# Step 3: 编写并执行单元测试代码

echo "编写并执行单元测试..."
cat > test_task_service_v2.py << EOL
from unittest.mock import MagicMock
from agentos.core.task.task_service_v2 import TaskServiceV2
from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision

def test_task_service_v2():
    task_data = {'task_type': 'classification', 'task_data': 'test_data'}
    
    # 模拟 MultiModelDecisionService 的 generate_decision 方法
    mock_decision_service = MagicMock(MultiModelDecisionService)
    mock_decision_service.generate_decision.return_value = {'execution_mode': 'auto', 'selected_candidate_id': '123'}
    
    task_service = TaskServiceV2()
    task_service.decision_service = mock_decision_service
    
    # 执行任务处理
    result = task_service.process_task(task_data)
    
    # 验证返回的决策对象
    assert isinstance(result, ApprovedDecision)
    assert result.execution_mode == 'auto'
    assert result.selected_candidate_id == '123'

test_task_service_v2()
EOL

# Step 4: 运行单元测试

echo "运行单元测试..."
python3 -m unittest test_task_service_v2.py

echo "所有操作已完成！"
