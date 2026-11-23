
# Image Python légère
FROM python:3.11-slim

# Répertoire de travail
WORKDIR /app

# Configuration Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MAINTAI_MODELS_DIR=/app/models
ENV MAINTAI_DATA_PATH=/app/data/sensors.csv

# Installer les dépendances avant de copier le code
# pour profiter du cache Docker
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copier uniquement le code applicatif
COPY maintai/ ./maintai/
COPY ui/ ./ui/

# Ports de l'API et de l'interface
EXPOSE 8000 8501

# Démarrage par défaut : API FastAPI
CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
