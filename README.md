# 🚢 Titanic API

Eine vollständige REST API für Titanic-Passagierdaten mit automatisierter Bereitstellung und **JWT-Authentifizierung**.

## ⚡ Schnellstart

**Ein Befehl, um alles bereitzustellen:**

```powershell
./deploy.ps1
```

> **Hinweis:** Dieses Projekt ist für **Windows** entwickelt und getestet.

Dieser eine Befehl wird:
- ✅ Daten aus der Titanic-Datenbank extrahieren
- ✅ PostgreSQL mit den Daten starten
- ✅ Den API-Server mit Authentifizierung starten
- ✅ Alles unter http://localhost:8000 zugänglich machen

## 🔐 Authentifizierung

Die API erfordert JWT-Token für den Zugriff auf Passagierdaten:

**Autorisierte Benutzer:**
- 👑 `admin` / `secret` - Vollzugriff
- 📊 `analyst` / `password123` - Datenanalyse
- 👀 `viewer` / `view2024` - Nur-Lese-Zugriff

## 📖 Was Sie erhalten

- **Sichere API** mit JWT-Token-Authentifizierung
- **Vollständige API** mit Passagierdaten und Statistiken
- **Interaktive Dokumentation** unter http://localhost:8000/docs
- **Gesundheitsprüfung** unter http://localhost:8000/health
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

## 📂 API-Endpunkte

Sobald die Anwendung läuft, können Sie folgende Endpunkte nutzen:

**Öffentlich:**
- **📚 Dokumentation**: http://localhost:8000/docs
- **❤️ Gesundheitsprüfung**: http://localhost:8000/health
- **🔐 Login**: http://localhost:8000/api/v1/auth/login

**Geschützt (JWT-Token erforderlich):**
- **👥 Passagiere**: http://localhost:8000/api/v1/passengers
- **📊 Statistiken**: http://localhost:8000/api/v1/passengers/statistics

## 🚀 Das war's!

Das Deploy-Skript übernimmt alles für Sie. Führen Sie einfach `./deploy.ps1` aus und erkunden Sie die API!