# 🚢 Titanic API

Eine vollständige REST API für Titanic-Passagierdaten mit automatisierter Bereitstellung.

## ⚡ Schnellstart

**Ein Befehl, um alles bereitzustellen:**

```bash
./deploy.ps1
```

> **Hinweis:** Dieses Projekt ist für **Windows** entwickelt und getestet.

Dieser eine Befehl wird:
- ✅ Daten aus der Titanic-Datenbank extrahieren
- ✅ PostgreSQL mit den Daten starten
- ✅ Den API-Server starten
- ✅ Alles unter http://localhost:8000 zugänglich machen

## 📖 Was Sie erhalten

- **Vollständige API** mit Passagierdaten und Statistiken
- **Interaktive Dokumentation** unter http://localhost:8000/docs
- **Gesundheitsprüfung** unter http://localhost:8000/health
- **Automatisierte Einrichtung** - keine manuelle Konfiguration erforderlich

## 🔧 Manuelle Einrichtung (Optional)

Falls Sie die Einrichtung manuell bevorzugen:

1. **Virtuelle Umgebung aktivieren**
```bash
axaenv\Scripts\activate
```

2. **Abhängigkeiten installieren**
```bash
pip install -r requirements.txt
```

3. **Services manuell starten**
```bash
docker-compose up
```

## 🧪 Tests

Tests ausführen mit:
```bash
pytest tests/ -v
```

## 📂 API-Endpunkte

Sobald die Anwendung läuft, können Sie folgende Endpunkte nutzen:

- **📚 Dokumentation**: http://localhost:8000/docs
- **❤️ Gesundheitsprüfung**: http://localhost:8000/health
- **👥 Passagiere**: http://localhost:8000/api/v1/passengers
- **📊 Statistiken**: http://localhost:8000/api/v1/passengers/statistics

## 🚀 Das war's!

Das Deploy-Skript übernimmt alles für Sie. Führen Sie einfach `./deploy.ps1` aus und erkunden Sie die API!
