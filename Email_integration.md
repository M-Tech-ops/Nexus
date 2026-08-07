# Nexus AI - Email Integration (Phase 1)

> **Feature:** Read unread emails using IMAP and allow the user to request AI-generated summaries.

---

# Objective

Implement the first real-world external service integration for Nexus AI.

The goal is to allow Nexus AI to:

1. Securely connect to a user's email account.
2. Read unread emails.
3. Display a concise list of unread email subjects.
4. Allow the user to choose one (or more) emails.
5. Generate an AI summary of the selected email.

This feature establishes the architecture that future integrations (Calendar, WhatsApp, Slack, Discord, etc.) will follow.

---

# High Level Architecture

```
                User
                  │
                  ▼
      Dynamic Island (Qt/C++)
                  │
             WebSocket
                  │
                  ▼
        FastAPI Backend (Python)
                  │
          Email Service Layer
                  │
                 IMAP
                  │
                  ▼
      Gmail / Outlook / Other
```

---

# Design Philosophy

The frontend **must never** communicate directly with external services.

The frontend only communicates with the backend.

The backend is responsible for:

- Authentication
- Credential management
- Email retrieval
- Email parsing
- AI summarization

This keeps the architecture modular and secure.

---

# Expected User Experience

Example:

### User

> Check my unread emails.

---

### Nexus AI

```
You have 5 unread emails.

1. Amazon
   Your order has shipped.

2. GitHub
   New security alert.

3. Professor Smith
   Assignment deadline reminder.

4. Steam
   Summer Sale is live.

5. Bank
   Monthly account statement.

Would you like me to summarize one of these?
```

---

### User

> Summarize number 3.

---

### Nexus AI

```
Professor Smith reminds you that the assignment deadline
has been extended to Friday.

Key points:

• Deadline moved
• Updated submission portal
• Office hours available Thursday
```

---

# Feature Scope (Phase 1)

The first version should only support:

- Reading unread emails
- Displaying sender
- Displaying subject
- Displaying received date
- Summarizing one selected email

No deleting, replying, forwarding, or composing emails.

---

# Data Flow

```
User

↓

"Check my unread emails"

↓

Frontend

↓

WebSocket

↓

Backend

↓

Email Service

↓

IMAP

↓

Unread emails

↓

Metadata extraction

↓

Frontend

↓

User chooses email

↓

Backend fetches full body

↓

LLM summarizes email

↓

Summary displayed
```

---

# Metadata Returned

Only email metadata should initially be sent to the frontend.

Each email should contain:

```
Sender

Subject

Received Date

Unique Email ID
```

The full email body should **not** be fetched until requested.

This improves:

- Privacy
- Speed
- Bandwidth
- Scalability

---

# Email Cache

After fetching unread emails, keep them cached in memory.

Example:

```
Unread Email Cache

1 -> UID 5821

2 -> UID 5824

3 -> UID 5828

4 -> UID 5831
```

If the user says:

> Summarize number 3

The backend translates:

```
3

↓

UID 5828

↓

Fetch email body

↓

Summarize
```

No additional unread-email search is required.

---

# Backend Components

Suggested structure:

```
backend/

email/

│
├── service.py
├── imap_client.py
├── parser.py
├── summarizer.py
└── models.py
```

---

# Responsibilities

## imap_client.py

Responsible for:

- Connecting to IMAP
- Authentication
- Listing unread emails
- Fetching email bodies

No AI logic.

---

## parser.py

Responsible for:

- HTML → Plain text conversion
- MIME decoding
- Removing signatures
- Removing quoted replies
- Extracting attachments metadata

---

## summarizer.py

Responsible for:

- Prompt engineering
- Sending email text to LLM
- Returning structured summaries

---

## service.py

High-level API.

Example:

```
get_unread_emails()

get_email(uid)

summarize_email(uid)
```

The rest of the backend should only interact with this service.

---

# Security

The project should follow these principles.

## Credentials

Never hardcode credentials.

Never store passwords in plaintext.

Use encrypted credential storage if persistence is added.

---

## Privacy

Never log email contents.

Never save emails to disk without explicit user permission.

Only keep email bodies in memory while required.

---

## Authentication

Long-term recommendation:

Use OAuth 2.0 where supported (e.g., Gmail, Outlook).

For early local development, IMAP with an app password may be acceptable.

---

# Future Expansion

The architecture should support adding:

- Read Inbox
- Search emails
- Starred emails
- Important emails
- Archive
- Delete
- Reply
- Draft emails
- Compose emails

without changing the frontend.

---

# Future AI Capabilities

Eventually Nexus AI should understand requests like:

```
Did I receive anything important today?
```

```
Did my professor reply?
```

```
Any invoices this week?
```

```
Summarize today's emails.
```

Instead of hardcoding commands, the backend should expose tools while the LLM determines the user's intent.

---

# Long-Term Service Architecture

```
Services

├── Email Service
├── Calendar Service
├── WhatsApp Service
├── Discord Service
├── Slack Service
├── Browser Service
├── File Service
└── System Service
```

Each service should expose a clean API to the backend while remaining independent of the frontend.

---

# Current Status

| Task | Status |
|------|--------|
| Feature Design | ✅ Complete |
| Architecture | ✅ Complete |
| Data Flow | ✅ Complete |
| Security Plan | ✅ Complete |
| Backend Structure | ✅ Planned |
| IMAP Integration | ⏳ Pending |
| Email Parsing | ⏳ Pending |
| AI Summarization | ⏳ Pending |
| Frontend Integration | ⏳ Pending |
| OAuth Support | ⏳ Future |

---

# Notes

This feature serves as the first external integration for Nexus AI and establishes the architectural pattern that all future services will follow.

The frontend remains a lightweight UI responsible only for user interaction and displaying results.

The backend owns all business logic, service integrations, authentication, and AI processing.

This separation ensures the project remains modular, secure, maintainable, and easy to extend as Nexus AI evolves into a full desktop AI operating assistant.