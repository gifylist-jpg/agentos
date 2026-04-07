#!/bin/bash

# 确保在正确目录下执行
cd ~/agentos/app

# 检查文件夹是否存在，不存在则创建
mkdir -p agentos/core/task
mkdir -p agentos/core/decision

# 创建 task_service_v2.py 文件并写入内容
echo "
from agentos.core.decision.multi_model_decision_service import MultiModelDecisionService
from agentos.core.decision.approved_decision import ApprovedDecision

class TaskServiceV2:
    def __init__(self):
        self.decision_service = MultiModelDecisionService()

    def process_task(self, task_data):
        """ Main method to process a task and generate decision """
        decision = self.decision_service.generate_decision(task_data)
        return decision
" > agentos/core/task/task_service_v2.py

# 创建 multi_model_decision_service.py 文件并写入内容
echo "
class MultiModelDecisionService:
    def __init__(self):
        self.models = []  # List of models to be used
    
    def add_model(self, model):
        """ Add a model to the decision service """
        self.models.append(model)

    def generate_decision(self, task_data):
        """ Generate decision based on task data using multiple models """
        decisions = []
        for model in self.models:
            decision = model.evaluate(task_data)  # Assuming each model has an 'evaluate' method
            decisions.append(decision)
        
        return self.combine_decisions(decisions)
    
    def combine_decisions(self, decisions):
        """ Combine multiple model decisions into one final decision """
        return decisions[0] if decisions else None
" > agentos/core/decision/multi_model_decision_service.py

# 创建 approved_decision.py 文件并写入内容
echo "
from datetime import datetime

class ApprovedDecision:
    def __init__(self, execution_mode, selected_candidate_id, timestamp=None, source='system'):
        self.execution_mode = execution_mode
        self.selected_candidate_id = selected_candidate_id
        self.timestamp = timestamp or datetime.utcnow()
        self.source = source

    def __repr__(self):
        return f'<ApprovedDecision(execution_mode={self.execution_mode}, selected_candidate_id={self.selected_candidate_id})>'
" > agentos/core/decision/approved_decision.py

# 检查创建是否成功
echo "以下文件已创建并恢复内容:"
ls -R agentos/core/task
ls -R agentos/core/decision

echo "文件恢复完毕！"
