"""
imap_client.py

Low-level IMAP client for Nexus AI.

Responsibilities
----------------
- Connect to IMAP server
- Authenticate user
- List unread emails
- Fetch email by UID
- Logout

This module should NOT perform:
- AI summarization
- MIME parsing
- HTML cleaning
"""

import imaplib
from typing import List
from core.config import Config

class IMAPClient:
    """
    Simple wrapper around Python's imaplib.
    """

    def __init__(
        self,
        server: str,
        username: str,
        password: str,
        port: int = 993,
    ):
        self.server = server
        self.port = port
        self.username = username
        self.password = password

        self.connection: imaplib.IMAP4_SSL | None = None

    # ---------------------------------------------------------
    # Connection
    # ---------------------------------------------------------

    def connect(self) -> None:
        """
        Connect to the IMAP server and authenticate.
        """

        self.connection = imaplib.IMAP4_SSL(self.server, self.port)
        self.connection.login(self.username, self.password)

    # ---------------------------------------------------------
    # Mailbox
    # ---------------------------------------------------------

    def select_inbox(self) -> None:
        """
        Select the INBOX mailbox.
        """

        if self.connection is None:
            raise RuntimeError("IMAP client is not connected.")

        self.connection.select("INBOX")

    # ---------------------------------------------------------
    # Fetch unread emails
    # ---------------------------------------------------------

    def list_unread(self) -> List[bytes]:
        """
        Returns a list of unread email UIDs.
        """

        if self.connection is None:
            raise RuntimeError("IMAP client is not connected.")

        status, data = self.connection.uid(
            "search",
            None,
            "UNSEEN",
        )

        if status != "OK":
            return []

        return data[0].split()

    # ---------------------------------------------------------
    # Fetch email
    # ---------------------------------------------------------

    def fetch_email(self, uid: bytes) -> bytes:
        if self.connection is None:
            raise RuntimeError("IMAP client is not connected.")

        status, data = self.connection.uid(
            "fetch",
            uid,
            "(RFC822)",
    )

        if status != "OK":
            raise RuntimeError(f"Failed to fetch email UID {uid.decode()}")

        return data[0][1]

    # ---------------------------------------------------------
    # Logout
    # ---------------------------------------------------------

    def disconnect(self) -> None:
        """
        Close the connection cleanly.
        """

        if self.connection is None:
            return

        try:
            self.connection.close()
        except Exception:
            pass

        self.connection.logout()
        self.connection = None