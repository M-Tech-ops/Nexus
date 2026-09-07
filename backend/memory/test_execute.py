from core.config import Config
from memory.parser import MemoryParser
from memory.router import MemoryRouter

Config.ensure_storage_directories()
parser = MemoryParser()
router = MemoryRouter(Config.MEMORY_DIR)


tests = [
    "Remember that I'm working on a new project called Test Project",
    "I have a deadline for the Test Project on November 2 2026",
    "I need to finish the email integration task",
]


for prompt in tests:

    print("\n================================")
    print("USER:")
    print(prompt)

    request = parser.parse(prompt)

    print("\nPARSED:")
    print(request)

    if request:

        result = router.execute(request)

        print("\nRESULT:")
        print(result)