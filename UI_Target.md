````markdown
# Nexus AI Desktop UI - Vision & Development Context

> **Project:** Nexus AI
> **Frontend:** Qt (C++)
> **Backend:** FastAPI + Python
> **Communication:** WebSockets
> **LLM:** llama.cpp
> **Current Phase:** UI Refactor (Phase 1)

---

# Goal

The current UI works, but it was designed around displaying a single response.

The goal is to evolve Nexus AI into a modern desktop AI assistant that feels closer to:

- Apple Dynamic Island
- Raycast AI
- Windows Copilot
- ChatGPT Desktop

while keeping the identity of Nexus.

The UI should feel like an operating system feature rather than just another application window.

---

# Core Design Philosophy

The application should have **two personalities**.

## 1. Compact Mode (Dynamic Island)

This is the default state.

It lives at the top-center of the screen as a small floating pill.

Example:

```
        ┌───────────────┐
        │    Nexus AI   │
        └───────────────┘
```

Requirements

- Always on top
- Acrylic blur
- Rounded corners
- Lightweight
- Doesn't block the desktop
- Clicking it expands the assistant
- Clicking again (or outside) collapses it back

This compact state should always remain.

It is the identity of Nexus.

---

## 2. Assistant Panel

When expanded, the Dynamic Island should smoothly animate into a complete AI assistant.

Instead of becoming a popup, it should become a floating assistant panel.

Example

```
┌────────────────────────────────────────────┐
│ Nexus AI                                   │
├────────────────────────────────────────────┤
│                                            │
│ You have 10 unread emails.                 │
│                                            │
│ 1. Coursera                               │
│ 2. Adobe                                  │
│ 3. GitHub                                 │
│                                            │
│ Would you like one summarized?             │
│                                            │
├────────────────────────────────────────────┤
│ > Ask Nexus...                             │
└────────────────────────────────────────────┘
```

---

# UI Requirements

## Keep the Dynamic Island

The Dynamic Island animation should remain exactly as it is.

The only difference is that it expands into a richer assistant.

---

## Smooth Animation

Expand animation

```
Pill

↓

Slight width increase

↓

Height increase

↓

Fade chat

↓

Fade input
```

Collapse animation

```
Panel

↓

Fade content

↓

Shrink height

↓

Shrink width

↓

Return to pill
```

Animations should remain smooth.

---

## Dynamic Height

The current implementation has a fixed expanded height.

Instead:

Minimum height

```
220 px
```

Maximum height

```
650 px
```

Behavior

```
Small response

↓

Small panel

Long response

↓

Panel grows

↓

Maximum reached

↓

Internal scrolling begins
```

---

# Chat Area

The response area should no longer be a QLabel.

Use a QTextBrowser (or equivalent).

Reasons

- Markdown support
- Hyperlinks
- Code blocks
- Rich formatting
- Internal scrolling
- Better future extensibility

---

# Input Bar

The input field should NEVER disappear.

Current

```
Thinking...

(no input)
```

Desired

```
Thinking...

(input disabled)
```

After the response finishes

```
Thinking complete

↓

Input enabled

↓

Cursor automatically focused
```

This allows the user to continue naturally.

---

# Conversation Style

Instead of replacing responses

Current

```
AI Response
```

Desired

```
You

Show unread emails

--------------------

Nexus

You have 10 unread emails...

--------------------

You

Summarize email 3

--------------------

Nexus

Summary...
```

Conversation history should remain visible.

---

# Streaming

Streaming must remain.

As tokens arrive

```
Backend

↓

WebSocket

↓

Qt

↓

Append token

↓

Auto-scroll
```

Do NOT wait for the entire response before displaying it.

Streaming is one of Nexus' strongest features.

---

# Auto Scroll

While streaming

```
append token

↓

scroll to bottom
```

The user should never have to manually scroll during generation.

---

# Backend Integration

The UI should remain completely independent of backend logic.

Current architecture

```
Qt

↓

WebSocket

↓

FastAPI

↓

Tool Router

↓

Services

↓

LLM
```

The frontend should never know

- IMAP
- Gmail
- Calendar
- Browser
- WhatsApp
- Tool Router

It only receives

```
status

token

completed response
```

Nothing else.

---

# Future Backend Tools

The UI must be generic.

Today

```
Email
```

Tomorrow

```
Calendar

Browser

WhatsApp

Files

Notes

Spotify

Discord
```

The frontend should not change when new backend services are added.

---

# Rich Content (Future)

Eventually the backend may send structured UI.

Example

Email Card

```
📧 GitHub

Security Alert

Today 3:42 PM

[Summarize]
[Reply]
[Archive]
```

Calendar

```
Meeting

Tomorrow 2 PM

[Join]

[Snooze]
```

Files

```
project.zip

Open

Delete

Share
```

The UI should be designed so these cards can be added later without redesigning everything.

---

# Markdown

The chat area should support Markdown.

Examples

Headers

Lists

Tables

Code blocks

Inline code

Links

Bold

Italic

This is one of the reasons for replacing QLabel.

---

# Appearance

Dark theme

Rounded corners

Glass / Acrylic

Minimal

Modern

Lots of whitespace

No sharp edges

Feels native to Windows 11.

---

# Performance

The UI should remain lightweight.

Avoid:

- Heavy widgets
- Blocking the UI thread
- Rebuilding the entire document every token

Instead

```
append token

↓

minimal repaint

↓

smooth scrolling
```

---

# Keyboard UX

Enter

```
Send message
```

Shift + Enter

```
New line
```

Escape

```
Collapse back to Dynamic Island
```

Ctrl + L (Future)

```
Clear conversation
```

---

# Conversation Memory

The UI should preserve conversation history.

The backend will maintain semantic memory.

The frontend only displays messages.

Example

```
User

Check emails

↓

Assistant

Lists emails

↓

User

Summarize number 4

↓

Assistant

Summary

↓

User

Reply to it

↓

Assistant
```

The UI should simply render the conversation.

---

# Separation of Responsibilities

Qt Frontend

Responsible for

- Rendering
- Animations
- Streaming
- User interaction

NOT responsible for

- AI
- Email
- Parsing
- Tool selection

---

FastAPI Backend

Responsible for

- Tool routing
- Email service
- Calendar
- Browser
- Memory
- Prompt construction
- LLM interaction

---

LLM

Responsible only for language generation.

---

# Long-Term Vision

Nexus AI should eventually feel like an operating system companion rather than a chatbot.

The user should interact with one persistent assistant capable of:

- Reading emails
- Managing files
- Browsing the web
- Managing calendar events
- Answering questions
- Controlling desktop workflows
- Integrating future tools

without the UI needing major redesigns.

---

# Development Philosophy

When implementing new UI features:

- Prefer extensibility over quick fixes.
- Keep backend and frontend loosely coupled.
- Preserve the Dynamic Island identity.
- Design for future tools, not just today's email integration.
- Ensure every animation and interaction feels smooth and intentional.

The goal is not simply to display AI responses, but to create a polished desktop assistant experience that can scale with Nexus AI as new capabilities are added.
````
