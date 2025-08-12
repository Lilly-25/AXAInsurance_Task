# Multi-Stage Dockerfile für die Titanic API
# Optimiert für Produktionsumgebungen

# Build-Stage
FROM python:3.10-slim as builder

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Dependencies installieren
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python-Dependencies installieren
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production-Stage
FROM python:3.10-slim

# Non-root User erstellen
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Arbeitsverzeichnis setzen
WORKDIR /app

# Python-Packages aus Build-Stage kopieren
COPY --from=builder /root/.local /home/appuser/.local

# Anwendungscode kopieren
COPY . .

# Logs-Verzeichnis erstellen
RUN mkdir -p logs && chown -R appuser:appuser /app

# User wechseln
USER appuser

# PATH anpassen
ENV PATH=/home/appuser/.local/bin:$PATH

# Umgebungsvariablen setzen
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Port freigeben
EXPOSE 8000

# Health-Check hinzufügen
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Startkommando
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
