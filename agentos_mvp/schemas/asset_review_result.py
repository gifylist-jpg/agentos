from dataclasses import dataclass
from typing import List, Dict


@dataclass
class AssetReviewResult:
    """
    最小素材审核结果：
    表示人工对回填素材做质量审核后的结果。
    """

    execution_id: str
    approved_assets: List[Dict]
    rejected_assets: List[Dict]
    review_note: str
