"""
Router für Passagier-Endpunkte der Titanic API.
Verwaltet alle HTTP-Endpunkte für Passagierdaten und Statistiken.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
import logging

from api.models.passenger import (
    PassengerResponse, 
    PassengerListResponse, 
    PassengerFilter,
    StatisticsResponse,
    ErrorResponse
)
from api.database.connection import execute_query, execute_count_query

logger = logging.getLogger(__name__)

router = APIRouter()


def build_passenger_query(filters: Optional[PassengerFilter] = None, 
                         limit: Optional[int] = None, 
                         offset: Optional[int] = None) -> tuple[str, tuple]:
    """
    Baut die SQL-Abfrage für Passagierdaten basierend auf Filtern auf.
    
    Args:
        filters: Optionale Filter für die Abfrage
        limit: Maximale Anzahl der Ergebnisse
        offset: Offset für Paginierung
    
    Returns:
        Tuple aus SQL-Query und Parametern
    """
    # Basis-Query aus dem Notebook übernommen und erweitert
    base_query = """
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
        c.class as class_name,
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
    """
    
    where_conditions = []
    params = []
    
    # Filter anwenden, falls vorhanden
    if filters:
        if filters.survived is not None:
            where_conditions.append("o.survived = %s")
            params.append(filters.survived)
        
        if filters.pclass is not None:
            where_conditions.append("o.pclass = %s")
            params.append(filters.pclass)
        
        if filters.sex is not None:
            where_conditions.append("s.sex = %s")
            params.append(filters.sex)
        
        if filters.min_age is not None:
            where_conditions.append("o.age >= %s")
            params.append(filters.min_age)
        
        if filters.max_age is not None:
            where_conditions.append("o.age <= %s")
            params.append(filters.max_age)
        
        if filters.embarked is not None:
            where_conditions.append("e.embarked = %s")
            params.append(filters.embarked)
        
        if filters.adult_male is not None:
            where_conditions.append("o.adult_male = %s")
            params.append(filters.adult_male)
        
        if filters.alone is not None:
            where_conditions.append("o.alone = %s")
            params.append(filters.alone)
    
    # WHERE-Klausel hinzufügen
    if where_conditions:
        base_query += " WHERE " + " AND ".join(where_conditions)
    
    # Sortierung hinzufügen
    base_query += " ORDER BY o.pclass, s.sex, o.age"
    
    # Limit und Offset hinzufügen
    if limit is not None:
        base_query += " LIMIT %s"
        params.append(limit)
        
        if offset is not None:
            base_query += " OFFSET %s"
            params.append(offset)
    
    return base_query, tuple(params)


def build_count_query(filters: Optional[PassengerFilter] = None) -> tuple[str, tuple]:
    """
    Baut eine COUNT-Abfrage für die Gesamtzahl der Passagiere.
    """
    base_query = """
    SELECT COUNT(*) as total
    FROM Observation o
    LEFT JOIN Sex s ON o.sex_id = s.sex_id
    LEFT JOIN Embarked e ON o.embarked_id = e.embarked_id
    LEFT JOIN Class c ON o.class_id = c.class_id
    LEFT JOIN Who w ON o.who_id = w.who_id
    LEFT JOIN Deck d ON o.deck_id = d.deck_id
    LEFT JOIN EmbarkTown et ON o.embark_town_id = et.embark_town_id
    LEFT JOIN Alive a ON o.alive_id = a.alive_id
    """
    
    where_conditions = []
    params = []
    
    if filters:
        if filters.survived is not None:
            where_conditions.append("o.survived = %s")
            params.append(filters.survived)
        
        if filters.pclass is not None:
            where_conditions.append("o.pclass = %s")
            params.append(filters.pclass)
        
        if filters.sex is not None:
            where_conditions.append("s.sex = %s")
            params.append(filters.sex)
        
        if filters.min_age is not None:
            where_conditions.append("o.age >= %s")
            params.append(filters.min_age)
        
        if filters.max_age is not None:
            where_conditions.append("o.age <= %s")
            params.append(filters.max_age)
        
        if filters.embarked is not None:
            where_conditions.append("e.embarked = %s")
            params.append(filters.embarked)
        
        if filters.adult_male is not None:
            where_conditions.append("o.adult_male = %s")
            params.append(filters.adult_male)
        
        if filters.alone is not None:
            where_conditions.append("o.alone = %s")
            params.append(filters.alone)
    
    if where_conditions:
        base_query += " WHERE " + " AND ".join(where_conditions)
    
    return base_query, tuple(params)


@router.get("/passengers", 
           response_model=PassengerListResponse,
           summary="Passagiere abrufen",
           description="Ruft eine paginierte Liste von Titanic-Passagieren mit optionalen Filtern ab.")
async def get_passengers(
    page: int = Query(1, ge=1, description="Seitennummer (beginnend bei 1)"),
    page_size: int = Query(50, ge=1, le=500, description="Anzahl Passagiere pro Seite"),
    survived: Optional[int] = Query(None, ge=0, le=1, description="Filter nach Überlebensstatus"),
    pclass: Optional[int] = Query(None, ge=1, le=3, description="Filter nach Passagierklasse"),
    sex: Optional[str] = Query(None, description="Filter nach Geschlecht"),
    min_age: Optional[float] = Query(None, ge=0, description="Mindestalter"),
    max_age: Optional[float] = Query(None, le=120, description="Höchstalter"),
    embarked: Optional[str] = Query(None, description="Filter nach Einschiffungshafen"),
    adult_male: Optional[bool] = Query(None, description="Filter nach erwachsenen Männern"),
    alone: Optional[bool] = Query(None, description="Filter nach allein Reisenden")
):
    """
    Ruft eine paginierte Liste von Passagieren ab.
    Unterstützt verschiedene Filter zur Eingrenzung der Ergebnisse.
    """
    try:
        # Filter-Objekt erstellen
        filters = PassengerFilter(
            survived=survived,
            pclass=pclass,
            sex=sex,
            min_age=min_age,
            max_age=max_age,
            embarked=embarked,
            adult_male=adult_male,
            alone=alone
        )
        
        # Gesamtzahl ermitteln
        count_query, count_params = build_count_query(filters)
        total_count = execute_count_query(count_query, count_params)
        
        # Paginierung berechnen
        offset = (page - 1) * page_size
        total_pages = (total_count + page_size - 1) // page_size
        
        # Hauptabfrage ausführen
        query, params = build_passenger_query(filters, page_size, offset)
        results = execute_query(query, params)
        
        # Ergebnisse in Pydantic-Modelle konvertieren
        passengers = []
        for row in results:
            passenger_data = dict(row)
            # 'class' ist ein reserviertes Wort in Python, daher Alias verwenden
            if 'class' in passenger_data:
                passenger_data['class_name'] = passenger_data.pop('class')
            passengers.append(PassengerResponse(**passenger_data))
        
        logger.info(f"Passagierliste abgerufen: {len(passengers)} von {total_count} Passagieren")
        
        return PassengerListResponse(
            passengers=passengers,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Passagierliste: {e}")
        raise HTTPException(status_code=500, detail=f"Interner Serverfehler: {str(e)}")


@router.get("/passengers/statistics",
           response_model=StatisticsResponse,
           summary="Passagierstatistiken",
           description="Ruft statistische Informationen über die Titanic-Passagiere ab.")
async def get_passenger_statistics():
    """
    Ruft umfassende Statistiken über die Titanic-Passagiere ab.
    """
    try:
        # Grundlegende Statistiken
        total_query = "SELECT COUNT(*) as total FROM Observation"
        total_count = execute_count_query(total_query)
        
        # Überlebensstatistiken
        survival_query = """
        SELECT 
            COUNT(*) as total,
            SUM(survived) as survivors
        FROM Observation
        """
        survival_result = execute_query(survival_query)[0]
        survivors = int(survival_result['survivors']) if survival_result['survivors'] else 0
        casualties = total_count - survivors
        survival_rate = (survivors / total_count * 100) if total_count > 0 else 0
        
        # Durchschnittsalter
        age_query = "SELECT AVG(age) as avg_age FROM Observation WHERE age IS NOT NULL"
        age_result = execute_query(age_query)[0]
        average_age = float(age_result['avg_age']) if age_result['avg_age'] else None
        
        # Durchschnittlicher Ticketpreis
        fare_query = "SELECT AVG(fare) as avg_fare FROM Observation WHERE fare IS NOT NULL"
        fare_result = execute_query(fare_query)[0]
        average_fare = float(fare_result['avg_fare']) if fare_result['avg_fare'] else None
        
        # Klassenverteilung
        class_query = """
        SELECT c.class, COUNT(*) as count
        FROM Observation o
        LEFT JOIN Class c ON o.class_id = c.class_id
        WHERE c.class IS NOT NULL
        GROUP BY c.class, c.class_id
        ORDER BY c.class_id
        """
        class_results = execute_query(class_query)
        class_distribution = {row['class']: int(row['count']) for row in class_results if row['class']}
        
        # Geschlechterverteilung
        gender_query = """
        SELECT s.sex, COUNT(*) as count
        FROM Observation o
        LEFT JOIN Sex s ON o.sex_id = s.sex_id
        GROUP BY s.sex
        """
        gender_results = execute_query(gender_query)
        gender_distribution = {row['sex']: int(row['count']) for row in gender_results if row['sex']}
        
        logger.info("Passagierstatistiken erfolgreich berechnet")
        
        return StatisticsResponse(
            total_passengers=total_count,
            survival_rate=round(survival_rate, 2),
            survivors=survivors,
            casualties=casualties,
            average_age=round(average_age, 2) if average_age else None,
            average_fare=round(average_fare, 2) if average_fare else None,
            class_distribution=class_distribution,
            gender_distribution=gender_distribution
        )
        
    except Exception as e:
        logger.error(f"Fehler beim Berechnen der Statistiken: {e}")
        raise HTTPException(status_code=500, detail=f"Interner Serverfehler: {str(e)}")


@router.get("/passengers/survival-by-class",
           summary="Überlebensrate nach Klasse",
           description="Ruft die Überlebensrate aufgeschlüsselt nach Passagierklasse ab.")
async def get_survival_by_class():
    """
    Analysiert die Überlebensrate nach Passagierklassen.
    """
    try:
        query = """
        SELECT 
            c.class,
            o.pclass,
            COUNT(*) as total,
            SUM(o.survived) as survivors,
            ROUND(CAST(SUM(o.survived) AS NUMERIC) / COUNT(*) * 100, 2) as survival_rate
        FROM Observation o
        LEFT JOIN Class c ON o.class_id = c.class_id
        WHERE c.class IS NOT NULL
        GROUP BY c.class, o.pclass
        ORDER BY o.pclass
        """
        
        results = execute_query(query)
        
        class_survival = []
        for row in results:
            if row['class']:  # Nur Zeilen mit gültigen Klassendaten
                class_survival.append({
                    "class": row['class'],
                    "total_passengers": int(row['total']),
                    "survivors": int(row['survivors']) if row['survivors'] else 0,
                    "survival_rate": float(row['survival_rate']) if row['survival_rate'] else 0.0
                })
        
        logger.info("Überlebensrate nach Klasse erfolgreich berechnet")
        return {"survival_by_class": class_survival}
        
    except Exception as e:
        logger.error(f"Fehler beim Berechnen der Überlebensrate nach Klasse: {e}")
        raise HTTPException(status_code=500, detail=f"Interner Serverfehler: {str(e)}")


@router.get("/passengers/survival-by-gender",
           summary="Überlebensrate nach Geschlecht",
           description="Ruft die Überlebensrate aufgeschlüsselt nach Geschlecht ab.")
async def get_survival_by_gender():
    """
    Analysiert die Überlebensrate nach Geschlecht.
    """
    try:
        query = """
        SELECT 
            s.sex,
            COUNT(*) as total,
            SUM(o.survived) as survivors,
            ROUND(CAST(SUM(o.survived) AS NUMERIC) / COUNT(*) * 100, 2) as survival_rate
        FROM Observation o
        LEFT JOIN Sex s ON o.sex_id = s.sex_id
        GROUP BY s.sex
        """
        
        results = execute_query(query)
        
        gender_survival = []
        for row in results:
            if row['sex']:  # Nur Zeilen mit gültigen Geschlechtsdaten
                gender_survival.append({
                    "gender": row['sex'],
                    "total_passengers": int(row['total']),
                    "survivors": int(row['survivors']) if row['survivors'] else 0,
                    "survival_rate": float(row['survival_rate']) if row['survival_rate'] else 0.0
                })
        
        logger.info("Überlebensrate nach Geschlecht erfolgreich berechnet")
        return {"survival_by_gender": gender_survival}
        
    except Exception as e:
        logger.error(f"Fehler beim Berechnen der Überlebensrate nach Geschlecht: {e}")
        raise HTTPException(status_code=500, detail=f"Interner Serverfehler: {str(e)}")


@router.get("/passengers/age-groups",
           summary="Altersgruppen-Analyse",
           description="Analysiert die Passagiere nach Altersgruppen.")
async def get_age_groups():
    """
    Gruppiert Passagiere nach Altersgruppen und berechnet Statistiken.
    """
    try:
        query = """
        SELECT 
            CASE 
                WHEN age < 18 THEN 'Kinder (0-17)'
                WHEN age < 30 THEN 'Junge Erwachsene (18-29)'
                WHEN age < 50 THEN 'Erwachsene (30-49)'
                WHEN age < 65 THEN 'Ältere Erwachsene (50-64)'
                ELSE 'Senioren (65+)'
            END as age_group,
            COUNT(*) as total,
            SUM(survived) as survivors,
            ROUND(CAST(SUM(survived) AS NUMERIC) / COUNT(*) * 100, 2) as survival_rate,
            ROUND(CAST(AVG(age) AS NUMERIC), 1) as avg_age
        FROM Observation
        WHERE age IS NOT NULL
        GROUP BY 
            CASE 
                WHEN age < 18 THEN 'Kinder (0-17)'
                WHEN age < 30 THEN 'Junge Erwachsene (18-29)'
                WHEN age < 50 THEN 'Erwachsene (30-49)'
                WHEN age < 65 THEN 'Ältere Erwachsene (50-64)'
                ELSE 'Senioren (65+)'
            END
        ORDER BY MIN(age)
        """
        
        results = execute_query(query)
        
        age_groups = []
        for row in results:
            age_groups.append({
                "age_group": row['age_group'],
                "total_passengers": int(row['total']),
                "survivors": int(row['survivors']) if row['survivors'] else 0,
                "survival_rate": float(row['survival_rate']) if row['survival_rate'] else 0.0,
                "average_age": float(row['avg_age']) if row['avg_age'] else 0.0
            })
        
        logger.info("Altersgruppen-Analyse erfolgreich durchgeführt")
        return {"age_groups": age_groups}
        
    except Exception as e:
        logger.error(f"Fehler bei der Altersgruppen-Analyse: {e}")
        raise HTTPException(status_code=500, detail=f"Interner Serverfehler: {str(e)}")
