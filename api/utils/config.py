"""
Konfigurationsmodul für die Titanic API.
Verwaltet Umgebungsvariablen und Anwendungseinstellungen.
"""

import os
from typing import Optional


class Settings:
    """
    Anwendungseinstellungen.
    Lädt Konfiguration aus Umgebungsvariablen.
    """
    
    def __init__(self):
        # API-Konfiguration
        self.app_name = os.getenv("APP_NAME", "Titanic Passagier API")
        self.version = os.getenv("VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Server-Konfiguration
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        
        # Datenbank-Konfiguration
        self.database_url = os.getenv("DATABASE_URL", "data/titanic.db")
        
        # Logging-Konfiguration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # API-Limits
        self.max_page_size = int(os.getenv("MAX_PAGE_SIZE", "500"))
        self.default_page_size = int(os.getenv("DEFAULT_PAGE_SIZE", "50"))
        
        # CORS-Konfiguration
        cors_origins_str = os.getenv("CORS_ORIGINS", "*")
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
        
        # Security
        allowed_hosts_str = os.getenv("ALLOWED_HOSTS", "*")
        self.allowed_hosts = [host.strip() for host in allowed_hosts_str.split(",")]


# Globale Settings-Instanz
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency für FastAPI zum Abrufen der Einstellungen.
    """
    return settings
