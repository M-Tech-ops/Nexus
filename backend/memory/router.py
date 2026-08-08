"""
Memory Router.

Executes structured memory requests produced by MemoryParser.

This module does NOT:
- Call the LLM.
- Parse natural language.
- Directly manipulate JSON.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .parser import MemoryRequest
from .service import MemoryService


class MemoryRouter:
    def __init__(self, storage_path: str | Path) -> None:
        self.memory = MemoryService(storage_path)

        print("[MemoryRouter] Initialized.")

    # =========================================================
    # Structured Request Execution
    # =========================================================

    def execute(self, request: MemoryRequest):
        """
        Execute a MemoryRequest.

        Returns:
            Created/updated memory object for WRITE operations,
            or retrieved memory data for READ operations.
        """

        print(
            f"[MemoryRouter] Executing action: "
            f"{request.action}"
        )

        # -----------------------------------------------------
        # READ operations
        # -----------------------------------------------------

        if request.action == "get_deadlines":
            return self.get_deadlines()

        if request.action == "get_projects":
            return self.get_projects()

        if request.action == "get_tasks":
            return self.get_tasks()

        if request.action == "get_memory_summary":
            return self.get_memory_summary()

        # -----------------------------------------------------
        # WRITE operations
        # -----------------------------------------------------

        if request.action == "create_project":
            return self.create_project(
                name=request.name or "Unnamed Project",
                description=request.description,
            )

        if request.action == "add_deadline":
            return self.add_deadline(
                title=request.title or "Deadline",
                date=request.date,
                project_name=request.project_name,
                description=request.description,
            )

        if request.action == "add_task":
            return self.add_task(
                title=request.title or "Task",
                project_name=request.project_name,
                description=request.description,
                due_date=request.due_date,
            )

        print(
            f"[MemoryRouter] Unknown action: "
            f"{request.action}"
        )

        return None

    # =========================================================
    # Projects
    # =========================================================

    def create_project(
        self,
        name: str,
        description: str = "",
    ):
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
        return self.memory.get_projects(
            status="active"
        )

    # =========================================================
    # Deadlines
    # =========================================================

    def add_deadline(
        self,
        title: str,
        date: Optional[str],
        project_name: Optional[str] = None,
        project_id: Optional[str] = None,
        description: str = "",
    ):
        if project_id is None and project_name:
            project = self.memory.find_project(
                project_name
            )

            if project:
                project_id = project.id
            else:
                print(
                    f"[MemoryRouter] Project not found: "
                    f"{project_name}"
                )

        if not date:
            print(
                "[MemoryRouter] Deadline requires a date."
            )
            return None

        return self.memory.add_deadline(
            title=title,
            date=date,
            project_id=project_id,
            description=description,
        )

    def get_deadlines(self):
        return self.memory.get_deadlines(
            include_completed=False
        )

    # =========================================================
    # Tasks
    # =========================================================

    def add_task(
        self,
        title: str,
        project_name: Optional[str] = None,
        project_id: Optional[str] = None,
        description: str = "",
        due_date: Optional[str] = None,
    ):
        if project_id is None and project_name:
            project = self.memory.find_project(
                project_name
            )

            if project:
                project_id = project.id
            else:
                print(
                    f"[MemoryRouter] Project not found: "
                    f"{project_name}"
                )

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
        return self.memory.get_tasks(
            project_id=project_id,
            include_completed=False,
        )

    # =========================================================
    # Summary
    # =========================================================

    def get_memory_summary(self):
        return self.memory.get_memory_summary()
