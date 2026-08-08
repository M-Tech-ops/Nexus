from memory.parser import MemoryParser


parser = MemoryParser()


tests = [
    "Remember that I'm working on a new project called Nexus AI",
    "I have a deadline for the Nexus AI project on November 2 2026",
    "I need to finish the email integration task",
    "I have to finish the memory system by 2026-09-01",
    "What is the weather today?",
]


for prompt in tests:

    print("\nUSER:")
    print(prompt)

    result = parser.parse(prompt)

    print("PARSED:")
    print(result)