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

import re
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
        
        if request.action == "complete_deadline":
            return self.complete_deadline(
            title=request.title,
            date=request.date,
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
    

    def complete_deadline(
    self,
    title: Optional[str] = None,
    date: Optional[str] = None,
):
        """
        Mark an existing deadline as completed.

        The deadline can be identified by title or date.
        If there is exactly one incomplete deadline and
        no identifying information was supplied, use that
        deadline as the target.
        """

        deadlines = self.memory.get_deadlines(
            include_completed=True
        )

        incomplete = [
            deadline
            for deadline in deadlines
            if not deadline.completed
        ]

        if not incomplete:
            print("[MemoryRouter] No incomplete deadlines found.")
            return None

        # ---------------------------------------------------------
        # Try matching by title
        # ---------------------------------------------------------

        if title:
            title_lower = title.strip().lower()

            title_words = set(
                re.findall(r"\b[a-z0-9]+\b", title_lower)
            )

            matches = []

            for deadline in incomplete:
                deadline_lower = deadline.title.lower()

                deadline_words = set(
                    re.findall(r"\b[a-z0-9]+\b", deadline_lower)
                )

                # Ignore generic words that don't help identify
                # the actual deadline.
                meaningful_words = title_words - {
                    "my",
                    "the",
                    "this",
                    "that",
                    "deadline",
                }

        if meaningful_words and meaningful_words.issubset(deadline_words):
            matches.append(deadline)

            if len(matches) == 1:
                deadline = matches[0]

                print(
                    f"[MemoryRouter] Completing deadline: "
                    f"{deadline.title} ({deadline.id})"
                )

                return self.memory.complete_deadline(
                    deadline.id
                )

        # ---------------------------------------------------------
        # Try matching by date
        # ---------------------------------------------------------

        if date:
            matches = [
                deadline
                for deadline in incomplete
                if deadline.date == date
            ]

            if len(matches) == 1:
                deadline = matches[0]

                print(
                    f"[MemoryRouter] Completing deadline: "
                    f"{deadline.title} ({deadline.id})"
                )

                return self.memory.complete_deadline(
                    deadline.id
                )

        # ---------------------------------------------------------
        # If there is exactly one incomplete deadline,
        # allow "mark this deadline complete"
        # ---------------------------------------------------------

        if not title and not date and len(incomplete) == 1:
            deadline = incomplete[0]

            print(
                f"[MemoryRouter] Completing only incomplete deadline: "
                f"{deadline.title} ({deadline.id})"
            )

            return self.memory.complete_deadline(
                deadline.id
            )

        print(
            "[MemoryRouter] Could not uniquely identify "
            "the deadline to complete."
        )

        return None
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
