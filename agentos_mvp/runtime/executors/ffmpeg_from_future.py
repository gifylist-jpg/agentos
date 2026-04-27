import subprocess
from pathlib import Path


FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]


def _run_cmd(cmd):
    print("[FFMPEG CMD]", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[FFMPEG ERROR]", result.stderr)
        raise RuntimeError("ffmpeg 执行失败")
    return result


def _escape_drawtext(text: str) -> str:
    return (
        text.replace("\\", r"\\")
        .replace(":", r"\:")
        .replace("'", r"\'")
        .replace(",", r"\,")
        .replace("[", r"\[")
        .replace("]", r"\]")
        .replace("%", r"\%")
    )


def _pick_font():
    for font_path in FONT_CANDIDATES:
        if Path(font_path).exists():
            return font_path
    raise FileNotFoundError("没有找到可用字体，请先安装 DejaVuSans 或 LiberationSans")


def _get_plan_value(plan, key, default=None):
    if isinstance(plan, dict):
        return plan.get(key, default)
    return getattr(plan, key, default)


def run_ffmpeg_from_future(future_package):
    """
    Execution OS v3：
    - 按 clip_order 顺序
    - 按 duration 裁剪
    - 从 composition_plan 读取 CTA 文案
    - 在最后一个片段最后2秒叠 CTA
    - 再拼接输出
    """

    execution_id = future_package.execution_id
    composition_plan = future_package.composition_plan
    clip_order = _get_plan_value(composition_plan, "clip_order", [])

    # 保留英文 CTA，避免中文字体问题
    cta_text = _get_plan_value(composition_plan, "cta_text", "Shop now")
    cta_last_seconds = _get_plan_value(composition_plan, "cta_last_seconds", 2)

    font_path = _pick_font()
    temp_dir = Path("/tmp/agentos_ffmpeg")
    temp_dir.mkdir(parents=True, exist_ok=True)

    cut_files = []

    for i, clip in enumerate(clip_order):
        input_path = clip["asset_uri"].replace("C:/", "/mnt/c/")
        duration = clip.get("duration", 3)

        output_path = temp_dir / f"{execution_id}_clip_{i}.mp4"
        is_last_clip = (i == len(clip_order) - 1)

        base_cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-t", str(duration),
        ]

        if is_last_clip:
            escaped_cta = _escape_drawtext(cta_text)

            drawtext_filter = (
                "drawtext="
                f"fontfile='{font_path}':"
                f"text='{escaped_cta}':"
                "fontcolor=white:"
                "fontsize=42:"
                "box=1:"
                "boxcolor=black@0.55:"
                "boxborderw=12:"
                "x=(w-text_w)/2:"
                "y=h-(text_h*2.8):"
                f"enable='gte(t,{max(duration - cta_last_seconds, 0)})'"
            )

            cmd = base_cmd + [
                "-vf", drawtext_filter,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                str(output_path),
            ]
        else:
            cmd = base_cmd + [
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                str(output_path),
            ]

        print(f"[CUT] {input_path} -> {output_path} ({duration}s)")
        _run_cmd(cmd)
        cut_files.append(output_path)

    list_file = temp_dir / f"{execution_id}_filelist.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for file in cut_files:
            f.write(f"file '{file}'\n")

    final_output = temp_dir / f"{execution_id}_final_v3.mp4"
    concat_cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(final_output),
    ]

    print(f"[CONCAT] -> {final_output}")
    _run_cmd(concat_cmd)

    return str(final_output)
