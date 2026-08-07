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

        self.cache = {}

    def get_unread_emails(self, limit: int = 10):

        emails = []

        self.client.connect()
        self.client.select_inbox()

        unread = self.client.list_unread()

        unread = unread[-limit:]

        unread.reverse()

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

        self.client.disconnect()

        return emails