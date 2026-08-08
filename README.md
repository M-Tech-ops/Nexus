<div align="center">

# NexusAI_Shell

### Dynamic Island Window Scaffold

![Qt](https://img.shields.io/badge/Qt-6-41CD52?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white)
![Build System](https://img.shields.io/badge/build-CMake%20%2B%20Ninja-064F8C?logo=cmake&logoColor=white)
![Toolchain](https://img.shields.io/badge/toolchain-MSVC-5C2D91?logo=visualstudio&logoColor=white)
![Backend](https://img.shields.io/badge/backend-Python-3776AB?logo=python&logoColor=white)

NexusAI_Shell is the interface for an AI agent that can add tasks, track deadlines, and read your emails — presented as a frameless, always-on-top Qt 6 widget that morphs between Idle, Compact, and Expanded states at the top-center of the screen, with Windows acrylic blur-behind.

</div>

## Table of Contents

- [Prerequisites](#prerequisites)
- [Python Backend Setup](#python-backend-setup)
  - [Optional: CUDA Support](#optional-cuda-support)
- [Build](#build-windows-msvc--ninja)
- [Run](#run)

## Prerequisites

| Requirement | Notes |
|---|---|
| **Qt 6** | MSVC build — e.g. `msvc2019_64` or `msvc2022_64` |
| **CMake** | Used to configure the project |
| **Ninja** | Build backend |
| **Visual Studio Build Tools** | Provides the MSVC toolchain and Developer PowerShell |
| **Python 3.x** | Runs the backend (`backend/main.py`) |
| **pip** | Installs backend dependencies |
| **NVIDIA GPU + CUDA Toolkit** *(optional)* | Only needed for CUDA-accelerated inference |

## Python Backend Setup

1. Navigate to the backend directory:

   ```powershell
   cd backend
   ```

2. *(Recommended)* Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install the required dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

### Optional: CUDA Support

If you have an NVIDIA GPU and want CUDA-accelerated inference, rebuild `llama-cpp-python` from source with the `GGML_CUDA` CMake flag enabled, instead of the default CPU-only build:

```powershell
$env:CMAKE_ARGS="-DGGML_CUDA=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

This requires the CUDA Toolkit to be installed and available on your `PATH`.

Then, in `backend/ai/ai_manager.py`, make sure `n_gpu_layers` is set to `-1` in the `AIManager` constructor so all model layers are offloaded to the GPU:

```python
def __init__(
        self,
        model_path: str | Path,
        n_ctx: int = 4096,
        n_gpu_layers: int = -1,
        verbose: bool = True,
)
```

## Build (Windows, MSVC + Ninja)

1. Open the **Developer PowerShell for VS** (or the **x64 Native Tools Command Prompt for VS**) — find it in the Start Menu under your Visual Studio version, or launch it via `vcvars64.bat` from your Visual Studio installation directory.

2. Point `CMAKE_PREFIX_PATH` at your Qt installation's MSVC lib directory:

   ```batch
   set CMAKE_PREFIX_PATH=C:\Qt\6.7.2\msvc2019_64
   ```

3. Configure and build:

   ```batch
   cmake -G Ninja -S . -B out\build\Ninja-Release -DCMAKE_BUILD_TYPE=Release
   cmake --build out\build\Ninja-Release
   ```

## Run

1. *(First run only)* Navigate to your Qt installation's `bin` directory, locate `wtv.dll`, and run it against the built executable to deploy the required Qt DLLs:

   ```batch
   wtv.dll out\build\Ninja-Release\NexusAI_Shell.exe
   ```

2. Open a terminal and start the Python backend, leaving it running in the background:

   ```powershell
   cd backend
   python main.py
   ```

3. In a separate terminal, launch NexusAI using `wasmdeployqt.exe` from your Qt installation's `bin` directory:

   ```batch
   wasmdeployqt.exe out\build\Ninja-Release\NexusAI_Shell.exe
   ```
