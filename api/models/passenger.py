"""
Pydantic-Modelle für die Titanic API.
Definiert die Datenstrukturen für Request- und Response-Objekte.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum


class SurvivalStatus(str, Enum):
    """Überlebensstatus Enumeration"""
    SURVIVED = "yes"
    DIED = "no"


class Gender(str, Enum):
    """Geschlecht Enumeration"""
    MALE = "male"
    FEMALE = "female"


class PassengerClass(str, Enum):
    """Passagierklasse Enumeration"""
    FIRST = "First"
    SECOND = "Second" 
    THIRD = "Third"


class EmbarkedPort(str, Enum):
    """Einschiffungshafen Enumeration"""
    CHERBOURG = "C"
    QUEENSTOWN = "Q"
    SOUTHAMPTON = "S"


class PassengerBase(BaseModel):
    """
    Basis-Modell für Passagierdaten.
    Enthält alle Felder, die von einem Passagier erwartet werden.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    survived: Optional[int] = Field(None, ge=0, le=1, description="Überlebensstatus (0=gestorben, 1=überlebt)")
    pclass: Optional[int] = Field(None, ge=1, le=3, description="Passagierklasse (1, 2, oder 3)")
    sex: Optional[str] = Field(None, description="Geschlecht des Passagiers")
    age: Optional[float] = Field(None, ge=0, le=120, description="Alter des Passagiers")
    sibsp: Optional[int] = Field(None, ge=0, description="Anzahl Geschwister/Ehepartner an Bord")
    parch: Optional[int] = Field(None, ge=0, description="Anzahl Eltern/Kinder an Bord")
    fare: Optional[float] = Field(None, ge=0, description="Ticketpreis")
    adult_male: Optional[bool] = Field(None, description="Ist erwachsener Mann")
    alone: Optional[bool] = Field(None, description="Reist alleine")
    embarked: Optional[str] = Field(None, description="Einschiffungshafen")
    class_name: Optional[str] = Field(None, alias="class", description="Klassename (First, Second, Third)")
    who: Optional[str] = Field(None, description="Kategorie (man, woman, child)")
    deck: Optional[str] = Field(None, description="Deckbezeichnung")
    embark_town: Optional[str] = Field(None, description="Einschiffungsstadt")
    alive: Optional[str] = Field(None, description="Überlebensstatus (yes/no)")


class PassengerResponse(PassengerBase):
    """
    Response-Modell für Passagierdaten.
    Wird für API-Antworten verwendet.
    """
    pass


class PassengerListResponse(BaseModel):
    """
    Response-Modell für Listen von Passagieren.
    """
    passengers: List[PassengerResponse]
    total_count: int = Field(description="Gesamtanzahl der Passagiere")
    page: int = Field(description="Aktuelle Seite")
    page_size: int = Field(description="Anzahl Einträge pro Seite")
    total_pages: int = Field(description="Gesamtanzahl der Seiten")


class PassengerFilter(BaseModel):
    """
    Modell für Passagierfilter.
    Ermöglicht das Filtern von Passagierdaten.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True
    )
    
    survived: Optional[int] = Field(None, ge=0, le=1, description="Filter nach Überlebensstatus")
    pclass: Optional[int] = Field(None, ge=1, le=3, description="Filter nach Passagierklasse")
    sex: Optional[str] = Field(None, description="Filter nach Geschlecht")
    min_age: Optional[float] = Field(None, ge=0, description="Mindestalter")
    max_age: Optional[float] = Field(None, le=120, description="Höchstalter")
    embarked: Optional[str] = Field(None, description="Filter nach Einschiffungshafen")
    adult_male: Optional[bool] = Field(None, description="Filter nach erwachsenen Männern")
    alone: Optional[bool] = Field(None, description="Filter nach allein Reisenden")


class StatisticsResponse(BaseModel):
    """
    Response-Modell für Statistiken.
    """
    total_passengers: int = Field(description="Gesamtanzahl Passagiere")
    survival_rate: float = Field(description="Überlebensrate in Prozent")
    survivors: int = Field(description="Anzahl Überlebende")
    casualties: int = Field(description="Anzahl Opfer")
    average_age: Optional[float] = Field(None, description="Durchschnittsalter")
    average_fare: Optional[float] = Field(None, description="Durchschnittlicher Ticketpreis")
    class_distribution: dict = Field(description="Verteilung nach Klassen")
    gender_distribution: dict = Field(description="Verteilung nach Geschlecht")
    

class ErrorResponse(BaseModel):
    """
    Standardmodell für Fehlerantworten.
    """
    error: str = Field(description="Fehlermeldung")
    detail: Optional[str] = Field(None, description="Detaillierte Fehlerbeschreibung")
    code: Optional[str] = Field(None, description="Fehlercode")
