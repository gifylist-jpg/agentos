import pytest
from agentos_mvp.runtime.task_loader_v2 import load_tasks_from_json
from agentos_mvp.schemas.task_request import TaskRequest
import json

def test_load_single_task():
    task_data = {
        "task_id": "task_001",
        "goal": "Generate video",
        "product_name": "Product A",
        "target_platform": "YouTube",
        "target_duration": 30,
        "objective": "Increase views",  # Adding the 'objective' field
        "ai_generation_needed": True,
        "output_type": "Video"
    }
    with open("task.json", "w") as f:
        json.dump([task_data], f)

    tasks = load_tasks_from_json("task.json")
    assert len(tasks) == 1
    assert isinstance(tasks[0], TaskRequest)
    assert tasks[0].task_id == "task_001"

def test_missing_required_fields():
    task_data = {
        "task_id": "task_002",
        "goal": "Generate video",
        "product_name": "Product B",
    }

    with open("task.json", "w") as f:
        json.dump([task_data], f)

    print("Starting to load tasks from json with missing fields")
    
    # Ensure the ValueError is raised due to missing required fields
    with pytest.raises(ValueError, match="任务缺少字段"):
        load_tasks_from_json("task.json")
