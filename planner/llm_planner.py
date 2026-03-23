import json
import os
from typing import Dict, Any, List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env", override=True)


PLANNER_SCHEMA_HINT = """
You are a task planning agent for AgentOS v2.

Return ONLY valid JSON in this exact format:
{
  "tasks": [
    {
      "id": "task_1",
      "type": "research|content|marketing|data",
      "agent": "ResearchAgent|ContentAgent|MarketingAgent|DataAgent",
      "task": "short actionable task",
      "priority": 1,
      "depends_on": [],
      "expected_output": "short description of what this task should produce"
    }
  ]
}

Rules:
1. Return 3 to 6 tasks only.
2. Tasks must be concrete and executable.
3. Use ids like task_1, task_2, task_3 ...
4. depends_on must only reference earlier task ids.
5. If a task requires research first, add depends_on correctly.
6. Do not include explanations.
7. Do not include markdown fences.
8. Prefer this mapping:
   - research -> ResearchAgent
   - content -> ContentAgent
   - marketing -> MarketingAgent
   - data -> DataAgent
"""


def _extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()

    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json", "", 1).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No valid JSON object found in LLM response")

    json_text = text[start:end + 1]
    data = json.loads(json_text)

    if "tasks" not in data or not isinstance(data["tasks"], list):
        raise ValueError("LLM JSON missing 'tasks' list")

    return data


def _validate_tasks(data: Dict[str, Any]) -> Dict[str, Any]:
    valid_types = {"research", "content", "marketing", "data"}
    valid_agents = {
        "ResearchAgent",
        "ContentAgent",
        "MarketingAgent",
        "DataAgent"
    }

    cleaned: List[Dict[str, Any]] = []
    seen_ids = set()

    for item in data["tasks"]:
        if not isinstance(item, dict):
            continue

        task_id = item.get("id")
        task_type = item.get("type")
        agent = item.get("agent")
        task_text = item.get("task")
        priority = item.get("priority", 1)
        depends_on = item.get("depends_on", [])
        expected_output = item.get("expected_output", "")

        if not isinstance(task_id, str) or not task_id.strip():
            continue
        if task_id in seen_ids:
            continue
        if task_type not in valid_types:
            continue
        if agent not in valid_agents:
            continue
        if not isinstance(task_text, str) or not task_text.strip():
            continue
        if not isinstance(priority, int):
            continue
        if not isinstance(depends_on, list):
            continue
        if not all(isinstance(x, str) for x in depends_on):
            continue
        if not isinstance(expected_output, str):
            continue

        seen_ids.add(task_id)

        cleaned.append({
            "id": task_id.strip(),
            "type": task_type,
            "agent": agent,
            "task": task_text.strip(),
            "priority": priority,
            "depends_on": depends_on,
            "expected_output": expected_output.strip()
        })

    if not cleaned:
        raise ValueError("No valid tasks after validation")

    return {"tasks": cleaned[:6]}


def _call_openai_planner(goal: str) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_PLANNER_MODEL", "gpt-5.4")

    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": PLANNER_SCHEMA_HINT},
            {"role": "user", "content": f"Goal: {goal}"}
        ],
        text={"format": {"type": "json_object"}}
    )

    output_text = response.output_text
    return _validate_tasks(_extract_json(output_text))


def _call_deepseek_planner(goal: str) -> Dict[str, Any]:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    model = os.getenv("DEEPSEEK_PLANNER_MODEL", "deepseek-chat")

    if not api_key:
        raise ValueError("Missing DEEPSEEK_API_KEY")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PLANNER_SCHEMA_HINT},
            {"role": "user", "content": f"Goal: {goal}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )

    output_text = response.choices[0].message.content
    return _validate_tasks(_extract_json(output_text))


def call_llm_planner(goal: str) -> Dict[str, Any]:
    provider = os.getenv("PLANNER_PROVIDER", "deepseek").lower()
    print(f"[LLM Planner] provider: {provider}")

    if provider == "openai":
        return _call_openai_planner(goal)

    if provider == "deepseek":
        return _call_deepseek_planner(goal)

    raise ValueError(f"Unsupported PLANNER_PROVIDER: {provider}")
