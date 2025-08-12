"""
Integration Tests für die Titanic API.
Testet das Zusammenspiel aller Komponenten mit echter Datenbank.
"""

import pytest
import httpx
import asyncio
import os
from typing import Dict, Any

# Test-Konfiguration
API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30


class TestAPIEndpoints:
    """Integration Tests für API-Endpunkte."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test Health-Check Endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "message" in data
    
    @pytest.mark.asyncio
    async def test_get_passengers_basic(self):
        """Test grundlegende Passagier-Abfrage."""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/passengers?limit=10")
            
            assert response.status_code == 200
            data = response.json()
            
            # Struktur prüfen
            assert "passengers" in data
            assert "total_count" in data
            assert "returned_count" in data
            assert "offset" in data
            assert "limit" in data
            
            # Daten prüfen
            assert len(data["passengers"]) <= 10
            assert data["total_count"] > 0
            assert data["returned_count"] == len(data["passengers"])
    
    @pytest.mark.asyncio
    async def test_get_passengers_with_filters(self):
        """Test Passagier-Abfrage mit Filtern."""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test Überlebensfilter
            response = await client.get(f"{API_BASE_URL}/api/v1/passengers?survived=true&limit=5")
            assert response.status_code == 200
            data = response.json()
            
            # Alle zurückgegebenen Passagiere sollten überlebt haben
            for passenger in data["passengers"]:
                assert passenger["survived"] == 1
    
    @pytest.mark.asyncio
    async def test_get_passengers_class_filter(self):
        """Test Klassenfilter."""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test erste Klasse
            response = await client.get(f"{API_BASE_URL}/api/v1/passengers?pclass=1&limit=5")
            assert response.status_code == 200
            data = response.json()
            
            # Alle sollten erste Klasse sein
            for passenger in data["passengers"]:
                assert passenger["pclass"] == 1
    
    @pytest.mark.asyncio
    async def test_get_passengers_pagination(self):
        """Test Paginierung."""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Erste Seite
            response1 = await client.get(f"{API_BASE_URL}/api/v1/passengers?limit=5&offset=0")
            assert response1.status_code == 200
            data1 = response1.json()
            
            # Zweite Seite
            response2 = await client.get(f"{API_BASE_URL}/api/v1/passengers?limit=5&offset=5")
            assert response2.status_code == 200
            data2 = response2.json()
            
            # Verschiedene Passagiere
            passenger_ids_1 = [p.get("id", str(p)) for p in data1["passengers"]]
            passenger_ids_2 = [p.get("id", str(p)) for p in data2["passengers"]]
            
            # Keine Überschneidungen (wenn genug Daten vorhanden)
            if len(data1["passengers"]) == 5 and len(data2["passengers"]) == 5:
                assert set(passenger_ids_1).isdisjoint(set(passenger_ids_2))


class TestStatisticsEndpoint:
    """Tests für Statistik-Endpunkte."""
    
    @pytest.mark.asyncio
    async def test_get_statistics(self):
        """Test allgemeine Statistiken."""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/passengers/statistics")
            
            assert response.status_code == 200
            data = response.json()
            
            # Erforderliche Felder prüfen
            required_fields = [
                "total_passengers", "survival_rate", "survivors", "casualties",
                "average_age", "average_fare", "class_distribution", "gender_distribution"
            ]
            
            for field in required_fields:
                assert field in data, f"Feld '{field}' fehlt in Statistiken"
            
            # Datentypen und Bereiche prüfen
            assert isinstance(data["total_passengers"], int)
            assert data["total_passengers"] > 0
            assert 0 <= data["survival_rate"] <= 100
            assert data["survivors"] + data["casualties"] == data["total_passengers"]
    
    @pytest.mark.asyncio
    async def test_survival_by_class(self):
        """Test Überlebensrate nach Klasse."""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/passengers/survival-by-class")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "survival_by_class" in data
            classes = data["survival_by_class"]
            
            # Sollte 3 Klassen haben
            assert len(classes) == 3
            
            # Jede Klasse prüfen
            for class_data in classes:
                assert "class" in class_data
                assert "total_passengers" in class_data
                assert "survivors" in class_data
                assert "survival_rate" in class_data
                
                # Datenqualität prüfen
                assert class_data["total_passengers"] > 0
                assert 0 <= class_data["survival_rate"] <= 100
                assert class_data["survivors"] <= class_data["total_passengers"]
    
    @pytest.mark.asyncio
    async def test_age_groups(self):
        """Test Altersgruppen-Statistiken."""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/passengers/age-groups")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "age_groups" in data
            age_groups = data["age_groups"]
            
            # Sollte mehrere Altersgruppen haben
            assert len(age_groups) > 0
            
            # Jede Altersgruppe prüfen
            for group in age_groups:
                assert "age_group" in group
                assert "total_passengers" in group
                assert "survivors" in group
                assert "survival_rate" in group
                assert "average_age" in group


class TestErrorHandling:
    """Tests für Fehlerbehandlung."""
    
    @pytest.mark.asyncio
    async def test_invalid_parameters(self):
        """Test ungültige Parameter."""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Ungültige Klasse
            response = await client.get(f"{API_BASE_URL}/api/v1/passengers?pclass=5")
            # Sollte 422 (Validation Error) oder leere Ergebnisse zurückgeben
            assert response.status_code in [200, 422]
            
            # Negative Werte
            response = await client.get(f"{API_BASE_URL}/api/v1/passengers?limit=-1")
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_nonexistent_endpoint(self):
        """Test nicht existierender Endpunkt."""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/nonexistent")
            assert response.status_code == 404


class TestDataConsistency:
    """Tests für Datenkonsistenz."""
    
    @pytest.mark.asyncio
    async def test_total_count_consistency(self):
        """Test Konsistenz der Gesamtanzahl."""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Statistiken abrufen
            stats_response = await client.get(f"{API_BASE_URL}/api/v1/passengers/statistics")
            stats_data = stats_response.json()
            total_from_stats = stats_data["total_passengers"]
            
            # Alle Passagiere abrufen
            passengers_response = await client.get(f"{API_BASE_URL}/api/v1/passengers?limit=1000")
            passengers_data = passengers_response.json()
            total_from_list = passengers_data["total_count"]
            
            # Sollten gleich sein
            assert total_from_stats == total_from_list
    
    @pytest.mark.asyncio
    async def test_survival_calculation_consistency(self):
        """Test Konsistenz der Überlebensberechnungen."""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Alle Passagiere abrufen
            response = await client.get(f"{API_BASE_URL}/api/v1/passengers?limit=1000")
            data = response.json()
            
            # Manuelle Berechnung
            total_passengers = len(data["passengers"])
            survivors = sum(1 for p in data["passengers"] if p["survived"] == 1)
            
            if total_passengers > 0:
                calculated_rate = round((survivors / total_passengers) * 100, 2)
                
                # Mit Statistik-Endpunkt vergleichen
                stats_response = await client.get(f"{API_BASE_URL}/api/v1/passengers/statistics")
                stats_data = stats_response.json()
                
                # Kleine Abweichungen durch Rundung erlauben
                assert abs(calculated_rate - stats_data["survival_rate"]) < 1.0


# Pytest-Konfiguration für Integration Tests
@pytest.fixture(scope="session")
def event_loop():
    """Event Loop für async Tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def pytest_configure(config):
    """Pytest-Konfiguration für Integration Tests."""
    config.addinivalue_line(
        "markers", "integration: integration tests requiring database"
    )
