class FreezeGate:

    def evaluate(self, decision_record):

        if decision_record.freeze_candidate:
            return {
                "frozen": True,
                "reason": "FREEZE_TRIGGERED"
            }

        return {
            "frozen": False,
            "reason": None
        }
