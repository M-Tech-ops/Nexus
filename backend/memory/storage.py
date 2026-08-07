"""
Persistent JSON storage for Nexus AI memory.

Responsibilities:
- Create the memory directory if it doesn't exist.
- Create missing JSON files with empty lists.
- Read JSON data.
- Write JSON data safely.

This module does NOT:
- Call the AI.
- Interpret user requests.
- Decide what something means.
- Handle projects/tasks/deadlines directly.

Those responsibilities belong to MemoryService.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JSONStorage:
    """
    Small and reusable JSON storage layer.

    Each JSON file is expected to contain a JSON object or list.
    """

    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)

        # Make sure the directory exists.
        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(
            f"[MemoryStorage] Storage directory: "
            f"{self.base_path.resolve()}"
        )

    # ---------------------------------------------------------
    # File handling
    # ---------------------------------------------------------

    def _get_path(self, filename: str) -> Path:
        """
        Return the full path for a storage file.
        """

        return self.base_path / filename

    def ensure_file(self, filename: str) -> Path:
        """
        Make sure a JSON file exists.

        Missing files are created with an empty list.
        """

        path = self._get_path(filename)

        if not path.exists():
            path.write_text(
                "[]",
                encoding="utf-8",
            )

            print(
                f"[MemoryStorage] Created: {path.name}"
            )

        return path

    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------

    def read(self, filename: str) -> Any:
        """
        Read and deserialize a JSON file.

        Returns:
            Parsed Python object.

        Raises:
            ValueError if the JSON is invalid.
        """

        path = self.ensure_file(filename)

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            return data

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in memory file: {path}"
            ) from exc

    # ---------------------------------------------------------
    # Write
    # ---------------------------------------------------------

    def write(
        self,
        filename: str,
        data: Any,
    ) -> None:
        """
        Serialize and write data to a JSON file.
        """

        path = self._get_path(filename)

        # Make sure the directory still exists.
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            with path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

        except OSError as exc:
            raise OSError(
                f"Could not write memory file: {path}"
            ) from exc

        print(
            f"[MemoryStorage] Saved: {path.name}"
        )

    # ---------------------------------------------------------
    # Convenience
    # ---------------------------------------------------------

    def append(
        self,
        filename: str,
        item: Any,
    ) -> None:
        """
        Append an item to a JSON list.

        If the file doesn't exist, it is created automatically.
        """

        data = self.read(filename)

        if not isinstance(data, list):
            raise ValueError(
                f"Cannot append to {filename}: "
                f"JSON root is not a list."
            )

        data.append(item)

        self.write(
            filename,
            data,
        )

    def delete(
        self,
        filename: str,
        item_id: str,
    ) -> bool:
        """
        Delete an object from a JSON list using its 'id' field.

        Returns:
            True if something was deleted.
            False if no matching ID was found.
        """

        data = self.read(filename)

        if not isinstance(data, list):
            raise ValueError(
                f"Cannot delete from {filename}: "
                f"JSON root is not a list."
            )

        original_length = len(data)

        data = [
            item
            for item in data
            if item.get("id") != item_id
        ]

        if len(data) == original_length:
            return False

        self.write(
            filename,
            data,
        )

        return True