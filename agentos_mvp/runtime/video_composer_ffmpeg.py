import os
import subprocess
from datetime import datetime
from typing import List

from schemas.generated_asset_record import GeneratedAssetRecord


OUTPUT_DIR = os.path.expanduser("~/agentos_workspace/videos")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _normalize_path(path: str) -> str:
    """
    统一路径格式并清洗异常字符：
    - Windows -> WSL: C:/x.mp4 -> /mnt/c/x.mp4
    - 去掉首尾空白
    - 清理非法 surrogate 字符
    """
    if not path:
        return path

    cleaned = path.strip()
    cleaned = cleaned.encode("utf-8", "ignore").decode("utf-8")
    cleaned = cleaned.replace("\\", "/")

    if len(cleaned) >= 3 and cleaned[1] == ":" and cleaned[2] == "/":
        drive = cleaned[0].lower()
        rest = cleaned[3:]
        return f"/mnt/{drive}/{rest}"

    return cleaned


def _build_output_path(execution_id: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(OUTPUT_DIR, f"{execution_id}_{ts}_final.mp4")


def compose_with_ffmpeg(execution_id: str, assets: List[GeneratedAssetRecord]) -> str | None:
    """
    最小 ffmpeg 合成：
    - 按 assets 当前顺序拼接
    - 自动转换 Windows 路径到 WSL 路径
    - 自动生成不覆盖的输出文件名
    """
    if not assets:
        print("❌ 没有可合成的素材")
        return None

    filelist_path = os.path.join(OUTPUT_DIR, "filelist.txt")

    with open(filelist_path, "w", encoding="utf-8") as f:
        for asset in assets:
            normalized = _normalize_path(asset.uri)
            print(f"[FFMPEG INPUT] raw={asset.uri} -> normalized={normalized}")
            f.write(f"file '{normalized}'\n")

    output_path = _build_output_path(execution_id)

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        filelist_path,
        "-c",
        "copy",
        output_path,
    ]

    print("[FFMPEG CMD]", " ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("❌ ffmpeg 合成失败")
        return None

    return output_path
