"""
Unit-Tests für die Titanic API.
Testet die Hauptfunktionalitäten der Passagier-Endpunkte.
"""

import pytest
from fastapi.testclient import TestClient
from api.database.connection import init_database
from main import app

# Test-Client erstellen
client = TestClient(app)


class TestPassengerAPI:
    """Test-Klasse für Passagier-Endpunkte"""

    @classmethod
    def setup_class(cls):
        """Setup vor allen Tests - Datenbank initialisieren"""
        try:
            init_database()
        except Exception as e:
            pytest.skip(f"Datenbank nicht verfügbar: {e}")

    def test_health_check(self):
        """Test des Health-Check-Endpunkts"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_redirect(self):
        """Test der Root-URL (sollte zur Dokumentation weiterleiten)"""
        response = client.get("/", allow_redirects=False)
        assert response.status_code == 307  # Temporary Redirect

    def test_get_passengers_default(self):
        """Test des Standard-Passagier-Endpunkts"""
        response = client.get("/api/v1/passengers")
        assert response.status_code == 200

        data = response.json()
        assert "passengers" in data
        assert "total_count" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

        # Standardwerte prüfen
        assert data["page"] == 1
        assert data["page_size"] == 50
        assert len(data["passengers"]) <= 50

    def test_get_passengers_with_pagination(self):
        """Test der Paginierung"""
        # Erste Seite
        response1 = client.get("/api/v1/passengers?page=1&page_size=10")
        assert response1.status_code == 200
        data1 = response1.json()

        # Zweite Seite
        response2 = client.get("/api/v1/passengers?page=2&page_size=10")
        assert response2.status_code == 200
        data2 = response2.json()

        # Verschiedene Passagiere auf verschiedenen Seiten
        if len(data1["passengers"]) > 0 and len(data2["passengers"]) > 0:
            assert data1["passengers"][0] != data2["passengers"][0]

    def test_get_passengers_with_filters(self):
        """Test der Filter-Funktionalität"""
        # Filter nach Überlebenden
        response = client.get("/api/v1/passengers?survived=1")
        assert response.status_code == 200
        data = response.json()

        # Alle zurückgegebenen Passagiere sollten überlebt haben
        for passenger in data["passengers"]:
            assert passenger["survived"] == 1

    def test_get_passengers_invalid_page(self):
        """Test mit ungültiger Seitenzahl"""
        response = client.get("/api/v1/passengers?page=0")
        assert response.status_code == 422  # Validation Error

    def test_get_passengers_invalid_page_size(self):
        """Test mit ungültiger Seitengröße"""
        response = client.get("/api/v1/passengers?page_size=1000")
        assert response.status_code == 422  # Validation Error

    def test_get_statistics(self):
        """Test des Statistik-Endpunkts"""
        response = client.get("/api/v1/passengers/statistics")
        assert response.status_code == 200

        data = response.json()
        required_fields = [
            "total_passengers",
            "survival_rate",
            "survivors",
            "casualties",
            "class_distribution",
            "gender_distribution",
        ]

        for field in required_fields:
            assert field in data

        # Logische Prüfungen
        assert data["total_passengers"] > 0
        assert data["survivors"] + data["casualties"] == data["total_passengers"]
        assert 0 <= data["survival_rate"] <= 100

    def test_get_survival_by_class(self):
        """Test der Überlebensrate nach Klasse"""
        response = client.get("/api/v1/passengers/survival-by-class")
        assert response.status_code == 200

        data = response.json()
        assert "survival_by_class" in data

        # Sollte Daten für alle drei Klassen enthalten
        class_data = data["survival_by_class"]
        assert len(class_data) >= 1

        for class_info in class_data:
            assert "class" in class_info
            assert "total_passengers" in class_info
            assert "survivors" in class_info
            assert "survival_rate" in class_info

    def test_get_survival_by_gender(self):
        """Test der Überlebensrate nach Geschlecht"""
        response = client.get("/api/v1/passengers/survival-by-gender")
        assert response.status_code == 200

        data = response.json()
        assert "survival_by_gender" in data

        gender_data = data["survival_by_gender"]
        assert len(gender_data) >= 1

        for gender_info in gender_data:
            assert "gender" in gender_info
            assert "total_passengers" in gender_info
            assert "survivors" in gender_info
            assert "survival_rate" in gender_info

    def test_get_age_groups(self):
        """Test der Altersgruppen-Analyse"""
        response = client.get("/api/v1/passengers/age-groups")
        assert response.status_code == 200

        data = response.json()
        assert "age_groups" in data

        age_groups = data["age_groups"]
        assert len(age_groups) >= 1

        for age_group in age_groups:
            assert "age_group" in age_group
            assert "total_passengers" in age_group
            assert "survivors" in age_group
            assert "survival_rate" in age_group
            assert "average_age" in age_group


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
