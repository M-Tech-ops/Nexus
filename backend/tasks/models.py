"""
Agent task models used for the Source Checklist feature.
"""

from dataclasses import dataclass, field
from enum import Enum


class ChecklistStatus(str, Enum):
    COMPLETE = "complete"
    MISSING = "missing"
    UNCERTAIN = "uncertain"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ChecklistItem:
    """
    A single requirement tracked against an agent task.
    """

    requirement: str
    status: ChecklistStatus
    source: str | None = None
    missing_reason: str | None = None


@dataclass
class ChecklistCompletion:
    """
    Derived completion state for a task's checklist. Always calculated from
    the checklist items — never set directly.

    Not-applicable items are excluded from the denominator: they don't
    count against completeness.
    """

    complete: int
    total: int

    @property
    def percent(self) -> int:
        if self.total == 0:
            return 0
        return round((self.complete / self.total) * 100)

    @classmethod
    def from_items(cls, items: list[ChecklistItem]) -> "ChecklistCompletion":
        applicable = [i for i in items if i.status != ChecklistStatus.NOT_APPLICABLE]
        complete = sum(1 for i in applicable if i.status == ChecklistStatus.COMPLETE)
        return cls(complete=complete, total=len(applicable))


@dataclass
class AgentTask:
    """
    A task produced by an agent, tracked for completeness via its checklist.
    """

    id: str
    title: str
    checklist: list[ChecklistItem] = field(default_factory=list)

    @property
    def completion(self) -> ChecklistCompletion:
        return ChecklistCompletion.from_items(self.checklist)