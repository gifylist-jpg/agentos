from pprint import pprint

from services.task_service import TaskService


def main():
    service = TaskService()

    task = service.create_task(
        task_type="video_workflow",
        goal="为粉色包包生成一轮可测试视频素材",
        input_payload={
            "product_id": "p_bag_001",
            "product_name": "pink kawaii backpack",
            "target_market": "US",
            "target_audience": "teen girls and young women",
            "selling_points": [
                "cute design",
                "large capacity",
                "giftable",
            ],
        },
    )

    workflow_result = service.run_video_workflow(task)
    feedback_result = service.run_feedback_loop(task, workflow_result)

    print("\n================ WORKFLOW RESULT ================\n")
    pprint(workflow_result)

    print("\n================ FEEDBACK RESULT ================\n")
    pprint(feedback_result)


if __name__ == "__main__":
    main()
