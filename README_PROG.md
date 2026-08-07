# Nexus AI

> A local-first, privacy-focused desktop AI assistant with a modern Dynamic Island inspired interface.

---

# Vision

Nexus AI aims to become a fully local desktop AI assistant capable of understanding your computer, interacting with applications, automating tasks, and serving as an intelligent operating system companion.

Unlike cloud-based assistants, Nexus AI is designed to run **locally**, giving users complete ownership of their data while providing low-latency AI interactions.

The long-term goal is to create something comparable to:

- ChatGPT Desktop
- Apple Intelligence
- Raycast AI
- Windows Copilot

while remaining fully local and extensible.

---

# Current Tech Stack

## Frontend

- C++20
- Qt 6
- Windows Acrylic Blur
- Dynamic Island UI
- QWebSocket

## Backend

- Python
- FastAPI
- WebSockets
- Local LLM
- Streaming responses

---

# Current Architecture

```
                 User
                   │
                   ▼
        DynamicIslandWindow
                   │
        promptRequested(QString)
                   │
                   ▼
          WebSocketClient.cpp
                   │
          ws://127.0.0.1:8000/ws
                   │
                   ▼
             FastAPI Backend
                   │
             Local LLM Model
                   │
        Streamed Tokens + States
                   │
                   ▼
          WebSocketClient.cpp
                   │
                   ▼
        DynamicIslandWindow
```

---

# Project Structure

```
NexusAI/

│
├── backend/
│   ├── main.py
│   ├── server.py
│   ├── model.py
│   └── requirements.txt
│
├── DynamicIslandWindow.cpp
├── DynamicIslandWindow.h
│
├── WebSocketClient.cpp
├── WebSocketClient.h
│
├── main.cpp
│
├── CMakeLists.txt
└── README.md
```

---

# Current Features

## UI

- Frameless window
- Acrylic Glass Effect
- Rounded corners
- Always on top
- Smooth geometry animations
- Dynamic Island style interface

---

## Backend

- FastAPI server
- WebSocket communication
- Local model loading
- Token streaming
- Response completion

---

## Communication

Current communication protocol:

### Client → Server

```json
{
    "type": "prompt",
    "text": "Hello"
}
```

---

### Server → Client

State updates

```json
{
    "type":"state",
    "value":"compact"
}
```

Streaming token

```json
{
    "type":"token",
    "text":"Hello"
}
```

Final response

```json
{
    "type":"response",
    "text":"Hello World"
}
```

Idle

```json
{
    "type":"state",
    "value":"idle"
}
```

---

# Current State Machine

Current implementation

```
Idle

↓

Input

↓

Compact (Listening)

↓

Expanded (Thinking)

↓

Idle
```

Planned implementation

```
Idle

↓

Input

↓

Listening

↓

Thinking

↓

Streaming

↓

Response

↓

Idle
```

---

# Development Progress

## Completed

### Backend

- FastAPI server
- WebSocket endpoint
- JSON protocol
- Streaming architecture
- Local LLM integration

---

### Frontend

- Dynamic Island window
- Acrylic blur
- Geometry animations
- Prompt input
- WebSocket client
- Streaming architecture

---

### Networking

Verified:

- Frontend connects
- Backend accepts connection
- Prompt reaches backend
- Backend generates response
- Backend streams tokens
- Frontend receives every token
- Frontend receives final response

The networking stack is considered **fully operational**.

---

# Current Known Issues

## UI

The remaining bugs are entirely inside:

```
DynamicIslandWindow.cpp
```

### Known issues

- Response label visibility
- State transitions
- Layout resizing
- Response rendering
- Idle transition timing

The backend and networking are functioning correctly.

---

# Debug Logs

Temporary debug statements currently in the project.

## DynamicIslandWindow

```cpp
qDebug() << "Emitting prompt:" << prompt;
```

---

## WebSocketClient

```cpp
qDebug() << "sendPrompt called";
```

```cpp
qDebug() << "Connected:" << isConnected();
```

```cpp
qDebug() << "Sending:" << text;
```

```cpp
qDebug() << QJsonDocument(obj).toJson(...);
```

---

Incoming messages

```cpp
qDebug() << "RAW MESSAGE:" << message;
```

These should be removed or wrapped behind a debug flag before release.

---

# Verified Working Flow

```
User clicks Dynamic Island

↓

Input box appears

↓

User enters prompt

↓

Prompt emitted

↓

WebSocket sends JSON

↓

FastAPI receives prompt

↓

LLM generates response

↓

Tokens stream

↓

Qt receives tokens

↓

Qt receives final response
```

Current issue:

```
Tokens are received correctly

↓

UI does not properly render them
```

---

# Immediate Next Tasks

## High Priority

- Fix response rendering
- Fix response label visibility
- Improve state transitions
- Introduce dedicated Response state

---

## Medium Priority

- Markdown rendering
- Code block rendering
- Syntax highlighting
- Copy buttons

---

## Future Features

### AI

- Multi-model support
- Model switching
- Tool calling
- Function calling
- Agent framework

---

### Desktop Integration

- File search
- Application launching
- Email integration
- Calendar integration
- Browser automation
- WhatsApp integration
- Clipboard history

(All integrations will require explicit user permission.)

---

### Voice

- Speech-to-text
- Text-to-speech
- Wake word
- Voice conversations

---

### Productivity

- Conversation history
- Search conversations
- Memory system
- Plugin system
- Settings page

---

# Design Philosophy

Nexus AI follows a few core principles.

- Privacy first
- Local-first AI
- Native desktop performance
- Beautiful minimal UI
- Streaming responses
- Extensible architecture
- Modular backend
- Clean separation between UI and AI logic

The frontend should never contain AI logic.

The backend should never contain UI logic.

Communication should happen exclusively through WebSockets.

---

# Long-Term Vision

Nexus AI is intended to evolve into a complete desktop AI operating companion capable of:

- Running local LLMs (Llama, Qwen, DeepSeek, Gemma, etc.)
- Understanding files and documents
- Desktop automation
- Intelligent search
- Voice interaction
- Multimodal AI
- Plugin ecosystem
- Modern native UI
- Full offline capability where possible

The architecture is intentionally modular so that models, tools, and interfaces can evolve independently without requiring major rewrites.

---

# Current Status

| Component | Status |
|-----------|--------|
| Dynamic Island UI | ✅ Working |
| Animations | ✅ Working |
| Acrylic Blur | ✅ Working |
| WebSocket Client | ✅ Working |
| FastAPI Backend | ✅ Working |
| Streaming Protocol | ✅ Working |
| Local LLM | ✅ Working |
| Prompt Input | ✅ Working |
| Token Streaming | ✅ Working |
| Response Rendering | 🚧 In Progress |
| Voice Support | ⏳ Planned |
| Desktop Automation | ⏳ Planned |
| Tool Calling | ⏳ Planned |
| Memory System | ⏳ Planned |

---

# License

This project is currently under active development.
License will be decided before the first public release.