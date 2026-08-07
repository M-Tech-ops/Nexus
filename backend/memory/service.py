"""
Nexus AI Memory Service.

High-level interface for persistent user memory.

Responsibilities:
- Create and manage projects.
- Create and manage deadlines.
- Create and manage tasks.
- Retrieve memory information.
- Hide JSON/storage implementation from the rest of the application.

This module does NOT:
- Call the LLM.
- Parse natural-language prompts.
- Directly handle IMAP/email.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from .models import Project, Deadline, Task
from .storage import JSONStorage


class MemoryService:

    PROJECTS_FILE = "projects.json"
    DEADLINES_FILE = "deadlines.json"
    TASKS_FILE = "tasks.json"

    def __init__(
        self,
        storage_path: str | Path,
    ) -> None:

        self.storage = JSONStorage(storage_path)

        print("[MemoryService] Initialized.")

    # =========================================================
    # Helpers
    # =========================================================

    @staticmethod
    def _generate_id(prefix: str) -> str:
        """
        Generate a unique ID for a memory item.
        """

        return f"{prefix}_{uuid4().hex[:8]}"

    @staticmethod
    def _now() -> str:
        """
        Return the current local timestamp in ISO format.
        """

        return datetime.now().isoformat(timespec="seconds")

    # =========================================================
    # Projects
    # =========================================================

    def create_project(
        self,
        name: str,
        description: str = "",
        status: str = "active",
    ) -> Project:
        """
        Create and persist a new project.
        """

        project = Project(
            id=self._generate_id("project"),
            name=name,
            description=description,
            status=status,
            started_at=self._now(),
        )

        self.storage.append(
            self.PROJECTS_FILE,
            project.to_dict(),
        )

        print(
            f"[MemoryService] Created project: "
            f"{project.name}"
        )

        return project

    def get_projects(
        self,
        status: Optional[str] = None,
    ) -> list[Project]:
        """
        Return all projects.

        If status is supplied, only projects with that status
        are returned.
        """

        data = self.storage.read(
            self.PROJECTS_FILE
        )

        projects = [
            Project.from_dict(item)
            for item in data
        ]

        if status is not None:
            projects = [
                project
                for project in projects
                if project.status.lower() == status.lower()
            ]

        return projects

    def get_project(
        self,
        project_id: str,
    ) -> Optional[Project]:
        """
        Find a project by ID.
        """

        projects = self.get_projects()

        for project in projects:
            if project.id == project_id:
                return project

        return None

    def find_project(
        self,
        name: str,
    ) -> Optional[Project]:
        """
        Find a project by name.

        Matching is case-insensitive.
        """

        name = name.strip().lower()

        projects = self.get_projects()

        for project in projects:
            if project.name.lower() == name:
                return project

        return None

    def update_project(
        self,
        project_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[Project]:
        """
        Update an existing project.
        """

        data = self.storage.read(
            self.PROJECTS_FILE
        )

        for item in data:

            if item.get("id") != project_id:
                continue

            if name is not None:
                item["name"] = name

            if description is not None:
                item["description"] = description

            if status is not None:
                item["status"] = status

            self.storage.write(
                self.PROJECTS_FILE,
                data,
            )

            return Project.from_dict(item)

        return None

    def delete_project(
        self,
        project_id: str,
    ) -> bool:
        """
        Delete a project.
        """

        return self.storage.delete(
            self.PROJECTS_FILE,
            project_id,
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
    ) -> Deadline:
        """
        Create and persist a deadline.

        Date is currently stored as a string so the service
        doesn't make assumptions about how the AI parsed it.
        """

        deadline = Deadline(
            id=self._generate_id("deadline"),
            title=title,
            date=date,
            project_id=project_id,
            description=description,
            completed=False,
        )

        self.storage.append(
            self.DEADLINES_FILE,
            deadline.to_dict(),
        )

        print(
            f"[MemoryService] Added deadline: "
            f"{deadline.title} ({deadline.date})"
        )

        return deadline

    def get_deadlines(
        self,
        include_completed: bool = False,
    ) -> list[Deadline]:
        """
        Return stored deadlines.
        """

        data = self.storage.read(
            self.DEADLINES_FILE
        )

        deadlines = [
            Deadline.from_dict(item)
            for item in data
        ]

        if not include_completed:
            deadlines = [
                deadline
                for deadline in deadlines
                if not deadline.completed
            ]

        return deadlines

    def get_deadline(
        self,
        deadline_id: str,
    ) -> Optional[Deadline]:
        """
        Find a deadline by ID.
        """

        deadlines = self.get_deadlines(
            include_completed=True
        )

        for deadline in deadlines:
            if deadline.id == deadline_id:
                return deadline

        return None

    def complete_deadline(
        self,
        deadline_id: str,
    ) -> Optional[Deadline]:
        """
        Mark a deadline as completed.
        """

        data = self.storage.read(
            self.DEADLINES_FILE
        )

        for item in data:

            if item.get("id") != deadline_id:
                continue

            item["completed"] = True

            self.storage.write(
                self.DEADLINES_FILE,
                data,
            )

            return Deadline.from_dict(item)

        return None

    def delete_deadline(
        self,
        deadline_id: str,
    ) -> bool:
        """
        Delete a deadline.
        """

        return self.storage.delete(
            self.DEADLINES_FILE,
            deadline_id,
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
    ) -> Task:
        """
        Create and persist a task.
        """

        task = Task(
            id=self._generate_id("task"),
            title=title,
            project_id=project_id,
            description=description,
            completed=False,
            due_date=due_date,
        )

        self.storage.append(
            self.TASKS_FILE,
            task.to_dict(),
        )

        print(
            f"[MemoryService] Added task: "
            f"{task.title}"
        )

        return task

    def get_tasks(
        self,
        project_id: Optional[str] = None,
        include_completed: bool = False,
    ) -> list[Task]:
        """
        Return stored tasks.

        Optional filtering:
        - project_id
        - completed status
        """

        data = self.storage.read(
            self.TASKS_FILE
        )

        tasks = [
            Task.from_dict(item)
            for item in data
        ]

        if project_id is not None:
            tasks = [
                task
                for task in tasks
                if task.project_id == project_id
            ]

        if not include_completed:
            tasks = [
                task
                for task in tasks
                if not task.completed
            ]

        return tasks

    def get_task(
        self,
        task_id: str,
    ) -> Optional[Task]:
        """
        Find a task by ID.
        """

        tasks = self.get_tasks(
            include_completed=True
        )

        for task in tasks:
            if task.id == task_id:
                return task

        return None

    def complete_task(
        self,
        task_id: str,
    ) -> Optional[Task]:
        """
        Mark a task as completed.
        """

        data = self.storage.read(
            self.TASKS_FILE
        )

        for item in data:

            if item.get("id") != task_id:
                continue

            item["completed"] = True

            self.storage.write(
                self.TASKS_FILE,
                data,
            )

            return Task.from_dict(item)

        return None

    def delete_task(
        self,
        task_id: str,
    ) -> bool:
        """
        Delete a task.
        """

        return self.storage.delete(
            self.TASKS_FILE,
            task_id,
        )

    # =========================================================
    # Summary
    # =========================================================

    def get_memory_summary(self) -> dict:
        """
        Return a structured summary of stored memory.

        This will later be useful for startup reminders and
        giving the LLM a compact memory context.
        """

        projects = self.get_projects()
        deadlines = self.get_deadlines()
        tasks = self.get_tasks()

        return {
            "projects": [
                project.to_dict()
                for project in projects
            ],
            "deadlines": [
                deadline.to_dict()
                for deadline in deadlines
            ],
            "tasks": [
                task.to_dict()
                for task in tasks
            ],
        }