class ReviewGate:

    def evaluate(self, decision_record):

        if decision_record.review_required:
            return {
                "blocked": True,
                "reason": "REVIEW_REQUIRED"
            }

        return {
            "blocked": False,
            "reason": None
        }
