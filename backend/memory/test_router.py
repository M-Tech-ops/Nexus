from core.config import Config
from memory.router import MemoryRouter

Config.ensure_storage_directories()
router = MemoryRouter(Config.MEMORY_DIR)


print("\n========== CREATE PROJECT ==========")

project = router.create_project(
    name="Nexus AI",
    description="Personal AI assistant",
)

print(project)


print("\n========== ADD DEADLINE ==========")

deadline = router.add_deadline(
    title="Nexus AI submission",
    date="2026-11-02",
    project_id=project.id,
)

print(deadline)


print("\n========== ADD TASK ==========")

task = router.add_task(
    title="Finish memory system",
    project_id=project.id,
)

print(task)


print("\n========== PROJECTS ==========")

for project in router.get_projects():
    print(project)


print("\n========== DEADLINES ==========")

for deadline in router.get_deadlines():
    print(deadline)


print("\n========== TASKS ==========")

for task in router.get_tasks():
    print(task)