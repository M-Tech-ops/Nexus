"""
Nexus AI - Email Service

This package provides the backend email functionality for Nexus AI.

Modules
-------
imap_client.py
    Handles low-level IMAP communication.

parser.py
    Parses and cleans email content.

summarizer.py
    Uses the AI manager to summarize emails.

service.py
    High-level interface used by the rest of the backend.
"""

from .service import EmailService

__all__ = ["EmailService"]