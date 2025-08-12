"""
Hauptkonfigurationsdatei für die FastAPI-Anwendung.
Diese Datei enthält die Basis-Konfiguration und startet die API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse
import logging
from contextlib import asynccontextmanager

from api.routers import passengers
from api.database.connection import init_database

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle-Manager für die FastAPI-Anwendung.
    Wird beim Start und Stopp der Anwendung ausgeführt.
    """
    # Startup
    logger.info("Starte Titanic API...")
    init_database()
    logger.info("Datenbank initialisiert")

    yield

    # Shutdown
    logger.info("Stoppe Titanic API...")


# FastAPI-Anwendung erstellen
app = FastAPI(
    title="Titanic Passagier API",
    description="REST API zur Interaktion mit der Titanic-Passagierdatenbank",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS-Middleware hinzufügen für Cross-Origin-Requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion spezifische Origins angeben
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted Host Middleware für Sicherheit
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In Produktion spezifische Hosts angeben
)

# Router einbinden
app.include_router(passengers.router, prefix="/api/v1", tags=["passengers"])


@app.get("/")
async def root():
    """
    Root-Endpoint der API.
    Leitet zur Dokumentation weiter.
    """
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """
    Health-Check-Endpoint für Monitoring und Load Balancer.
    """
    return {
        "status": "healthy",
        "message": "Titanic API ist betriebsbereit",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    # API in der Entwicklungsumgebung starten
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
