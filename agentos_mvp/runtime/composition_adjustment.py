from typing import List, Dict


def adjust_clip_order(approved_assets: List[Dict]) -> List[Dict]:
    """
    最小合成前人工调整：
    允许人工重新排序 approved assets。
    当前阶段只调整顺序，不改其他结构。
    """

    print("\n================ COMPOSITION ADJUSTMENT ================")
    print("当前可用素材顺序：")

    for idx, asset in enumerate(approved_assets, start=1):
        print(f"{idx}. {asset['scene_id']} -> {asset['asset_id']} -> {asset['uri']}")

    raw = input(
        "\n请输入新的顺序编号（例如 2,1,3），直接回车则保持不变:\n"
    ).strip()

    if not raw:
        return approved_assets

    try:
        indices = [int(x.strip()) - 1 for x in raw.split(",")]
        reordered = [approved_assets[i] for i in indices]
        return reordered
    except Exception:
        print("⚠️ 顺序输入无效，保持原顺序。")
        return approved_assets


def replace_asset_uri(approved_assets: List[Dict]) -> List[Dict]:
    """
    最小素材替换：
    允许人工按 scene 替换素材 URI。
    """

    print("\n================ ASSET REPLACEMENT ================")

    for asset in approved_assets:
        new_uri = input(
            f"是否替换 {asset['scene_id']} 的素材 URI？当前为 {asset['uri']} （直接回车跳过）:\n"
        ).strip()

        if new_uri:
            asset["uri"] = new_uri

    return approved_assets
