ROLE_REGISTRY = {
    "coordinator_agent": {
        "role_id": "coordinator_agent",
        "role_name": "Coordinator",
        "allowed_task_types": ["planning", "coordination"],
        "reports_to": "owner",
        "can_request_from": ["research_agent", "content_agent", "ops_agent", "data_agent"],
        "can_delegate_to": ["research_agent", "content_agent", "ops_agent", "data_agent"],
        "approval_required": False,
    },
    "research_agent": {
        "role_id": "research_agent",
        "role_name": "Research",
        "allowed_task_types": ["research"],
        "reports_to": "coordinator_agent",
        "can_request_from": [],
        "can_delegate_to": [],
        "approval_required": False,
    },
    "content_agent": {
        "role_id": "content_agent",
        "role_name": "Content",
        "allowed_task_types": ["content"],
        "reports_to": "coordinator_agent",
        "can_request_from": ["research_agent"],
        "can_delegate_to": ["ops_agent"],
        "approval_required": False,
    },
    "ops_agent": {
        "role_id": "ops_agent",
        "role_name": "Ops",
        "allowed_task_types": ["execution"],
        "reports_to": "coordinator_agent",
        "can_request_from": ["content_agent"],
        "can_delegate_to": [],
        "approval_required": False,
    },
    "data_agent": {
        "role_id": "data_agent",
        "role_name": "Data",
        "allowed_task_types": ["data"],
        "reports_to": "coordinator_agent",
        "can_request_from": [],
        "can_delegate_to": [],
        "approval_required": False,
    },
}


def get_role(role_id: str) -> dict:
    if role_id not in ROLE_REGISTRY:
        raise ValueError(f"Unknown role: {role_id}")
    return ROLE_REGISTRY[role_id]
