from dataclasses import dataclass
from typing import Dict


@dataclass
class DecisionRecord:
    task_id: str
    variant_id: str

    action: str
    decision_type: str
    confidence: str

    review_required: bool
    freeze_candidate: bool
    memory_admission_candidate: bool

    diagnostics: Dict
    metadata: Dict

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "variant_id": self.variant_id,
            "action": self.action,
            "decision_type": self.decision_type,
            "confidence": self.confidence,
            "review_required": self.review_required,
            "freeze_candidate": self.freeze_candidate,
            "memory_admission_candidate": self.memory_admission_candidate,
            "diagnostics": self.diagnostics,
            "metadata": self.metadata,
        }
