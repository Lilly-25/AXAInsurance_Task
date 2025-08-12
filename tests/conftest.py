"""
Pytest-Konfiguration und Fixtures für Tests.
Setzt Umgebungsvariablen und gemeinsame Test-Utilities.
"""

import pytest
import os
import asyncio
from typing import Generator


# Umgebungsvariablen für Tests setzen
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Umgebungsvariablen für Tests konfigurieren."""
    test_env = {
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": os.getenv("DB_PORT", "5432"),
        "DB_NAME": os.getenv("DB_NAME", "titanic"),
        "DB_USER": os.getenv("DB_USER", "postgres"),
        "DB_PASSWORD": os.getenv(
            "DB_PASSWORD"
        ),  # Kein Default - muss über Umgebung gesetzt werden!
        "LOG_LEVEL": "ERROR",  # Reduziere Logs in Tests
        "DEBUG": "false",
    }

    # Umgebungsvariablen setzen
    for key, value in test_env.items():
        os.environ[key] = value

    yield

    # Cleanup nach Tests (optional)
    pass


@pytest.fixture(scope="session")
def event_loop():
    """Event Loop für async Tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def api_base_url() -> str:
    """Base URL für API-Tests."""
    return "http://localhost:8000"


@pytest.fixture
def sample_passenger_data() -> dict:
    """Beispiel-Passagierdaten für Tests."""
    return {
        "survived": 1,
        "pclass": 1,
        "sex": "female",
        "age": 29.0,
        "sibsp": 0,
        "parch": 0,
        "fare": 211.3375,
        "adult_male": False,
        "alone": True,
        "embarked": "S",
        "passenger_class": "First",
        "who": "woman",
        "deck": "B",
        "embark_town": "Southampton",
        "alive": "yes",
    }


# Test-spezifische Marker
def pytest_configure(config):
    """Pytest-Konfiguration."""
    config.addinivalue_line(
        "markers", "requires_db: Tests die eine Datenbankverbindung benötigen"
    )
    config.addinivalue_line(
        "markers", "requires_api: Tests die eine laufende API benötigen"
    )
