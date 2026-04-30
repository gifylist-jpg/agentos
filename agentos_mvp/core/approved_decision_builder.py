from typing import Dict, Any

class ApprovedDecisionBuilder:
    def build_decision(self, task_type: str, llm_response: Dict[str, Any]) -> Dict[str, Any]:
        decision = {
            "video_angle": llm_response.get("video_angle", ""),
            "hooks": llm_response.get("hooks", []),
            "primary_hook": llm_response.get("primary_hook", ""),
            "script": llm_response.get("script", ""),
        }
        return decision
