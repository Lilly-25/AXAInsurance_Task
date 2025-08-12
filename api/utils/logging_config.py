"""
Logging-Konfiguration für die Titanic API.
Stellt einheitliche Logging-Funktionen bereit.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: bool = True) -> None:
    """
    Konfiguriert das Logging für die Anwendung.

    Args:
        log_level: Logging-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ob Logs in eine Datei geschrieben werden sollen
    """

    # Log-Level setzen
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Log-Format definieren
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Root-Logger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Alle bestehenden Handler entfernen
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console-Handler hinzufügen
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File-Handler hinzufügen (optional)
    if log_file:
        # Log-Verzeichnis erstellen
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Log-Datei mit Datum im Namen
        log_filename = f"titanic_api_{datetime.now().strftime('%Y%m%d')}.log"
        log_filepath = log_dir / log_filename

        file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Bestimmte Logger auf höhere Level setzen um Spam zu vermeiden
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    # Startup-Message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialisiert - Level: {log_level}")
    if log_file:
        logger.info(f"Logs werden geschrieben nach: {log_filepath}")


def get_logger(name: str) -> logging.Logger:
    """
    Erstellt einen Logger mit dem angegebenen Namen.

    Args:
        name: Name des Loggers (normalerweise __name__)

    Returns:
        Konfigurierter Logger
    """
    return logging.getLogger(name)
