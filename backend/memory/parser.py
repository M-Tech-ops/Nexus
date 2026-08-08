"""
Memory Parser.

Converts natural-language memory requests into structured
memory operations.

This module does NOT:
- Write JSON files.
- Call MemoryService.
- Call the LLM.
- Modify projects, deadlines, or tasks.

It only identifies the requested memory operation and extracts
the information that can be determined reliably.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class MemoryRequest:
    """
    Structured representation of a memory operation.
    """

    action: str

    # Project information
    name: Optional[str] = None
    description: str = ""

    # Deadline information
    title: Optional[str] = None
    date: Optional[str] = None

    # Task information
    due_date: Optional[str] = None

    # Relationship
    project_name: Optional[str] = None


class MemoryParser:

    # =========================================================
    # Public API
    # =========================================================

    def parse(self, prompt: str) -> Optional[MemoryRequest]:
        """
        Parse a user prompt into a MemoryRequest.

        Returns None when the prompt does not appear to contain
        a memory operation.
        """

        if not prompt or not prompt.strip():
            return None

        prompt = prompt.strip()

        # Order matters.
        #
        # A deadline can also contain words like "project",
        # so check deadlines before generic project creation.

        deadline = self._parse_deadline(prompt)

        if deadline:
            return deadline

        task = self._parse_task(prompt)

        if task:
            return task

        project = self._parse_project(prompt)

        if project:
            return project

        return None

    # =========================================================
    # Intent Detection
    # =========================================================

    def _looks_like_memory_request(self, prompt: str) -> bool:
        """
        Determine whether the user appears to be asking Nexus
        to remember something.
        """

        lower = prompt.lower()

        memory_keywords = (
            "remember",
            "keep in mind",
            "keep track",
            "save this",
            "store this",
            "don't forget",
            "do not forget",
            "deadline",
            "task",
            "project",
        )

        return any(
            keyword in lower
            for keyword in memory_keywords
        )

    # =========================================================
    # Project
    # =========================================================

    def _parse_project(
        self,
        prompt: str,
    ) -> Optional[MemoryRequest]:

        lower = prompt.lower()

        if not self._looks_like_memory_request(prompt):
            return None

        project_patterns = [
            r"(?:remember|save|store)\s+(?:that\s+)?(?:i(?:'m| am)\s+)?(?:am\s+)?working\s+on\s+(?:a\s+)?(?:new\s+)?project\s+(?:called\s+)?(.+)",
            r"(?:remember|save|store)\s+(?:that\s+)?(?:my\s+)?project\s+(?:is\s+)?(?:called\s+)?(.+)",
            r"(?:i\s+)?(?:just\s+)?started\s+(?:working\s+on\s+)?(?:a\s+)?project\s+(?:called\s+)?(.+)",
        ]

        for pattern in project_patterns:

            match = re.search(
                pattern,
                lower,
                re.IGNORECASE,
            )

            if not match:
                continue

            name = match.group(1).strip()

            name = self._clean_name(name)

            if not name:
                return None

            return MemoryRequest(
                action="create_project",
                name=name,
            )

        return None

    # =========================================================
    # Deadline
    # =========================================================

    def _parse_deadline(
        self,
        prompt: str,
    ) -> Optional[MemoryRequest]:

        lower = prompt.lower()

        if "deadline" not in lower:
            return None

        date = self._extract_date(prompt)

        if not date:
            # We know it's probably a deadline request,
            # but we don't have a reliable date.
            return MemoryRequest(
                action="add_deadline",
                title=self._extract_deadline_title(prompt),
            )

        title = self._extract_deadline_title(prompt)
        project_name = self._extract_project_name(prompt)

        return MemoryRequest(
            action="add_deadline",
            title=title,
            date=date,
            project_name=project_name,
        )

    # =========================================================
    # Task
    # =========================================================

    def _parse_task(
        self,
        prompt: str,
    ) -> Optional[MemoryRequest]:

        lower = prompt.lower()

        task_keywords = (
            "task",
            "todo",
            "to-do",
            "need to",
            "have to",
            "should do",
        )

        if not any(
            keyword in lower
            for keyword in task_keywords
        ):
            return None

        title = None

        patterns = [
            r"(?:remember\s+)?(?:the\s+)?task\s+(?:is\s+)?(.+)",
            r"(?:remember\s+)?(?:i\s+)?need\s+to\s+(.+)",
            r"(?:remember\s+)?(?:i\s+)?have\s+to\s+(.+)",
            r"(?:remember\s+)?(?:i\s+)?should\s+(.+)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                lower,
                re.IGNORECASE,
            )

            if match:
                title = match.group(1).strip()
                break

        if not title:
            return None

        due_date = self._extract_date(prompt)
        project_name = self._extract_project_name(prompt)

        return MemoryRequest(
            action="add_task",
            title=self._clean_name(title),
            due_date=due_date,
            project_name=project_name,
        )

    # =========================================================
    # Date Extraction
    # =========================================================

    def _extract_date(
        self,
        prompt: str,
    ) -> Optional[str]:

        # YYYY-MM-DD
        match = re.search(
            r"\b(20\d{2})-(\d{1,2})-(\d{1,2})\b",
            prompt,
        )

        if match:
            year, month, day = match.groups()

            return (
                f"{int(year):04d}-"
                f"{int(month):02d}-"
                f"{int(day):02d}"
            )

        # DD/MM/YYYY
        match = re.search(
            r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b",
            prompt,
        )

        if match:
            day, month, year = match.groups()

            return (
                f"{int(year):04d}-"
                f"{int(month):02d}-"
                f"{int(day):02d}"
            )

        # DD Month YYYY
        months = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }

        month_pattern = "|".join(months.keys())

        match = re.search(
            rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+"
            rf"({month_pattern})"
            rf"(?:\s+(20\d{{2}}))?\b",
            prompt.lower(),
        )

        if match:
            day = int(match.group(1))
            month = months[match.group(2)]

            year = match.group(3)

            if not year:
                # Don't guess the year here.
                # The higher layer can resolve a missing year.
                return None

            return (
                f"{int(year):04d}-"
                f"{month:02d}-"
                f"{day:02d}"
            )

        # Month DD YYYY
        match = re.search(
            rf"\b({month_pattern})\s+"
            rf"(\d{{1,2}})(?:st|nd|rd|th)?"
            rf"(?:\s+(20\d{{2}}))?\b",
            prompt.lower(),
        )

        if match:
            month = months[match.group(1)]
            day = int(match.group(2))
            year = match.group(3)

            if not year:
                return None

            return (
                f"{int(year):04d}-"
                f"{month:02d}-"
                f"{day:02d}"
            )

        return None

    # =========================================================
    # Project Name Extraction
    # =========================================================

    def _extract_project_name(
        self,
        prompt: str,
    ) -> Optional[str]:

        patterns = [
            r"(?:for|on|of)\s+(?:the\s+)?"
            r"([A-Za-z0-9][A-Za-z0-9 _-]{1,50}?)"
            r"\s+project\b",

            r"(?:project)\s+"
            r"([A-Za-z0-9][A-Za-z0-9 _-]{1,50}?)"
            r"(?:\s+deadline|\s+task|\s+due|\s+on\b|$)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                prompt,
                re.IGNORECASE,
            )

            if match:
                return self._clean_name(
                    match.group(1)
                )

        return None

    # =========================================================
    # Deadline Title
    # =========================================================

    def _extract_deadline_title(
        self,
        prompt: str,
    ) -> str:

        project_name = self._extract_project_name(prompt)

        if project_name:
            return f"{project_name} deadline"

        lower = prompt.lower()

        match = re.search(
            r"deadline\s+(?:for|of)\s+(.+?)(?:\s+on\s+|\s+by\s+|\s+due\s+|$)",
            lower,
        )

        if match:
            return self._clean_name(
                match.group(1)
            )

        return "Deadline"

    # =========================================================
    # Cleanup
    # =========================================================

    @staticmethod
    def _clean_name(value: str) -> str:
        """
        Clean extracted names/titles.
        """

        value = value.strip()

        value = re.sub(
            r"[.!?,]+$",
            "",
            value,
        )

        return value.strip()