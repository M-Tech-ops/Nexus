"""
Central configuration for Nexus AI.

Loads all configuration values from the .env file.

Every service should import configuration
from this module instead of reading environment
variables directly.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# -------------------------------------------------
# Load .env
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Config:
    """
    Application configuration.
    """

    # ==========================
    # AI
    # ==========================

    MODEL_PATH = os.getenv("MODEL_PATH", "")

    # ==========================
    # Email
    # ==========================

    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")

    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

    IMAP_SERVER = os.getenv("IMAP_SERVER", "")

    IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))