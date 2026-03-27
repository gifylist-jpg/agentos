from datetime import datetime, timedelta

from agents.performance_analysis_agent import PerformanceAnalysisAgent
from core.publish_record import PublishRecord
from core.performance_snapshot import PerformanceSnapshot
from models.task import Task
from services.feedback_builder import BaselineReference
from services.task_service import TaskService
from storage.db import DatabaseManager


def main():
    db = DatabaseManager()
    task_service = TaskService(db=db)
    analysis_agent = PerformanceAnalysisAgent()

    task = Task(
        task_id="task_structured_feedback_1",
        task_type="video_test",
        workflow_type="video_production",
        priority=0,
        context={},
        assigned_worker="",
    )

    published_at = datetime.utcnow() - timedelta(hours=24)

    publish_record = PublishRecord(
        publish_id="pub_1",
        task_id=task.task_id,
        variant_id="variant_1",
        account_id="acc_feedback",
        product_id="prod_feedback",
        publish_mode="ads",
        published_at=published_at,
        platform="tiktok",
        metadata={},
    )

    snapshots = [
        PerformanceSnapshot(
            snapshot_id="snap_1",
            publish_id="pub_1",
            captured_at=datetime.utcnow(),
            age_hours=24,
            impressions=3000,
            clicks=240,
            ctr=0.08,
            cvr=0.015,
            watch_time=6.5,
            completion_rate=0.38,
            orders=2,
            traffic_split={
                "organic_ratio": 0.1,
                "ads_ratio": 0.9,
            },
            source_metadata={},
        )
    ]

    baseline = BaselineReference(
        baseline_scope="ads",
        product_id="prod_feedback",
        account_id="acc_feedback",
        organic_baseline={"ctr": 0.03},
        ads_baseline={"ctr": 0.05},
        baseline_version="v1",
        metadata={},
    )

    feedback_result = task_service.run_feedback_loop(
        task=task,
        publish_record=publish_record,
        snapshots=snapshots,
        baseline=baseline,
        analysis_agent=analysis_agent,
    )

    print("\n=== STRUCTURED FEEDBACK RESULT ===")
    print(feedback_result)


if __name__ == "__main__":
    main()
