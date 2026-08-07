"""
Email Context

Maintains the user's current email snapshot during a Nexus session.

Responsibilities
----------------
- Remember the latest email list shown to the user.
- Resolve natural references such as:
    "email 3"
    "the third email"
    "the GitHub email"
    "the one from Coursera"
- Track the currently selected email for follow-up questions.

This module does NOT connect to IMAP.
This module does NOT call the AI.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from api.email.models import EmailMetadata


@dataclass
class EmailContext:
    """
    Stores the current email snapshot and the currently selected email.
    """

    emails: list[EmailMetadata]

    selected_index: Optional[int] = None

    def __init__(self) -> None:
        self.emails = []
        self.selected_index = None

    # ---------------------------------------------------------
    # Snapshot
    # ---------------------------------------------------------

    def update(self, emails: list[EmailMetadata]) -> None:
        """
        Replace the current email snapshot.

        Called whenever Nexus retrieves a fresh unread-email list.
        """

        self.emails = list(emails)

        # A new email snapshot invalidates the previous selection.
        self.selected_index = None

        print(
            f"[EmailContext] Snapshot updated: "
            f"{len(self.emails)} emails"
        )

    def clear(self) -> None:
        """
        Clear the current email context.
        """

        self.emails.clear()
        self.selected_index = None

        print("[EmailContext] Context cleared.")

    # ---------------------------------------------------------
    # Selection
    # ---------------------------------------------------------

    def select(self, index: int) -> Optional[EmailMetadata]:
        """
        Select an email by its displayed number.
        """

        email = self.get_by_index(index)

        if email is None:
            return None

        self.selected_index = index

        print(
            f"[EmailContext] Selected email #{index}: "
            f"{email.subject}"
        )

        return email

    def get_selected(self) -> Optional[EmailMetadata]:
        """
        Return the currently selected email.
        """

        if self.selected_index is None:
            return None

        return self.get_by_index(self.selected_index)

    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------

    def get_by_index(self, index: int) -> Optional[EmailMetadata]:
        """
        Find an email by its displayed number.
        """

        for email in self.emails:
            if email.index == index:
                return email

        return None

    def resolve(self, prompt: str) -> Optional[EmailMetadata]:
        """
        Resolve an email reference from a natural-language prompt.

        Examples:

            "summarize email 3"
            "summarize #3"
            "summarize the third email"
            "summarize the GitHub email"
            "summarize the one from Coursera"
        """

        if not self.emails:
            return None

        # -----------------------------------------------------
        # 1. Explicit numeric reference
        # -----------------------------------------------------

        index = self._extract_index(prompt)

        if index is not None:
            return self.select(index)

        # -----------------------------------------------------
        # 2. Sender / subject matching
        # -----------------------------------------------------

        match = self._match_email(prompt)

        if match is not None:
            return self.select(match.index)

        # -----------------------------------------------------
        # 3. Follow-up reference
        # -----------------------------------------------------

        if self._is_follow_up_reference(prompt):
            selected = self.get_selected()

            if selected is not None:
                print(
                    f"[EmailContext] Using previously selected "
                    f"email #{selected.index}"
                )

                return selected

        return None

    # ---------------------------------------------------------
    # Numeric references
    # ---------------------------------------------------------

    @staticmethod
    def _extract_index(prompt: str) -> Optional[int]:
        lower = prompt.lower()

        # email 3
        # email #3
        # number 3
        # number #3
        # #3
        match = re.search(
            r"(?:email|number)\s*#?\s*([1-9]\d*)\b",
            lower,
        )

        if match:
            return int(match.group(1))

        # #3
        match = re.search(
            r"#\s*([1-9]\d*)\b",
            lower,
        )

        if match:
            return int(match.group(1))

        ordinal_map = {
            "first": 1,
            "second": 2,
            "third": 3,
            "fourth": 4,
            "fifth": 5,
            "sixth": 6,
            "seventh": 7,
            "eighth": 8,
            "ninth": 9,
            "tenth": 10,
        }

        for word, index in ordinal_map.items():
            if re.search(rf"\b{word}\b", lower):
                return index

        return None

    # ---------------------------------------------------------
    # Natural matching
    # ---------------------------------------------------------

    def _match_email(
        self,
        prompt: str,
    ) -> Optional[EmailMetadata]:

        lower = prompt.lower()

        best_match = None
        best_score = 0

        for email in self.emails:

            score = 0

            sender = (email.sender or "").lower()
            subject = (email.subject or "").lower()

            # -------------------------------------------------
            # Sender matching
            # -------------------------------------------------

            sender_tokens = self._tokens(sender)

            for token in sender_tokens:
                if len(token) >= 3 and token in lower:
                    score += 3

            # -------------------------------------------------
            # Subject matching
            # -------------------------------------------------

            subject_tokens = self._tokens(subject)

            for token in subject_tokens:
                if len(token) >= 3 and token in lower:
                    score += 2

            # -------------------------------------------------
            # Exact phrase matching
            # -------------------------------------------------

            if sender and sender in lower:
                score += 5

            if subject and subject in lower:
                score += 5

            if score > best_score:
                best_score = score
                best_match = email

        if best_match is not None:
            print(
                f"[EmailContext] Natural match: "
                f"#{best_match.index} "
                f"(score={best_score})"
            )

        return best_match

    @staticmethod
    def _tokens(value: str) -> list[str]:
        """
        Convert an email sender/subject into useful searchable words.
        """

        return re.findall(
            r"[a-zA-Z0-9@._-]+",
            value,
        )

    # ---------------------------------------------------------
    # Follow-up detection
    # ---------------------------------------------------------

    @staticmethod
    def _is_follow_up_reference(prompt: str) -> bool:
        """
        Detect phrases that commonly refer to the previously selected
        email.
        """

        lower = prompt.lower()

        follow_up_phrases = (
            "that email",
            "this email",
            "the email",
            "that one",
            "this one",
            "the one",
            "it",
            "its",
            "what does it say",
            "what does that say",
            "what do i need to do",
            "what should i do",
            "what action",
            "deadline",
        )

        return any(
            phrase in lower
            for phrase in follow_up_phrases
        )