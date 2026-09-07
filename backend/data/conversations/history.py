from __future__ import annotations
"""
Conversation History

Stores recent user/assistant messages in JSON so Nexus AI
can maintain conversational context across requests and restarts.

This is NOT persistent semantic memory.

Persistent facts:
    data/memory/

Conversation context:
    data/conversation/
"""
""" We can convert  the max_messages to be dynamic based on the context window length"""



import json
from pathlib import Path
from typing import List, Dict, Optional

from core.config import Config


class ConversationHistory:

    def __init__(
        self,
        storage_path: Optional[str | Path] = None,
        max_messages: int = 10,
    ) -> None:

        self.storage_path = Path(storage_path) if storage_path is not None else Config.HISTORY_FILE
        self.max_messages = max_messages

        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.messages: List[Dict[str, str]] = []

        self._load()

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    def _load(self) -> None:

        if not self.storage_path.exists() or self.storage_path.stat().st_size == 0:
            self.messages = []
            self._save()
            return

        try:
            with self.storage_path.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if isinstance(data, dict):
                messages = data.get("messages", [])

                if isinstance(messages, list):
                    self.messages = [
                        message
                        for message in messages
                        if self._valid_message(message)
                    ]

            self._trim()

        except (json.JSONDecodeError, OSError) as exc:

            print(
                f"[Conversation] Failed to load history: {exc}"
            )

            self.messages = []

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    def _save(self) -> None:

        try:

            with self.storage_path.open(
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    {
                        "messages": self.messages
                    },
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

        except OSError as exc:

            print(
                f"[Conversation] Failed to save history: {exc}"
            )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    @staticmethod
    def _valid_message(message) -> bool:

        return (
            isinstance(message, dict)
            and message.get("role") in {"user", "assistant"}
            and isinstance(message.get("content"), str)
        )

    # ---------------------------------------------------------
    # Add messages
    # ---------------------------------------------------------

    def add_user_message(self, content: str) -> None:

        self.messages.append(
            {
                "role": "user",
                "content": content,
            }
        )

        self._trim()
        self._save()

    def add_assistant_message(self, content: str) -> None:

        self.messages.append(
            {
                "role": "assistant",
                "content": content,
            }
        )

        self._trim()
        self._save()

    # ---------------------------------------------------------
    # Context
    # ---------------------------------------------------------

    def get_messages(self) -> List[Dict[str, str]]:

        return list(self.messages)

    # ---------------------------------------------------------
    # Limit history
    # ---------------------------------------------------------

    def _trim(self) -> None:

        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self) -> None:

        self.messages = []
        self._save()