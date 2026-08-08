# Nexus AI

> A local-first desktop AI assistant built around a native Qt/C++ interface, a Python backend, local LLM inference, persistent memory, and real-world integrations.

Nexus AI is an experimental **local desktop AI assistant** designed to sit quietly on your desktop and act as a persistent interface between you, your computer, and the information you work with every day.

Instead of being just another chatbot, Nexus is being built around a simple idea:

> **The AI should reason, while the backend provides the facts.**

Emails, tasks, deadlines, projects, and other information are handled by dedicated backend services and then supplied to the local LLM as structured context.

The long-term goal is to create a fast, private, extensible assistant that feels like a native part of the operating system.

---
## Build (Windows, MSVC + Ninja — matches the project's existing toolchain)

1. Open the **x64 Native Tools Command Prompt for VS**.
2. Make sure `Qt6` is on your `CMAKE_PREFIX_PATH` (point it at your Qt
   install's `msvc2019_64` or `msvc2022_64` lib dir), e.g.:
   ```
   set CMAKE_PREFIX_PATH=C:\Qt\6.7.2\msvc2019_64
   ```
3. Configure and build:
   ```
   cmake -G Ninja -S . -B out\build\Ninja-Release -DCMAKE_BUILD_TYPE=Release
   cmake --build out\build\Ninja-Release
   ```
4. Run:
   ```
   out\build\Ninja-Release\NexusAI_Shell.exe
   ```
   If it can't find Qt DLLs at runtime, either run `windeployqt` on the
   .exe or add Qt's `bin` dir to `PATH`.



## ✨ Features

### 🧠 Local AI

Nexus uses a locally running LLM rather than depending on a cloud AI API for its core reasoning.

This provides:

- Local inference
- Better privacy
- No dependency on cloud inference for normal conversations
- Control over the model and inference parameters
- Ability to build custom tools around the model

The AI layer is intentionally separated from the tools and services that provide information.

---

### 🖥️ Native Qt/C++ Desktop UI

The frontend is built using **Qt and C++**.

The UI is designed around a compact, dynamic desktop panel inspired by modern "Dynamic Island / Dynamic Bar" interfaces.

Instead of occupying the entire screen, Nexus can remain as a small pill near the top of the screen.

Example:

```text
┌────────────────────────┐
│ Nexus AI           ●   │
└────────────────────────┘
- **Single monitor assumed** for centering; multi-monitor / DPI-aware
  positioning isn't handled yet.
- **Content of the expanded state is a stub label** — this scaffold is
  about the window mechanics, not the chat/response UI inside it.
