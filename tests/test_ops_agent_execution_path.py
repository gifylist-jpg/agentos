from agentos.agents.ops_agent import OpsAgent


class DummyTask:
    task_id = "t1"
    project_id = "p1"


class DummyMessage:
    message_id = "m1"
    payload = {
        "parsed": {
            "execution_plan": ["stepA", "stepB"]
        }
    }


class DummyStateManager:
    def update_role_output(self, *args, **kwargs):
        pass

    def append_artifact(self, *args, **kwargs):
        pass


class DummyArtifactStore:
    def save(self, *args, **kwargs):
        return "artifact-1"


def test_ops_agent_execution_path():
    agent = OpsAgent()

    result = agent.run(
        task=DummyTask(),
        message=DummyMessage(),
        state_manager=DummyStateManager(),
        artifact_store=DummyArtifactStore()
    )

    assert result["status"] == "SUCCESS"
    assert "artifact_ids" in result
    assert len(result["artifact_ids"]) == 1

    assert "result" in result
    assert "execution_result" in result["result"]

    inner = result["result"]["execution_result"]
    assert inner["status"] == "success"
    assert "result" in inner
    assert "steps_completed" in inner["result"]
