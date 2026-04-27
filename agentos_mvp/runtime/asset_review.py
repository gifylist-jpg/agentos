from typing import List

from schemas.generated_asset_record import GeneratedAssetRecord
from schemas.asset_review_result import AssetReviewResult


def review_assets(
    execution_id: str,
    assets: List[GeneratedAssetRecord],
) -> AssetReviewResult:
    """
    最小素材质量审核：
    当前阶段由人工逐条判断素材是否可进入合成。
    """

    approved_assets = []
    rejected_assets = []

    print("\n================ ASSET QUALITY REVIEW ================")

    for asset in assets:
        print(
            f"\nscene: {asset.scene_id}\n"
            f"asset_id: {asset.asset_id}\n"
            f"uri: {asset.uri}\n"
            f"source: {asset.source}\n"
        )

        decision = input("该素材是否通过质量审核？(y/n): ").strip().lower()

        asset_dict = {
            "asset_id": asset.asset_id,
            "scene_id": asset.scene_id,
            "source": asset.source,
            "uri": asset.uri,
            "status": asset.status,
            "operator": asset.operator,
        }

        if decision == "y":
            approved_assets.append(asset_dict)
        else:
            rejected_assets.append(asset_dict)

    review_note = input("\n📝 素材审核备注（可直接回车）:\n").strip()

    return AssetReviewResult(
        execution_id=execution_id,
        approved_assets=approved_assets,
        rejected_assets=rejected_assets,
        review_note=review_note,
    )
