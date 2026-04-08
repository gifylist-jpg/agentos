from datetime import datetime, UTC

class ApprovedDecision:
    def __init__(self, execution_mode, selected_candidate_id, timestamp=None, source='system'):
        self.execution_mode = execution_mode
        self.selected_candidate_id = selected_candidate_id
        self.timestamp = timestamp or datetime.now(UTC)
        self.source = source

    def __repr__(self):
        return f'<ApprovedDecision(execution_mode={self.execution_mode}, selected_candidate_id={self.selected_candidate_id})>'
