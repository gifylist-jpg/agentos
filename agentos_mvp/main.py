from pprint import pprint
import sys

from schemas.generated_asset_record import GeneratedAssetRecord
from core.decision import make_decision
from review.review_policy import review_decision
from core.compiler import compile_to_execution_request
from runtime.manual_generation import build_manual_generation_package
from runtime.manual_fillback import (
    write_fillback_template,
    load_generated_assets,
    is_fillback_complete,
)
from runtime.asset_review import review_assets
from runtime.composition_adjustment import adjust_clip_order, replace_asset_uri
from runtime.composition import compose_video
from runtime.mock_execution import run_mock_execution
from feedback.feedback_loop import build_feedback
from runtime.human_view import show_decision
from runtime.task_intake import prepare_tasks


def get_scene_count(execution_result) -> int:
    if execution_result.scene_status:
        return len(execution_result.scene_status)

    if execution_result.future_execution_package is not None:
        future_plan = execution_result.future_execution_package.composition_plan
        if isinstance(future_plan, dict):
            return len(future_plan.get("clip_order", []))
        return len(getattr(future_plan, "clip_order", []))

    return 0


def run_single_task(task):
    print("\n==============================")
    print(f"🚀 开始任务: {task.task_id}")
    print("==============================")

    print("=== TaskRequest ===")
    print(task)

    decision = make_decision(task)

    print("\n=== ProductionDecision ===")
    pprint(decision)

    show_decision(decision)

    review_result = review_decision(decision)

    print("\n=== ReviewResult ===")
    pprint(review_result)

    if review_result.status != "approved":
        print(f"\n⏭ 任务 {task.task_id} 未通过审核，跳过执行。")
        return

    input("\n🚦 确认进入执行阶段？（回车继续）")

    execution_request = compile_to_execution_request(decision)

    manual_pkg = build_manual_generation_package(execution_request)
    write_fillback_template(manual_pkg)

    if not is_fillback_complete(execution_request.execution_id):
        print(f"\n请填写 runtime_data/manual_fillback_{execution_request.execution_id}.json 后重新运行")
        return

    generated_assets = load_generated_assets(execution_request.execution_id)

    asset_review_result = review_assets(
        execution_id=execution_request.execution_id,
        assets=generated_assets,
    )

    if asset_review_result.rejected_assets:
        print("存在未通过素材")
        return

    approved_assets = replace_asset_uri(asset_review_result.approved_assets)
    approved_assets = adjust_clip_order(approved_assets)

    adjusted_assets = [
        GeneratedAssetRecord(**item) for item in approved_assets
    ]

    composition_plan, composition_result = compose_video(
        execution_request,
        adjusted_assets,
    )

    print("\n=== CompositionPlan ===")
    pprint(composition_plan)

    print("\n=== CompositionResult ===")
    pprint(composition_result)

    executor_name = input(
        "\n🛠 选择执行器 (ffmpeg / future / ffmpeg_future): "
    ).strip().lower()

    execution_result = run_mock_execution(
        execution_request=execution_request,
        assets=adjusted_assets,
        executor_name=executor_name,
        composition_plan=composition_plan,
    )

    print("\n=== ExecutionResult ===")
    print(f"execution_id={execution_result.execution_id}")
    print(f"task_id={execution_result.task_id}")
    print(f"status={execution_result.status}")
    print(f"video_url={execution_result.video_url}")
    print(f"scene_count={get_scene_count(execution_result)}")
    print(f"has_future_package={execution_result.future_execution_package is not None}")

    feedback = build_feedback(execution_result)

    print("\n=== VideoTaskFeedback ===")
    pprint(feedback)

    if execution_result.status == "pending_manual_execution":
        from runtime.future_executor_human_readable import render_human_execution_guide

        print("\n=== 🎬 HUMAN EXECUTION GUIDE ===")
        guide = render_human_execution_guide(execution_result.future_execution_package)
        print(guide)

        print("\n=== Waiting State ===")
        print("请按 FutureExecutionPackage 执行剪辑")
        return


def main():
    task_json_path = sys.argv[1] if len(sys.argv) > 1 else "task.json"
    tasks = prepare_tasks(task_json_path)

    print(f"\n📦 本次确认进入主链的任务数: {len(tasks)}")

    for task in tasks:
        run_single_task(task)


if __name__ == "__main__":
    main()
