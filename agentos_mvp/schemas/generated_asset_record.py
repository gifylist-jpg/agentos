from dataclasses import dataclass


@dataclass
class GeneratedAssetRecord:
    """
    人工生成结果回填对象：
    用于记录人工在即梦官网生成后带回系统的素材信息。
    """

    asset_id: str
    scene_id: str
    source: str
    uri: str
    status: str
    operator: str
