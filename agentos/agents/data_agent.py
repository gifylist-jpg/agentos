class DataAgent:
    role_id = "data_agent"

    def run(self, *args, **kwargs):
        return {
            "status": "not_enabled",
            "result": {},
            "artifact_ids": [],
            "summary": "data_agent 当前版本未启用",
        }
