import json
from pathlib import Path
from typing import List

from schemas.generated_asset_record import GeneratedAssetRecord


BASE_DIR = Path("runtime_data")
BASE_DIR.mkdir(exist_ok=True)


def _fillback_path(execution_id: str) -> Path:
    return BASE_DIR / f"manual_fillback_{execution_id}.json"


def _existing_assets_path(execution_id: str) -> Path:
    return BASE_DIR / f"existing_assets_{execution_id}.json"


def write_fillback_template(manual_pkg) -> None:
    """
    为当前 execution_id 写独立 fillback 模板
    """

    path = _fillback_path(manual_pkg.execution_id)

    template = [
        {
            "scene_id": task["scene_id"],
            "uri": "",
        }
        for task in manual_pkg.generation_tasks
        if task["asset_type"] == "ai_video"
    ]

    if not path.exists():
        path.write_text(
            json.dumps(template, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def is_fillback_complete(execution_id: str) -> bool:
    path = _fillback_path(execution_id)

    if not path.exists():
        return False

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False

    if not isinstance(data, list):
        return False

    for item in data:
        if not item.get("scene_id") or not item.get("uri"):
            return False

    return True


def _infer_source_from_uri(uri: str) -> str:
    u = (uri or "").lower()

    if any(key in u for key in ["real_shot", "real_", "footage", "existing"]):
        return "human_real_footage"

    return "jimeng_manual"


def _load_json_list(path: Path) -> list:
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    return data


def load_generated_assets(execution_id: str) -> List[GeneratedAssetRecord]:
    """
    按 execution_id 加载资产
    """

    ai_data = _load_json_list(_fillback_path(execution_id))
    existing_data = _load_json_list(_existing_assets_path(execution_id))

    merged = []

    for item in existing_data:
        uri = item["uri"]
        merged.append(
            GeneratedAssetRecord(
                asset_id=f"manual_asset_{item['scene_id']}",
                scene_id=item["scene_id"],
                source=_infer_source_from_uri(uri),
                uri=uri,
                status="success",
                operator="human",
            )
        )

    for item in ai_data:
        uri = item["uri"]
        merged.append(
            GeneratedAssetRecord(
                asset_id=f"manual_asset_{item['scene_id']}",
                scene_id=item["scene_id"],
                source=_infer_source_from_uri(uri),
                uri=uri,
                status="success",
                operator="human",
            )
        )

    return merged
