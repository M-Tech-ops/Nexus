"""
tool_router.py

Preprocesses user prompts before they are sent to the LLM.

Responsibilities
----------------
- Detect whether a backend tool is needed.
- Gather context from backend services.
- Inject that context into the prompt.

This module NEVER calls the AI.
"""

from api.email.service import EmailService


class ToolRouter:

    EMAIL_KEYWORDS = {
        "email",
        "emails",
        "mail",
        "gmail",
        "inbox",
        "unread",
        "message",
        "messages",
    }

    def __init__(self):

        self.email = EmailService()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def process_prompt(self, prompt: str) -> str:
        print("================================================")
        print("TOOL ROUTER IS RUNNING")
        print("Prompt:", prompt)
        print("================================================")
        """
        Returns the prompt that should be sent to the LLM.
        """

        print(f"[Router] Prompt: {prompt}")

        if self._needs_email(prompt):
            print("[Router] Email tool selected.")
            return self._process_email(prompt)

        print("[Router] No tool selected.")
        return prompt

    # ---------------------------------------------------------
    # Tool Detection
    # ---------------------------------------------------------

    def _needs_email(self, prompt: str) -> bool:

        prompt = prompt.lower()

        return any(
            keyword in prompt
            for keyword in self.EMAIL_KEYWORDS
        )

    # ---------------------------------------------------------
    # Email
    # ---------------------------------------------------------

    def _process_email(self, user_prompt: str) -> str:

        emails = self.email.get_unread_emails(limit=10)

        print(f"[Router] {len(emails)} unread emails found.")

        return self._build_email_prompt(
            user_prompt,
            emails
        )

    # ---------------------------------------------------------
    # Prompt Builder
    # ---------------------------------------------------------

    def _build_email_prompt(self, user_prompt, emails):

        prompt = """
SYSTEM:

You are Nexus AI.

The following email list was retrieved directly from the user's inbox by the backend.

It is factual.

Never claim that you cannot access emails.

Never ask the user to copy and paste them.

Never state that you lack permissions.

Treat the following email metadata as real information supplied by the system.

Your job is to:

1. Tell the user how many unread emails they have.
2. Present the latest unread emails.
3. Mention any obvious important senders if applicable.
4. Ask the user whether they would like one summarized.
5. Do NOT summarize until asked.

Unread Emails:

"""

        for email in emails:

            prompt += (
                f"{email.index}.\n"
                f"Sender: {email.sender}\n"
                f"Subject: {email.subject}\n"
                f"Date: {email.date}\n\n"
            )

        prompt += f"""

User Request:

{user_prompt}

Respond naturally.
"""

        return prompt