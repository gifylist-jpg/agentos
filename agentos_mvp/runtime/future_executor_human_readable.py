def render_human_execution_guide(future_pkg) -> str:
    """
    把 FutureExecutionPackage（dataclass）转成“人可执行剪映步骤”
    """

    lines = []

    lines.append("剪映执行指南\n")

    lines.append(f"执行ID：{future_pkg.execution_id}")
    lines.append(f"任务ID：{future_pkg.task_id}")
    lines.append(f"执行器：{future_pkg.executor_name}")

    composition_plan = future_pkg.composition_plan
    clip_order = composition_plan.get("clip_order", [])
    assets = future_pkg.assets

    lines.append("\n1️⃣ 导入素材：")
    for asset in assets:
        lines.append(
            f"   - {asset['scene_id']} -> {asset['uri']} ({asset['source']})"
        )

    lines.append("\n2️⃣ 按顺序排列片段：")
    for idx, clip in enumerate(clip_order, 1):
        role = "content"
        if clip.get("emphasis") == "hook_emphasis":
            role = "hook"
        elif clip.get("emphasis") == "cta_emphasis":
            role = "cta"

        lines.append(
            f"   {idx}. {clip['scene_id']} | {clip['duration']}s | {role} | {clip['asset_uri']}"
        )

    lines.append("\n3️⃣ 全局剪辑参数：")
    lines.append(f"   - 字幕策略: {composition_plan.get('subtitle_strategy')}")
    lines.append(f"   - BGM风格: {composition_plan.get('bgm_style')}")
    lines.append(f"   - 转场风格: {composition_plan.get('transition_style')}")
    lines.append(f"   - CTA位置: {composition_plan.get('cta_position')}")

    lines.append("\n4️⃣ 操作步骤：")
    for step in future_pkg.instructions:
        lines.append(f"   - {step}")

    lines.append("\n5️⃣ 预期输出：")
    lines.append(f"   - {future_pkg.expected_output}")

    return "\n".join(lines)
