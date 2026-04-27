import sys

sys.path.append('/home/gifylist/agentos_workspace')

from agentos_mvp.runtime.task_intake import normalize_task_input, validate_task_input
from agentos_mvp.core.decision import make_decision


def test_task_to_decision_integration_with_upgraded_contract():
    raw_task = {
        "task_id": "task_003",
        "goal": "生成完整方案",
        "product_name": "Test Product",
    }

    normalized, _, _ = normalize_task_input(raw_task)
    validate_task_input(normalized)

    result = make_decision(normalized)

    assert result["primary_hook"]
    assert len(result["hooks"]) >= 2
    assert len(result["selling_points"]) >= 2
    assert len(result["script_outline"]) >= 3
    assert len(result["storyboard"]) >= 3
    assert len(result["asset_plan"]) >= 1
    assert len(result["edit_plan"]) >= 3
    assert len(result["execution_plan"]) >= 3
