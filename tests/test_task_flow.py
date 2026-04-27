import sys
sys.path.append('/home/gifylist/agentos_workspace')

from agentos_mvp.runtime.task_intake import normalize_task_input, validate_task_input
from agentos_mvp.core.decision import make_decision

def test_task_flow():
    raw_task = {
        "task_id": "task_004",
        "goal": "生成视频广告",
        "product_name": "New Product",
    }

    normalized, _, _ = normalize_task_input(raw_task)
    validate_task_input(normalized)

    result = make_decision(normalized)

    # 验证决策输出的准确性
    assert isinstance(result["asset_plan"], list)
    assert len(result["asset_plan"]) > 0
    assert isinstance(result["edit_plan"], list)
    assert len(result["edit_plan"]) > 0
    assert isinstance(result["execution_plan"], list)
    assert len(result["execution_plan"]) > 0
