#!/bin/bash

# 1. 创建测试目录（如果不存在）
echo "检查测试目录..."
mkdir -p tests

# 2. 创建测试文件
echo "创建测试文件..."

cat > tests/test_task_service_v2.py << EOL
import unittest
from unittest.mock import MagicMock
from agentos.core.task.task_service_v2 import TaskServiceV2
from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision

class TestTaskServiceV2(unittest.TestCase):
    
    def test_task_service_v2(self):
        task_data = {'task_type': 'classification', 'task_data': 'test_data'}
        
        # 模拟 MultiModelDecisionService 的 generate_decision 方法
        mock_decision_service = MagicMock(MultiModelDecisionService)
        mock_decision_service.generate_decision.return_value = {'execution_mode': 'auto', 'selected_candidate_id': '123'}
        
        task_service = TaskServiceV2()
        task_service.decision_service = mock_decision_service
        
        # 执行任务处理
        result = task_service.process_task(task_data)
        
        # 验证返回的决策对象
        self.assertIsInstance(result, ApprovedDecision)
        self.assertEqual(result.execution_mode, 'auto')
        self.assertEqual(result.selected_candidate_id, '123')

if __name__ == '__main__':
    unittest.main()
EOL

echo "测试文件 test_task_service_v2.py 已创建"

# 3. 确保测试文件命名符合 unittest 规范
echo "检查测试文件命名..."
find tests/ -name "test_*.py"

# 4. 执行测试并输出结果
echo "运行单元测试..."
python3 -m unittest discover tests/

# 5. 输出结束信息
echo "所有操作已完成！"
