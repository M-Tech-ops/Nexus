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
import shutil
import tempfile
import logging

logger = logging.getLogger("NexusAI.Config")

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

    MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "llama-3.2-3b-instruct.gguf"))

    # ==========================
    # Email
    # ==========================

    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")

    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

    IMAP_SERVER = os.getenv("IMAP_SERVER", "")

    IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))

    # ==========================
    # Storage Paths
    # ==========================

    # Persistent storage for tasks, projects, deadlines ("tasks and stuff")
    NEXUS_DATA_DIR = Path(
        os.getenv("NEXUS_DATA_DIR", Path.home() / "Documents" / "Nexus")
    )

    # Ephemeral storage for conversation history
    NEXUS_TEMP_DIR = Path(
        os.getenv("NEXUS_TEMP_DIR", Path(tempfile.gettempdir()) / "Nexus")
    )

    TASKS_DIR = NEXUS_DATA_DIR / "tasks"
    TASKS_FILE = TASKS_DIR / "agent_tasks.json"

    MEMORY_DIR = NEXUS_DATA_DIR / "memory"

    HISTORY_DIR = NEXUS_TEMP_DIR / "conversations"
    HISTORY_FILE = HISTORY_DIR / "history.json"

    @classmethod
    def ensure_storage_directories(cls) -> None:
        """
        Ensure storage directories exist and migrate any existing legacy
        data files to the new locations if not already present.
        """
        cls.TASKS_DIR.mkdir(parents=True, exist_ok=True)
        cls.MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        cls.HISTORY_DIR.mkdir(parents=True, exist_ok=True)

        legacy_data_dir = BASE_DIR / "data"

        # Migrate tasks if not yet created in Documents/Nexus
        legacy_tasks = legacy_data_dir / "tasks" / "agent_tasks.json"
        if not cls.TASKS_FILE.exists() and legacy_tasks.exists():
            try:
                shutil.copy2(legacy_tasks, cls.TASKS_FILE)
                logger.info(f"Migrated agent tasks to: {cls.TASKS_FILE}")
            except Exception as e:
                logger.warning(f"Failed to migrate tasks file: {e}")

        # Migrate memory files (projects.json, deadlines.json, tasks.json)
        legacy_memory = legacy_data_dir / "memory"
        if legacy_memory.exists():
            for json_file in legacy_memory.glob("*.json"):
                target_file = cls.MEMORY_DIR / json_file.name
                if not target_file.exists():
                    try:
                        shutil.copy2(json_file, target_file)
                        logger.info(f"Migrated memory file to: {target_file}")
                    except Exception as e:
                        logger.warning(f"Failed to migrate {json_file.name}: {e}")

        # Migrate existing conversation history if any exists and target does not
        if not cls.HISTORY_FILE.exists():
            legacy_history = legacy_data_dir / "conversations" / "history.json"
            legacy_api_history = BASE_DIR / "api" / "data" / "conversations" / "history.json"
            source_history = None
            if legacy_history.exists():
                source_history = legacy_history
            elif legacy_api_history.exists():
                source_history = legacy_api_history

            if source_history and source_history.exists():
                try:
                    shutil.copy2(source_history, cls.HISTORY_FILE)
                    logger.info(f"Migrated history to temp: {cls.HISTORY_FILE}")
                except Exception as e:
                    logger.warning(f"Failed to migrate history file: {e}")