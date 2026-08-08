"""
High-level Agent Task Service.

The rest of Nexus AI should ONLY interact with this class for agent task
and checklist data.
"""

import json
from pathlib import Path

from tasks.models import AgentTask, ChecklistItem, ChecklistStatus

DEFAULT_STORAGE_PATH = (
        Path(__file__).resolve().parents[1] / "data" / "tasks" / "agent_tasks.json"
)


class TaskService:
    def __init__(self, storage_path: Path = DEFAULT_STORAGE_PATH):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def list_tasks(self) -> list[AgentTask]:
        return [self._from_dict(raw) for raw in self._read()]

    def get_task(self, task_id: str) -> AgentTask:
        for raw in self._read():
            if raw["id"] == task_id:
                return self._from_dict(raw)

        raise ValueError(f"Task '{task_id}' was not found.")

    def save_task(self, task: AgentTask) -> None:
        """Insert or update a task, keyed by id."""
        tasks = self._read()
        data = self._to_dict(task)

        for i, raw in enumerate(tasks):
            if raw["id"] == task.id:
                tasks[i] = data
                break
        else:
            tasks.append(data)

        self._write(tasks)

    def _read(self) -> list[dict]:
        if not self.storage_path.exists():
            return []

        with open(self.storage_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, tasks: list[dict]) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)

    @staticmethod
    def _to_dict(task: AgentTask) -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "checklist": [
                {
                    "requirement": item.requirement,
                    "status": item.status.value,
                    "source": item.source,
                    "missing_reason": item.missing_reason,
                }
                for item in task.checklist
            ],
        }

    @staticmethod
    def _from_dict(raw: dict) -> AgentTask:
        return AgentTask(
            id=raw["id"],
            title=raw["title"],
            checklist=[
                ChecklistItem(
                    requirement=item["requirement"],
                    status=ChecklistStatus(item["status"]),
                    source=item.get("source"),
                    missing_reason=item.get("missing_reason"),
                )
                for item in raw["checklist"]
            ],
        )