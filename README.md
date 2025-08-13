# 🚢 Titanic API

Eine vollständige REST API für Titanic-Passagierdaten mit automatisierter Bereitstellung und **schöner Web-Anmeldung**.

## ⚡ Schnellstart

**Ein Befehl, um alles bereitzustellen:**

```powershell
./deploy.ps1
```

**Für öffentlichen Zugang (über ngrok):**

```powershell
./deploy.ps1 -Public
```

> **Hinweis:** Dieses Projekt ist für **Windows** entwickelt und getestet.

## 🔐 Authentifizierung

Die API verwendet eine schöne **Titanic-themed Web-Anmeldung** mit drei Benutzerrollen:

- **Administrator** - Vollzugriff
- **Datenanalyst** - Datenanalyse
- **Betrachter** - Nur Ansicht

Einfach zu http://localhost:8000 navigieren und sich anmelden!


## 🌐 Öffentlicher Zugang mit Ngrok

### Einmalige Einrichtung:
1. **Ngrok-Konto erstellen**: https://dashboard.ngrok.com/signup
2. **Auth-Token kopieren**: https://dashboard.ngrok.com/get-started/your-authtoken
3. **Token konfigurieren**:
```powershell
.\axaenv\Scripts\Activate.ps1
python -c "from pyngrok import ngrok; ngrok.set_auth_token('YOUR_TOKEN_HERE')"
```

### Verwendung:
```powershell
# Lokal bereitstellen
./deploy.ps1

# Öffentlich verfügbar machen
./deploy.ps1 -Public

# Oder direkt:
python main.py          # Lokal
python main.py --public # Öffentlich mit ngrok
```

**⚠️ Wichtig:** Die ngrok-URL ändert sich bei jedem Neustart (z.B. `https://abc123.ngrok-free.app/docs`)

## 📖 Was Sie erhalten

- **Schöne Web-Anmeldung** mit Titanic-Design
- **Dashboard** mit rollenbasiertem Zugang
- **Vollständige API** mit Passagierdaten und Statistiken
- **Interaktive Dokumentation** unter http://localhost:8000/docs
- **Gesundheitsprüfung** unter http://localhost:8000/health
- **Öffentlicher Zugang** über ngrok-Tunnel
- **Automatisierte Einrichtung** - keine manuelle Konfiguration erforderlich

## 🔧 Manuelle Einrichtung (Optional)

Falls Sie die Einrichtung manuell bevorzugen:

1. **Virtuelle Umgebung aktivieren**
```powershell
axaenv\Scripts\activate
```

2. **Abhängigkeiten installieren**
```powershell
pip install -r requirements.txt
```

3. **Services manuell starten**
```powershell
docker-compose up
```

## 🧪 Tests

Tests ausführen mit:
```powershell
pytest tests/ -v
```

## 📁 Projektstruktur

```
AXAInsurance_Task/
├── api/                    # API Quellcode
│   ├── database/          # Datenbankverbindung
│   ├── middleware/        # Authentifizierungs-Middleware
│   ├── models/           # Datenmodelle
│   ├── routes/           # Authentifizierungs-Routen
│   ├── routers/          # API-Endpunkt-Router
│   ├── templates/        # HTML-Templates (Login, Dashboard)
│   └── utils/            # Hilfsfunktionen
├── data/                 # Datenbank-Dateien
├── logs/                 # Log-Dateien
├── notebooks/            # Jupyter Notebooks
├── scripts/              # Setup- und Hilfsskripte
├── sql/                  # SQL-Initialisierungsskripte
├── tests/                # Testsuite
│   ├── integration/      # Integrationstests
│   ├── performance/      # Performance-Tests
│   └── unit/            # Unit-Tests
├── .github/workflows/    # CI/CD Pipeline
├── docker-compose.yml    # Container-Konfiguration
├── main.py              # Hauptanwendung
└── requirements.txt     # Python-Abhängigkeiten
```

## 📂 API-Endpunkte

Sobald die Anwendung läuft, können Sie folgende Endpunkte nutzen:

**Öffentlich:**
- **� Anmeldung**: http://localhost:8000
- **📚 Dokumentation**: http://localhost:8000/docs
- **❤️ Gesundheitsprüfung**: http://localhost:8000/health

**Geschützt (Nach Anmeldung verfügbar):**
- **📊 Dashboard**: http://localhost:8000/dashboard
- **👥 Passagiere**: http://localhost:8000/api/v1/passengers
- **📊 Statistiken**: http://localhost:8000/api/v1/passengers/statistics
- **📈 Überlebensanalyse**: http://localhost:8000/api/v1/passengers/survival-by-gender

## 🚀 Das war's!

**Lokale Bereitstellung:**
```powershell
./deploy.ps1
```

**Öffentliche Bereitstellung:**
```powershell
./deploy.ps1 -Public
```

Das Deploy-Skript übernimmt alles für Sie!