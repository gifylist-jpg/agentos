import json
import re


def extract_json_block(text: str) -> dict:
    """
    尝试从模型输出中提取 JSON。
    支持：
    1. ```json ... ```
    2. 纯 JSON
    3. 文本中包裹的 JSON 对象
    """
    if not text:
        return {}

    text = text.strip()

    # 1) 优先匹配 ```json ... ```
    fenced_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced_match:
        json_str = fenced_match.group(1).strip()
        try:
            return json.loads(json_str)
        except Exception:
            pass

    # 2) 尝试整个文本直接按 JSON 解析
    try:
        return json.loads(text)
    except Exception:
        pass

    # 3) 尝试提取第一个 {...}
    brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
    if brace_match:
        json_str = brace_match.group(1).strip()
        try:
            return json.loads(json_str)
        except Exception:
            pass

    return {}
