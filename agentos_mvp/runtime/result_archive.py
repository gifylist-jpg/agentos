import os
import shutil


ACCEPTED_DIR = os.path.expanduser("~/agentos_workspace/videos/accepted")
os.makedirs(ACCEPTED_DIR, exist_ok=True)


def archive_accepted_video(video_path: str, task_id: str, execution_id: str) -> str:
    """
    把 accept 的视频归档到 accepted 目录。
    """
    if not video_path or not os.path.exists(video_path):
        raise FileNotFoundError(f"视频不存在，无法归档: {video_path}")

    filename = os.path.basename(video_path)
    archived_name = f"{task_id}__{execution_id}__{filename}"
    archived_path = os.path.join(ACCEPTED_DIR, archived_name)

    shutil.copy2(video_path, archived_path)
    return archived_path
