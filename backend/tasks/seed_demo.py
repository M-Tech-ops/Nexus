"""
Seeds the sample "Prepare ABC Proposal" task used to demonstrate the
Source Checklist feature end to end.

Run directly: python -m tasks.seed_demo
"""

from tasks.models import AgentTask, ChecklistItem, ChecklistStatus
from tasks.service import TaskService


def build_sample_task() -> AgentTask:
    return AgentTask(
        id="TASK-001",
        title="Prepare ABC Proposal",
        checklist=[
            ChecklistItem(
                requirement="Client identified",
                status=ChecklistStatus.COMPLETE,
                source="email_182",
            ),
            ChecklistItem(
                requirement="Meeting date identified",
                status=ChecklistStatus.COMPLETE,
                source="email_182",
            ),
            ChecklistItem(
                requirement="Proposal requested",
                status=ChecklistStatus.COMPLETE,
                source="email_182",
            ),
            ChecklistItem(
                requirement="Revised proposal requirements",
                status=ChecklistStatus.UNCERTAIN,
                missing_reason="Client referenced revised requirements "
                               "but did not specify them in the email.",
            ),
            ChecklistItem(
                requirement="Recipient identified",
                status=ChecklistStatus.COMPLETE,
                source="email_182",
            ),
        ],
    )


if __name__ == "__main__":
    task = build_sample_task()
    TaskService().save_task(task)

    print(f"{task.title}\n")
    for item in task.checklist:
        mark = "\u2713" if item.status == ChecklistStatus.COMPLETE else "\u26a0"
        print(f"{mark} {item.requirement}")

    c = task.completion
    print(f"\n{c.complete} / {c.total} complete\n{c.percent}%")