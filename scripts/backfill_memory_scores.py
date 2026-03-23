import json
from pathlib import Path


MEMORY_FILE = Path("memory/long_term_memory.json")


def calculate_score(result_text: str, token_usage: int, status: str) -> int:
    score = 0

    if status == "completed":
        score += 50

    result_len = len(str(result_text or ""))
    if result_len >= 2000:
        score += 25
    elif result_len >= 1000:
        score += 18
    elif result_len >= 500:
        score += 12
    elif result_len >= 200:
        score += 6

    token_usage = int(token_usage or 0)
    if token_usage > 0:
        if token_usage <= 500:
            score += 20
        elif token_usage <= 900:
            score += 16
        elif token_usage <= 1300:
            score += 12
        elif token_usage <= 1800:
            score += 8
        else:
            score += 4

    return score


def main():
    if not MEMORY_FILE.exists():
        print("memory file not found")
        return

    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0

    for item in data:
        if "score" in item and item["score"] not in (None, 0):
            continue

        result_text = item.get("result", "") or ""
        token_usage = int(item.get("token_usage", 0) or 0)
        status = item.get("status", "")

        item["score"] = calculate_score(result_text, token_usage, status)
        updated += 1

    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"updated_records={updated}")
    print(f"total_records={len(data)}")


if __name__ == "__main__":
    main()
