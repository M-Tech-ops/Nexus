"""
parser.py

Responsible for converting raw MIME email messages
into clean Python objects.

Responsibilities
----------------
- MIME decoding
- HTML → Plain text
- Header decoding
- Multipart handling
- Attachment metadata extraction

No networking.
No AI.
"""

from email import message_from_bytes
from email.header import decode_header
from email.message import Message


class EmailParser:

    @staticmethod
    def decode_header_value(value: str) -> str:
        """
        Decode MIME encoded headers.
        """

        if not value:
            return ""

        decoded = decode_header(value)

        parts = []

        for text, encoding in decoded:

            if isinstance(text, bytes):

                parts.append(
                    text.decode(
                        encoding or "utf-8",
                        errors="replace",
                    )
                )

            else:
                parts.append(text)

        return "".join(parts)

    @staticmethod
    def parse(raw_email: bytes) -> Message:
        """
        Convert raw bytes into an email.message.Message.
        """

        return message_from_bytes(raw_email)

    @staticmethod
    def subject(msg: Message) -> str:

        return EmailParser.decode_header_value(
            msg.get("Subject", "")
        )

    @staticmethod
    def sender(msg: Message) -> str:

        return EmailParser.decode_header_value(
            msg.get("From", "")
        )

    @staticmethod
    def date(msg: Message) -> str:

        return msg.get("Date", "")

    @staticmethod
    def body(msg: Message) -> str:
        """
        Extract the plain text body from an email.

        HTML handling will be added later.
        """

        if msg.is_multipart():

            for part in msg.walk():

                content_type = part.get_content_type()

                disposition = str(
                    part.get("Content-Disposition")
                )

                if (
                    content_type == "text/plain"
                    and "attachment" not in disposition
                ):

                    payload = part.get_payload(decode=True)

                    if payload:

                        return payload.decode(
                            errors="replace"
                        )

        else:

            payload = msg.get_payload(decode=True)

            if payload:

                return payload.decode(errors="replace")

        return ""