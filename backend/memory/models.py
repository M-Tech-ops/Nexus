"""
Memory data models.

These models define the structure of information Nexus can remember.
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Project:
    id: str
    name: str
    description: str = ""
    status: str = "active"
    started_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            status=data.get("status", "active"),
            started_at=data.get("started_at"),
        )


@dataclass
class Deadline:
    id: str
    title: str
    date: str
    project_id: Optional[str] = None
    description: str = ""
    completed: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Deadline":
        return cls(
            id=data["id"],
            title=data["title"],
            date=data["date"],
            project_id=data.get("project_id"),
            description=data.get("description", ""),
            completed=data.get("completed", False),
        )


@dataclass
class Task:
    id: str
    title: str
    project_id: Optional[str] = None
    description: str = ""
    completed: bool = False
    due_date: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            title=data["title"],
            project_id=data.get("project_id"),
            description=data.get("description", ""),
            completed=data.get("completed", False),
            due_date=data.get("due_date"),
        )