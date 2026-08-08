"""
Memory Context.

Converts factual data retrieved by MemoryService into a controlled
prompt context for the LLM.

The LLM is never allowed to invent records. The data supplied here
comes directly from the persistent memory service.
"""

from __future__ import annotations

from typing import Any


class MemoryContext:
    """Formats backend memory data for grounded LLM responses."""

    @staticmethod
    def _format_projects(projects: list[dict]) -> str:
        if not projects:
            return "No active projects are currently stored."

        lines = []

        for index, project in enumerate(projects, start=1):
            lines.append(
                f"{index}. {project.get('name', 'Unnamed project')}"
            )

            description = project.get("description")
            if description:
                lines.append(f"   Description: {description}")

            started_at = project.get("started_at")
            if started_at:
                lines.append(f"   Started: {started_at}")

        return "\n".join(lines)

    @staticmethod
    def _format_deadlines(deadlines: list[dict]) -> str:
        if not deadlines:
            return "No incomplete deadlines are currently stored."

        lines = []

        for index, deadline in enumerate(deadlines, start=1):
            title = deadline.get("title", "Untitled deadline")
            date = deadline.get("date", "Date not specified")

            lines.append(
                f"{index}. {title} — due {date}"
            )

            description = deadline.get("description")
            if description:
                lines.append(f"   Description: {description}")

        return "\n".join(lines)

    @staticmethod
    def _format_tasks(tasks: list[dict]) -> str:
        if not tasks:
            return "No incomplete tasks are currently stored."

        lines = []

        for index, task in enumerate(tasks, start=1):
            title = task.get("title", "Untitled task")
            line = f"{index}. {title}"

            due_date = task.get("due_date")
            if due_date:
                line += f" — due {due_date}"

            lines.append(line)

            description = task.get("description")
            if description:
                lines.append(f"   Description: {description}")

        return "\n".join(lines)

    @classmethod
    def for_request(
        cls,
        action: str,
        result: Any,
    ) -> str:
        """
        Build a grounded prompt for one memory operation.

        `result` must come from MemoryService/MemoryRouter.
        """

        if action == "get_deadlines":
            data = [
                item.to_dict()
                for item in result
            ]

            return f"""
MEMORY CONTEXT — DEADLINES

The following information was retrieved directly from Nexus's
persistent memory storage.

{cls._format_deadlines(data)}
""".strip()

        if action == "get_projects":
            data = [
                item.to_dict()
                for item in result
            ]

            return f"""
MEMORY CONTEXT — PROJECTS

The following information was retrieved directly from Nexus's
persistent memory storage.

{cls._format_projects(data)}
""".strip()

        if action == "get_tasks":
            data = [
                item.to_dict()
                for item in result
            ]

            return f"""
MEMORY CONTEXT — TASKS

The following information was retrieved directly from Nexus's
persistent memory storage.

{cls._format_tasks(data)}
""".strip()

        if action == "get_memory_summary":
            data = result or {}

            projects = data.get("projects", [])
            deadlines = data.get("deadlines", [])
            tasks = data.get("tasks", [])

            return f"""
MEMORY CONTEXT — COMPLETE STORED MEMORY

The following information was retrieved directly from Nexus's
persistent memory storage.

ACTIVE PROJECTS:
{cls._format_projects(projects)}

INCOMPLETE DEADLINES:
{cls._format_deadlines(deadlines)}

INCOMPLETE TASKS:
{cls._format_tasks(tasks)}
""".strip()

        raise ValueError(
            f"Unsupported memory context action: {action}"
        )
