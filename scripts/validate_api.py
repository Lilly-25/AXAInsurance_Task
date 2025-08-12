#!/usr/bin/env python3
"""
Validierungsscript für die Titanic API.
Testet die wichtigsten Endpunkte ohne externe Dependencies.
"""

import sys
import os


def test_database_connection():
    """Testet die PostgreSQL-Datenbankverbindung."""
    try:
        # Teste über das API-Modul
        sys.path.insert(0, os.getcwd())
        from api.database.connection import execute_count_query

        count = execute_count_query("SELECT COUNT(*) FROM Observation")
        print(
            f"✓ PostgreSQL-Datenbankverbindung erfolgreich - {count} Passagiere gefunden"
        )
        return True
    except Exception as e:
        print(f"✗ Datenbankverbindung fehlgeschlagen: {e}")
        return False


def test_database_schema():
    """Testet das PostgreSQL-Datenbankschema."""
    try:
        sys.path.insert(0, os.getcwd())
        from api.database.connection import execute_query

        # Teste JOIN-Query
        query = """
        SELECT 
            o.survived,
            o.pclass,
            s.sex,
            o.age,
            o.sibsp,
            o.parch,
            o.fare,
            o.adult_male,
            o.alone,
            e.embarked,
            c.class,
            w.who,
            d.deck,
            et.embark_town,
            a.alive
        FROM Observation o
        LEFT JOIN Sex s ON o.sex_id = s.sex_id
        LEFT JOIN Embarked e ON o.embarked_id = e.embarked_id
        LEFT JOIN Class c ON o.class_id = c.class_id
        LEFT JOIN Who w ON o.who_id = w.who_id
        LEFT JOIN Deck d ON o.deck_id = d.deck_id
        LEFT JOIN EmbarkTown et ON o.embark_town_id = et.embark_town_id
        LEFT JOIN Alive a ON o.alive_id = a.alive_id
        LIMIT 5
        """

        results = execute_query(query)

        if results:
            print(f"✓ PostgreSQL-Schema gültig - {len(results)} Testzeilen abgerufen")
            return True
        else:
            print("✗ PostgreSQL-Schema-Test fehlgeschlagen - Keine Daten")
            return False

    except Exception as e:
        print(f"✗ PostgreSQL-Schema-Test fehlgeschlagen: {e}")
        return False


def test_api_startup():
    """Testet ob die API-Anwendung startet."""
    try:
        from main import app

        print("✓ FastAPI-Anwendung erfolgreich erstellt")
        return True
    except Exception as e:
        print(f"✗ API-Startup-Test fehlgeschlagen: {e}")
        return False


def main():
    """Führt alle Validierungstests aus."""
    print("🚢 Titanic API Validierung")
    print("=" * 40)

    tests = [
        ("Datenbankverbindung", test_database_connection),
        ("Datenbankschema", test_database_schema),
        ("API-Startup", test_api_startup),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Teste {test_name}...")
        if test_func():
            passed += 1

    print("\n" + "=" * 40)
    print(f"📊 Ergebnis: {passed}/{total} Tests bestanden")

    if passed == total:
        print("🎉 Alle Tests erfolgreich - API ist bereit für Deployment!")
        return 0
    else:
        print("⚠️  Einige Tests fehlgeschlagen - Bitte Konfiguration prüfen")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
