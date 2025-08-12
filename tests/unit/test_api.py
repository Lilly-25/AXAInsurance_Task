"""
Unit Tests für die Titanic API.
Testet einzelne Komponenten isoliert.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from api.database.connection import get_db_config, execute_query
from api.models.passenger import PassengerResponse


class TestDatabaseConnection:
    """Tests für Datenbankverbindung."""

    def test_get_db_config_default_values(self):
        """Test Standard-Datenbankkonfiguration ohne DB_PASSWORD (sollte None sein)."""
        with patch.dict("os.environ", {}, clear=True):
            config = get_db_config()
            assert config["host"] == "localhost"
            assert config["port"] == "5432"
            assert config["database"] == "titanic"
            assert config["user"] == "postgres"
            assert config["password"] is None  # Kein Default mehr - sicherer!

    def test_get_db_config_environment_variables(self):
        """Test Konfiguration aus Umgebungsvariablen."""
        env_vars = {
            "DB_HOST": "test-host",
            "DB_PORT": "5433",
            "DB_NAME": "test-db",
            "DB_USER": "test-user",
            "DB_PASSWORD": "test-pass",
        }
        with patch.dict("os.environ", env_vars):
            config = get_db_config()
            assert config["host"] == "test-host"
            assert config["port"] == "5433"
            assert config["database"] == "test-db"
            assert config["user"] == "test-user"
            assert config["password"] == "test-pass"


class TestPassengerModels:
    """Tests für Passagier-Datenmodelle."""

    def test_passenger_response_model(self):
        """Test PassengerResponse Pydantic Model."""
        passenger_data = {
            "survived": 1,
            "pclass": 1,
            "sex": "female",
            "age": 29.0,
            "sibsp": 0,
            "parch": 0,
            "fare": 71.2833,
            "adult_male": False,
            "alone": True,
            "embarked": "C",
            "passenger_class": "First",
            "who": "woman",
            "deck": "B",
            "embark_town": "Cherbourg",
            "alive": "yes",
        }

        passenger = PassengerResponse(**passenger_data)
        assert passenger.survived == 1
        assert passenger.pclass == 1
        assert passenger.sex == "female"
        assert passenger.age == 29.0
        assert passenger.adult_male is False
        assert passenger.alone is True

    def test_passenger_response_optional_fields(self):
        """Test PassengerResponse mit optionalen Feldern."""
        minimal_data = {
            "survived": 0,
            "pclass": 3,
            "sex": "male",
            "sibsp": 1,
            "parch": 0,
            "fare": 7.25,
            "adult_male": True,
            "alone": False,
        }

        passenger = PassengerResponse(**minimal_data)
        assert passenger.survived == 0
        assert passenger.age is None
        assert passenger.embarked is None


class TestQueryBuilding:
    """Tests für SQL-Query-Generierung."""

    @patch("api.database.connection.execute_query")
    def test_basic_query_execution(self, mock_execute):
        """Test grundlegende Query-Ausführung."""
        # Mock-Rückgabe
        mock_execute.return_value = [
            (
                1,
                1,
                "female",
                29.0,
                0,
                0,
                71.28,
                False,
                True,
                "C",
                "First",
                "woman",
                "B",
                "Cherbourg",
                "yes",
            )
        ]

        # Query ausführen
        result = execute_query("SELECT * FROM passengers LIMIT 1", ())

        # Überprüfungen
        mock_execute.assert_called_once_with("SELECT * FROM passengers LIMIT 1", ())
        assert len(result) == 1
        assert result[0][0] == 1  # survived
        assert result[0][2] == "female"  # sex


class TestValidationLogic:
    """Tests für Validierungslogik."""

    def test_age_validation(self):
        """Test Altersvalidierung."""
        # Gültige Altersangaben
        valid_ages = [0, 1, 25, 80, 100]
        for age in valid_ages:
            passenger = PassengerResponse(
                survived=1,
                pclass=1,
                sex="female",
                age=age,
                sibsp=0,
                parch=0,
                fare=10.0,
                adult_male=False,
                alone=True,
            )
            assert passenger.age == age

    def test_class_validation(self):
        """Test Klassenvalidierung."""
        # Gültige Klassen
        valid_classes = [1, 2, 3]
        for pclass in valid_classes:
            passenger = PassengerResponse(
                survived=1,
                pclass=pclass,
                sex="female",
                sibsp=0,
                parch=0,
                fare=10.0,
                adult_male=False,
                alone=True,
            )
            assert passenger.pclass == pclass

    def test_sex_validation(self):
        """Test Geschlechtsvalidierung."""
        # Gültige Geschlechter
        valid_sexes = ["male", "female"]
        for sex in valid_sexes:
            passenger = PassengerResponse(
                survived=1,
                pclass=1,
                sex=sex,
                sibsp=0,
                parch=0,
                fare=10.0,
                adult_male=(sex == "male"),
                alone=True,
            )
            assert passenger.sex == sex


class TestUtilityFunctions:
    """Tests für Hilfsfunktionen."""

    def test_boolean_conversion(self):
        """Test Boolean-Konvertierung."""
        # Test verschiedene Boolean-Werte
        test_cases = [
            (True, True),
            (False, False),
            (1, True),
            (0, False),
            ("true", True),
            ("false", False),
        ]

        for input_val, expected in test_cases:
            passenger = PassengerResponse(
                survived=1,
                pclass=1,
                sex="female",
                sibsp=0,
                parch=0,
                fare=10.0,
                adult_male=bool(input_val),
                alone=True,
            )
            assert passenger.adult_male == expected


# Pytest-Konfiguration
@pytest.fixture
def client():
    """Test-Client für FastAPI."""
    from main import app

    return TestClient(app)


def pytest_configure(config):
    """Pytest-Konfiguration."""
    config.addinivalue_line("markers", "unit: unit tests")
