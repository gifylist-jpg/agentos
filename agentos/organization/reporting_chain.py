REPORTING_CHAIN = {
    "coordinator_agent": "owner",
    "research_agent": "coordinator_agent",
    "content_agent": "coordinator_agent",
    "ops_agent": "coordinator_agent",
    "data_agent": "coordinator_agent",
}


def get_manager(role_id: str) -> str | None:
    return REPORTING_CHAIN.get(role_id)
