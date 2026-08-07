"""
Memory Router.

Converts structured memory requests into MemoryService operations.

This module does NOT call the LLM.
It only performs memory operations requested by the AI/backend.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .service import MemoryService


class MemoryRouter:

    def __init__(
        self,
        storage_path: str | Path,
    ) -> None:

        self.memory = MemoryService(storage_path)

        print("[MemoryRouter] Initialized.")

    # =========================================================
    # Projects
    # =========================================================

    def create_project(
        self,
        name: str,
        description: str = "",
    ):
        """
        Create a new project.
        """

        existing = self.memory.find_project(name)

        if existing:
            print(
                f"[MemoryRouter] Project already exists: "
                f"{existing.name}"
            )

            return existing

        return self.memory.create_project(
            name=name,
            description=description,
        )

    def get_projects(self):
        """
        Get active projects.
        """

        return self.memory.get_projects(
            status="active"
        )

    # =========================================================
    # Deadlines
    # =========================================================

    def add_deadline(
        self,
        title: str,
        date: str,
        project_id: Optional[str] = None,
        description: str = "",
    ):
        """
        Add a deadline.
        """

        return self.memory.add_deadline(
            title=title,
            date=date,
            project_id=project_id,
            description=description,
        )

    def get_deadlines(self):
        """
        Get incomplete deadlines.
        """

        return self.memory.get_deadlines(
            include_completed=False
        )

    # =========================================================
    # Tasks
    # =========================================================

    def add_task(
        self,
        title: str,
        project_id: Optional[str] = None,
        description: str = "",
        due_date: Optional[str] = None,
    ):
        """
        Add a task.
        """

        return self.memory.add_task(
            title=title,
            project_id=project_id,
            description=description,
            due_date=due_date,
        )

    def get_tasks(
        self,
        project_id: Optional[str] = None,
    ):
        """
        Get incomplete tasks.
        """

        return self.memory.get_tasks(
            project_id=project_id,
            include_completed=False,
        )

    # =========================================================
    # Summary
    # =========================================================

    def get_memory_summary(self):
        """
        Return all currently active memory.
        """

        return self.memory.get_memory_summary()