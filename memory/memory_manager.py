import json
import os
from datetime import datetime
from typing import Any


class MemoryManager:
    def __init__(self, memory_file="memory/long_term_memory.json"):
        self.memory_file = memory_file
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)

        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

        self.stopwords = {
            "build", "create", "generate", "design", "make", "plan", "strategy",
            "for", "the", "a", "an", "and", "or", "to", "of", "in", "on", "with",
            "goal", "solution", "summary", "report", "full"
        }

    def _load_data(self) -> list[dict]:
        if not os.path.exists(self.memory_file):
            return []

        with open(self.memory_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []

    def _save_data(self, data: list[dict]) -> None:
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _normalize_text(self, text: str) -> str:
        return str(text or "").strip().lower()

    def _tokenize(self, text: str) -> list[str]:
        normalized = self._normalize_text(text)
        raw = normalized.replace("_", " ").replace("-", " ").split()
        return [word for word in raw if word]

    def _meaningful_tokens(self, text: str) -> set[str]:
        return {
            token for token in self._tokenize(text)
            if token not in self.stopwords and len(token) >= 3
        }

    def _calculate_score(self, result_text: str, token_usage: int, status: str) -> int:
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

    def _task_to_memory_item(self, goal: str, task) -> dict[str, Any]:
        result_text = getattr(task, "result", None) or ""
        token_usage = int(getattr(task, "token_usage", 0) or 0)
        status = getattr(task, "status", None)
        summary = str(result_text)[:300]
        score = self._calculate_score(result_text, token_usage, status)

        return {
            "goal": goal,
            "task_id": getattr(task, "id", None),
            "task_type": getattr(task, "type", None),
            "agent": getattr(task, "agent", None),
            "task_text": getattr(task, "task", ""),
            "result": result_text,
            "summary": summary,
            "status": status,
            "model": getattr(task, "model", None),
            "token_usage": token_usage,
            "score": score,
            "depends_on": getattr(task, "depends_on", []),
            "timestamp": datetime.now().isoformat(),
        }

    def store_task_result(self, goal, task):
        data = self._load_data()
        data.append(self._task_to_memory_item(goal, task))
        self._save_data(data)

    def get_recent_tasks(self, limit: int = 10) -> list[dict]:
        data = self._load_data()
        return data[-limit:]

    def _score_goal_similarity(self, current_goal: str, memory_goal: str) -> int:
        current_tokens = self._meaningful_tokens(current_goal)
        memory_tokens = self._meaningful_tokens(memory_goal)

        if not current_tokens or not memory_tokens:
            return 0

        overlap = current_tokens.intersection(memory_tokens)
        overlap_count = len(overlap)

        current_goal_norm = self._normalize_text(current_goal)
        memory_goal_norm = self._normalize_text(memory_goal)

        if current_goal_norm == memory_goal_norm:
            return 100 + overlap_count * 10

        if overlap_count < 2:
            return 0

        score = overlap_count * 10

        if current_goal_norm in memory_goal_norm or memory_goal_norm in current_goal_norm:
            score += 20

        return score

    def search_similar_goals(self, goal, limit: int = 5, min_score: int = 10) -> list[dict]:
        data = self._load_data()

        scored = []
        for item in data:
            memory_goal = item.get("goal", "")
            similarity_score = self._score_goal_similarity(goal, memory_goal)
            if similarity_score >= min_score:
                enriched = dict(item)
                enriched["_similarity_score"] = similarity_score
                scored.append(enriched)

        scored.sort(
            key=lambda x: (
                x.get("_similarity_score", 0),
                x.get("score", 0),
                x.get("timestamp", ""),
            ),
            reverse=True,
        )

        return scored[:limit]

    def get_high_quality_similar_goals(self, goal: str, limit: int = 10, min_score: int = 10) -> list[dict]:
        matched = self.search_similar_goals(goal, limit=limit * 3, min_score=min_score)

        filtered = []
        for item in matched:
            if item.get("status") != "completed":
                continue
            if not item.get("result"):
                continue
            filtered.append(item)

        filtered.sort(
            key=lambda x: (
                x.get("_similarity_score", 0),
                x.get("score", 0),
                x.get("timestamp", ""),
            ),
            reverse=True,
        )

        return filtered[:limit]

    def get_recommended_task_types(self, goal: str, limit: int = 10, min_score: int = 10) -> list[str]:
        matched = self.get_high_quality_similar_goals(goal, limit=limit, min_score=min_score)

        counts = {}
        for item in matched:
            task_type = item.get("task_type")
            if not task_type:
                continue
            counts[task_type] = counts.get(task_type, 0) + 1

        ranked = sorted(
            counts.items(),
            key=lambda x: (x[1], x[0]),
            reverse=True,
        )

        return [task_type for task_type, _ in ranked]

    def get_recommended_task_type_scores(self, goal: str, limit: int = 10, min_score: int = 10) -> list[dict]:
        matched = self.get_high_quality_similar_goals(goal, limit=limit, min_score=min_score)

        stats = {}
        for item in matched:
            task_type = item.get("task_type")
            if not task_type:
                continue

            if task_type not in stats:
                stats[task_type] = {
                    "task_type": task_type,
                    "count": 0,
                    "total_score": 0,
                    "best_score": 0,
                    "avg_token_usage": 0,
                    "_token_sum": 0,
                }

            stats[task_type]["count"] += 1
            stats[task_type]["total_score"] += int(item.get("score", 0) or 0)
            stats[task_type]["best_score"] = max(
                stats[task_type]["best_score"],
                int(item.get("score", 0) or 0),
            )
            stats[task_type]["_token_sum"] += int(item.get("token_usage", 0) or 0)

        results = []
        for task_type, item in stats.items():
            count = item["count"]
            item["avg_score"] = round(item["total_score"] / count, 2) if count else 0
            item["avg_token_usage"] = round(item["_token_sum"] / count, 2) if count else 0
            del item["_token_sum"]
            results.append(item)

        results.sort(
            key=lambda x: (
                x["avg_score"],
                x["count"],
                -x["avg_token_usage"],
            ),
            reverse=True,
        )

        return results

    def build_goal_memory_summary(self, goal: str, limit: int = 5, min_score: int = 10) -> str:
        matched = self.get_high_quality_similar_goals(goal, limit=limit, min_score=min_score)

        if not matched:
            return "No similar historical goals found."

        lines = []
        lines.append("Relevant historical task memory:")
        lines.append("")

        for idx, item in enumerate(matched, start=1):
            lines.append(f"{idx}. Goal: {item.get('goal', '')}")
            lines.append(f"   Similarity Score: {item.get('_similarity_score', 0)}")
            lines.append(f"   Task Type: {item.get('task_type', '')}")
            lines.append(f"   Agent: {item.get('agent', '')}")
            lines.append(f"   Status: {item.get('status', '')}")
            lines.append(f"   Model: {item.get('model', '')}")
            lines.append(f"   Token Usage: {item.get('token_usage', 0)}")
            lines.append(f"   Score: {item.get('score', 0)}")
            lines.append(f"   Summary: {item.get('summary', '')}")
            lines.append("")

        return "\n".join(lines).strip()

    def get_status(self) -> dict:
        data = self._load_data()
        return {
            "memory_file": self.memory_file,
            "total_records": len(data),
        }
