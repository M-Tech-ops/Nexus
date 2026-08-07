# NexusAI_Shell — Dynamic Island Window Scaffold

Frameless, translucent, always-on-top Qt 6 widget that morphs between
Idle / Compact / Expanded sizes at the top-center of the screen, with
Windows acrylic blur-behind. This is just the frontend shell — no backend
connection yet.

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

## What's here

- `DynamicIslandWindow.{h,cpp}` — the widget itself: frameless/translucent
  window, rounded-corner mask, geometry animation between the three states,
  and the Windows-only acrylic blur hook (`SetWindowCompositionAttribute`,
  resolved dynamically so it degrades gracefully elsewhere).
- `main.cpp` — launches the window and (temporarily) cycles through states
  on a timer so you can see it working standalone. Click the pill to cycle
  states manually. Remove the timer demo once this is wired to real events.

## Known gaps / next steps

- **No backend connection yet.** State changes should eventually come from
  the Python backend over a WebSocket (email received, voice command,
  AI response ready, etc.) instead of the click handler / demo timer here.
- **Acrylic tint/opacity is a placeholder** (`0x99201818`) — tune once you
  have real content in the expanded state.
- **Single monitor assumed** for centering; multi-monitor / DPI-aware
  positioning isn't handled yet.
- **Content of the expanded state is a stub label** — this scaffold is
  about the window mechanics, not the chat/response UI inside it.
