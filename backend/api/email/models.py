"""
Email models used throughout the Email Service.
"""

from dataclasses import dataclass


@dataclass
class EmailMetadata:
    """
    Metadata shown to the user.
    """

    index: int
    uid: str

    sender: str
    subject: str
    date: str