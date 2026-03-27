from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict


@dataclass
class PublishRecord:
    publish_id: str
    task_id: str
    variant_id: str
    account_id: str
    product_id: str
    publish_mode: str  # organic | ads
    published_at: datetime
    platform: str = "tiktok"
    metadata: Dict = field(default_factory=dict)
