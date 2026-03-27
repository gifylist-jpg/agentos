from agents.performance_analysis_agent import PerformanceAnalysisAgent
from services.task_service import TaskService
from services.feedback_builder import BaselineReference
from storage.db import DatabaseManager
from models.task import Task
from core.publish_record import PublishRecord
from core.performance_snapshot import PerformanceSnapshot
from datetime import datetime


def main():
    db = DatabaseManager()
    service = TaskService(db=db)
    analysis_agent = PerformanceAnalysisAgent()

    task = Task(
        task_id="task_feedback_1",
        task_type="video_test",
        workflow_type="video_production",
        priority=0,
        context={},
        assigned_worker="",
    )

    publish_record = PublishRecord(
        publish_id="pub_1",
        task_id="task_feedback_1",
        variant_id="v_feedback_test",
        account_id="acc_feedback",
        product_id="prod_feedback",
        publish_mode="ads",
        published_at=datetime.now(),
        platform="tiktok",
        metadata={},
    )

    snapshots = [
        PerformanceSnapshot(
            snapshot_id="snap_1",
            publish_id="pub_1",
            captured_at=datetime.now(),
            age_hours=24,
            impressions=3000,
            clicks=240,
            ctr=0.08,
            cvr=0.015,
            watch_time=6.5,
            completion_rate=0.38,
            orders=2,
            traffic_split={"organic_ratio": 0.1, "ads_ratio": 0.9},
            source_metadata={},
        )
    ]

    baseline = BaselineReference(
        baseline_scope="ads",
        product_id="prod_feedback",
        account_id="acc_feedback",
        organic_baseline={"ctr": 0.03},
        ads_baseline={
            "ctr": 0.05,
            "watch_rate": 0.2,
            "avg_watch_time": 5.0,
            "views": 1000,
            "cvr": 0.01,
        },
        baseline_version="v1",
        metadata={},
    )

    feedback_result = service.run_feedback_loop(
        task=task,
        publish_record=publish_record,
        snapshots=snapshots,
        baseline=baseline,
        analysis_agent=analysis_agent,
    )

    print("\n=== FEEDBACK RESULT ===")
    print(feedback_result)


if __name__ == "__main__":
    main()
