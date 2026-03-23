from models.task import Task


class Planner:
    def _default_agent_for_type(self, task_type: str) -> str:
        mapping = {
            "research": "research",
            "content": "content",
            "marketing": "marketing",
            "data": "data",
            "summary": "content",
            "video": "content",
        }
        return mapping.get(task_type, "content")

    def _build_tiktok_marketing_plan(self, history=None):
        return [
            Task(
                id="task_1",
                type="research",
                agent=self._default_agent_for_type("research"),
                task="Research TikTok trends",
                priority=1,
                depends_on=[],
                expected_output="Trend summary",
            ),
            Task(
                id="task_2",
                type="research",
                agent=self._default_agent_for_type("research"),
                task="Analyze competitors",
                priority=1,
                depends_on=[],
                expected_output="Competitor summary",
            ),
            Task(
                id="task_3",
                type="content",
                agent=self._default_agent_for_type("content"),
                task="Generate content ideas",
                priority=2,
                depends_on=["task_1", "task_2"],
                expected_output="Content ideas",
            ),
            Task(
                id="task_4",
                type="marketing",
                agent=self._default_agent_for_type("marketing"),
                task="Design TikTok marketing strategy",
                priority=2,
                depends_on=["task_1", "task_2"],
                expected_output="Marketing strategy",
            ),
            Task(
                id="task_5",
                type="data",
                agent=self._default_agent_for_type("data"),
                task="Define evaluation metrics",
                priority=3,
                depends_on=["task_3", "task_4"],
                expected_output="KPI metrics",
            ),
            Task(
                id="task_6",
                type="summary",
                agent=self._default_agent_for_type("summary"),
                task="Summarize the full TikTok strategy into an executive report",
                priority=4,
                depends_on=["task_3", "task_4", "task_5"],
                expected_output="Executive summary",
            ),
            Task(
                id="task_7",
                type="video",
                agent=self._default_agent_for_type("video"),
                task="Generate short video campaign concepts for TikTok",
                priority=4,
                depends_on=["task_3", "task_4"],
                expected_output="Video campaign ideas",
            ),
        ]

    def _build_generic_plan(self, goal, history=None):
        history = history or []

        tasks = [
            Task(
                id="task_1",
                type="research",
                agent=self._default_agent_for_type("research"),
                task=f"Research goal: {goal}",
                priority=1,
                depends_on=[],
                expected_output="Research summary",
            ),
            Task(
                id="task_2",
                type="content",
                agent=self._default_agent_for_type("content"),
                task=f"Generate solution content for goal: {goal}",
                priority=2,
                depends_on=["task_1"],
                expected_output="Content output",
            ),
        ]

        task_scores = {}
        for item in history:
            task_type = item.get("task_type")
            if not task_type:
                continue

            if task_type not in task_scores:
                task_scores[task_type] = {
                    "count": 0,
                    "score_sum": 0,
                }

            task_scores[task_type]["count"] += 1
            task_scores[task_type]["score_sum"] += int(item.get("score", 0) or 0)

        ranked = []
        for task_type, stat in task_scores.items():
            avg_score = stat["score_sum"] / stat["count"] if stat["count"] else 0
            ranked.append(
                {
                    "task_type": task_type,
                    "count": stat["count"],
                    "avg_score": avg_score,
                }
            )

        ranked.sort(
            key=lambda x: (x["avg_score"], x["count"]),
            reverse=True,
        )

        allowed_extra_types = ["marketing", "data", "summary"]
        selected_extra_types = []

        for item in ranked:
            task_type = item["task_type"]
            if task_type not in allowed_extra_types:
                continue
            if item["count"] < 1:
                continue
            if item["avg_score"] < 55:
                continue
            selected_extra_types.append(task_type)

        selected_extra_types = selected_extra_types[:3]

        next_id = 3

        if "marketing" in selected_extra_types and next_id <= 5:
            tasks.append(
                Task(
                    id=f"task_{next_id}",
                    type="marketing",
                    agent=self._default_agent_for_type("marketing"),
                    task=f"Design strategy for goal: {goal}",
                    priority=3,
                    depends_on=["task_1", "task_2"],
                    expected_output="Strategy output",
                )
            )
            next_id += 1

        if "data" in selected_extra_types and next_id <= 5:
            depends = ["task_2"]
            if any(t.type == "marketing" for t in tasks):
                depends = ["task_2", "task_3"]

            tasks.append(
                Task(
                    id=f"task_{next_id}",
                    type="data",
                    agent=self._default_agent_for_type("data"),
                    task=f"Define metrics for goal: {goal}",
                    priority=3,
                    depends_on=depends,
                    expected_output="Metrics",
                )
            )
            next_id += 1

        if "summary" in selected_extra_types and next_id <= 5:
            previous_ids = [task.id for task in tasks if task.id != "task_1"]

            tasks.append(
                Task(
                    id=f"task_{next_id}",
                    type="summary",
                    agent=self._default_agent_for_type("summary"),
                    task=f"Summarize solution for goal: {goal}",
                    priority=4,
                    depends_on=previous_ids,
                    expected_output="Summary",
                )
            )
            next_id += 1

        return tasks

    def plan(self, goal, history=None):
        history = history or []
        goal_lower = goal.lower()

        if "tiktok" in goal_lower and "marketing" in goal_lower:
            return self._build_tiktok_marketing_plan(history)

        return self._build_generic_plan(goal, history)
