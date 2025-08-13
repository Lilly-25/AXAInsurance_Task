# 🚢 Titanic API

Eine vollständige REST API für Titanic-Passagierdaten mit automatisierter Bereitstellung und **HTTP Basic Authentifizierung**.

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

Die API verwendet HTTP Basic Authentication - einfach Benutzername/Passwort eingeben:

**Autorisierte Benutzer:**
- 👑 `admin` / `secret` - Vollzugriff
- 📊 `analyst` / `password123` - Datenanalyse
- 👀 `viewer` / `view2024` - Nur-Lese-Zugriff

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

- **Sichere API** mit HTTP Basic Authentication
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

## 📂 API-Endpunkte

Sobald die Anwendung läuft, können Sie folgende Endpunkte nutzen:

**Öffentlich:**
- **📚 Dokumentation**: http://localhost:8000/docs
- **❤️ Gesundheitsprüfung**: http://localhost:8000/health

**Geschützt (HTTP Basic Auth erforderlich):**
- **👥 Passagiere**: http://localhost:8000/api/v1/passengers
- **📊 Statistiken**: http://localhost:8000/api/v1/passengers/statistics

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