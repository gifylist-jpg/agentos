from dataclasses import dataclass
from typing import List


@dataclass
class ReviewResult:
    """
    最小 ReviewResult：
    第一阶段只表达是否通过、原因代码和说明。
    """

    status: str
    reason_codes: List[str]
    suggestion: str
