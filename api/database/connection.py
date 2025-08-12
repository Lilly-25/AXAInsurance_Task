"""
Datenbankverbindungsmodul für die Titanic-Datenbank.
Verwaltet PostgreSQL-Verbindungen und stellt Hilfsfunktionen bereit.
"""

import psycopg2
import psycopg2.extras
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


# Datenbank-Konfiguration
def get_db_config() -> Dict[str, str]:
    """
    Gibt die Datenbankkonfiguration zurück.
    Alle Werte müssen über Umgebungsvariablen gesetzt werden.
    """
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "titanic"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD"),  # Kein Default - muss gesetzt werden!
    }


def get_db_connection() -> psycopg2.extensions.connection:
    """
    Erstellt eine neue PostgreSQL-Datenbankverbindung.
    """
    try:
        config = get_db_config()
        conn = psycopg2.connect(**config)
        conn.autocommit = False
        logger.debug(
            f"PostgreSQL-Verbindung hergestellt: {config['host']}:{config['port']}"
        )
        return conn

    except Exception as e:
        logger.error(f"Fehler beim Herstellen der Datenbankverbindung: {e}")
        raise


def init_database() -> None:
    """
    Initialisiert die Datenbank und überprüft die Verbindung.
    """
    try:
        conn = get_db_connection()

        # Teste die Verbindung durch Abfrage der Tabellen
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
            )
            tables = cursor.fetchall()

        if not tables:
            logger.warning("Keine Tabellen in der Datenbank gefunden")

        table_names = [table[0] for table in tables]
        logger.info(f"Datenbank erfolgreich initialisiert. Tabellen: {table_names}")

        conn.close()

    except Exception as e:
        logger.error(f"Fehler bei der Datenbankinitialisierung: {e}")
        raise


def execute_query(query: str, params: Optional[tuple] = None) -> list[Dict[str, Any]]:
    """
    Führt eine SELECT-Abfrage aus und gibt die Ergebnisse zurück.

    Args:
        query: SQL-Abfrage
        params: Parameter für die Abfrage (optional)

    Returns:
        Liste der Ergebniszeilen als Dictionaries
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            logger.debug(
                f"Abfrage erfolgreich ausgeführt: {len(results)} Zeilen zurückgegeben"
            )
            return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Fehler bei der Abfrageausführung: {e}")
        raise
    finally:
        if conn:
            conn.close()


def execute_count_query(query: str, params: Optional[tuple] = None) -> int:
    """
    Führt eine COUNT-Abfrage aus und gibt die Anzahl zurück.

    Args:
        query: SQL-COUNT-Abfrage
        params: Parameter für die Abfrage (optional)

    Returns:
        Anzahl der Zeilen
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            count = result[0] if result else 0
            logger.debug(f"Count-Abfrage erfolgreich: {count} Zeilen")
            return count

    except Exception as e:
        logger.error(f"Fehler bei der Count-Abfrage: {e}")
        raise
    finally:
        if conn:
            conn.close()
