"""
High-level Email Service.

The rest of Nexus AI should ONLY interact with this class.
"""

from core.config import Config
from api.email.imap_client import IMAPClient
from api.email.parser import EmailParser
from api.email.models import EmailMetadata


class EmailService:
    def __init__(self):
        self.client = IMAPClient(
            server=Config.IMAP_SERVER,
            username=Config.EMAIL_ADDRESS,
            password=Config.EMAIL_PASSWORD,
            port=Config.IMAP_PORT,
        )
        self.cache: dict[int, bytes] = {}

    def get_unread_emails(self, limit: int = 10):
        emails = []
        self.client.connect()

        try:
            self.client.select_inbox()
            unread = self.client.list_unread()
            unread = unread[-limit:]
            unread.reverse()

            self.cache.clear()

            for index, uid in enumerate(unread, start=1):
                raw = self.client.fetch_email(uid)
                msg = EmailParser.parse(raw)

                email = EmailMetadata(
                    index=index,
                    uid=uid.decode(),
                    sender=EmailParser.sender(msg),
                    subject=EmailParser.subject(msg),
                    date=EmailParser.date(msg),
                )

                emails.append(email)
                self.cache[index] = uid

        finally:
            self.client.disconnect()

        return emails

    def get_email_by_index(self, index: int) -> tuple[EmailMetadata, str]:
        """Resolve a displayed number to its cached UID and fetch its body."""
        uid = self.cache.get(index)

        if uid is None:
            raise ValueError(
                f"Email #{index} is not available. "
                "Ask Nexus to check the unread emails again."
            )

        self.client.connect()

        try:
            self.client.select_inbox()
            raw = self.client.fetch_email(uid)
            msg = EmailParser.parse(raw)

            metadata = EmailMetadata(
                index=index,
                uid=uid.decode(),
                sender=EmailParser.sender(msg),
                subject=EmailParser.subject(msg),
                date=EmailParser.date(msg),
            )

            return metadata, EmailParser.body(msg)

        finally:
            self.client.disconnect()