"""
Hauptkonfigurationsdatei für die FastAPI-Anwendung.
Diese Datei enthält die Basis-Konfiguration und startet die API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import logging
from contextlib import asynccontextmanager

from api.routers import passengers
from api.routes import auth
from api.database.connection import init_database
from api.middleware.auth import SessionAuthMiddleware

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
    description="""
    **REST API zur Interaktion mit der Titanic-Passagierdatenbank**
    
    ## � Welcome Aboard the Titanic API!
    
    **Diese API bietet eine schöne Web-Oberfläche für die Authentifizierung!**
    
    **🎫 So steigen Sie ein:**
    1. Besuchen Sie [/auth/](/auth/) für die Anmeldung
    2. Verwenden Sie einen der verfügbaren Zugänge:
       - **admin** / secret (Vollzugriff)
       - **analyst** / password123 (Datenanalyse)  
       - **viewer** / view2024 (Nur-Lese-Zugriff)
    3. Nach der Anmeldung erhalten Sie Zugang zu allen API-Endpunkten
    
    **🌊 Erkunden Sie die Geschichte des berühmtesten Schiffs der Welt!**
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Security scheme für Swagger UI (HTTP Basic Auth)
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Titanic Passagier API",
        version="1.0.0",
        description="REST API zur Interaktion mit der Titanic-Passagierdatenbank",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBasic": {
            "type": "http",
            "scheme": "basic",
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Session-based Authentication Middleware - PROTECTS ENTIRE API with beautiful login page
app.add_middleware(SessionAuthMiddleware)

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
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(passengers.router, prefix="/api/v1", tags=["passengers"])


@app.get("/")
async def root():
    """
    Root-Endpoint der API.
    Leitet zur schönen Anmeldeseite weiter.
    """
    return RedirectResponse(url="/auth/")


@app.get("/health")
async def health_check():
    """
    Health-Check-Endpoint für Monitoring und Load Balancer.
    Dieser Endpoint benötigt keine Authentifizierung.
    """
    return {
        "status": "healthy",
        "message": "Titanic API ist betriebsbereit",
        "version": "1.0.0",
        "authentication": "required_for_data_endpoints",
    }


if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    
    # Check for --public flag
    public_mode = "--public" in sys.argv
    
    if public_mode:
        try:
            from pyngrok import ngrok
            import threading
            import time
            
            def start_ngrok():
                """Start ngrok tunnel in a separate thread"""
                time.sleep(2)  # Wait for uvicorn to start
                try:
                    tunnel = ngrok.connect(8000)
                    print(f"\n🌐 PUBLIC API URLs:")
                    print(f"📚 Interactive Docs: {tunnel.public_url}/docs")
                    print(f"🔗 API Base URL: {tunnel.public_url}/api/v1/")
                    print(f"❤️ Health Check: {tunnel.public_url}/health")
                    print(f"\n🔐 Authentication required:")
                    print(f"   Username: admin, Password: secret")
                    print(f"   Username: analyst, Password: password123")
                    print(f"   Username: viewer, Password: view2024")
                    print(f"\n📤 SHARE THIS URL: {tunnel.public_url}/docs")
                    print(f"\n⏹️ Press Ctrl+C to stop...\n")
                except Exception as e:
                    print(f"❌ Ngrok error: {e}")
                    print(f"Make sure ngrok auth token is configured!")
            
            # Start ngrok in background thread
            ngrok_thread = threading.Thread(target=start_ngrok, daemon=True)
            ngrok_thread.start()
            
            print("🚀 Starting API with public ngrok tunnel...")
            
        except ImportError:
            print("❌ pyngrok not installed. Install with: pip install pyngrok")
            sys.exit(1)
    else:
        print("🚀 Starting API locally...")
        print("💡 For public access, run: python main.py --public")

    # API in der Entwicklungsumgebung starten
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")