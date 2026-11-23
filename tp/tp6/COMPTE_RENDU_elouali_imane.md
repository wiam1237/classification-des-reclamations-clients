# Compte rendu · TP6 : Conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :*2* À compléter · **Membres :** Imane Elouali · **Date :** 23/11/2026

## 1. Mise en place

La commande `docker run hello-world` a été exécutée avec succès. Le message « Hello from Docker! » confirme que Docker est correctement installé et que le client communique avec le moteur Docker.

**Dernière ligne de `python -m pytest` après la mise en place :**

```text
====================== 38 passed, 109 warnings in 136.73s =======================
```

## 2. Image et conteneur

**1. Quelle différence entre une image et un conteneur ?**

Une image Docker est un modèle contenant le système de base, les dépendances et le code nécessaire à l'application. Un conteneur est une instance créée à partir de cette image et qui permet d'exécuter l'application.

**2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?**

Cela permet de profiter du cache Docker. Si le code source change mais que les dépendances restent identiques, Docker peut réutiliser la couche d'installation sans réinstaller toutes les bibliothèques.

**3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?**

Une version figée garantit un environnement reproductible et évite les différences de comportement entre versions. Elle permet également de conserver la compatibilité avec le modèle entraîné.

**4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?**

Ces outils servent principalement au développement, au suivi des expériences, à la gestion des données et aux tests. Ils ne sont pas nécessaires pour exécuter l'API et l'interface en production.

## 3. Sprint 1 : le Dockerfile

**Dockerfile utilisé :**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MAINTAI_MODELS_DIR=/app/models
ENV MAINTAI_DATA_PATH=/app/data/sensors.csv

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY maintai/ ./maintai/
COPY ui/ ./ui/

EXPOSE 8000 8501

CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Résultats des builds Docker :**

| Build | Durée | Taille du contenu de l'image |
|---|---:|---:|
| Premier build mesuré | 6 min environ | 259 MB |
| Après modification de `maintai/predict.py` | Non mesuré séparément | 255 MB |

Le premier build mesuré a nécessité environ 6 minutes. Le build suivant, après modification du code, a été exécuté en 2 secondes grâce au cache Docker.

**Que signifie `CACHED` dans le journal du second build ?**

Cela signifie que Docker réutilise une couche déjà construite au lieu de refaire l'opération. Cela accélère la construction de l'image, notamment lorsque les dépendances n'ont pas changé.

## 4. Sprint 1 : lancer un conteneur

**Commande `docker run` utilisée :**

```bash
docker run -d --name test \
  -p 8002:8000 \
  --env-file .env \
  -v "$PWD/models:/app/models:ro" \
  maintai:0.4.0
```

**Résultats des essais :**

| Essai | Réponse |
|---|---|
| `GET /health` | API opérationnelle, modèle chargé (`status=ok`, `model_loaded=true`). |
| `POST /v1/predict` sans clé | 401 Unauthorized attendu : clé API absente. |
| `POST /v1/predict` avec la clé | 200 OK attendu : prédiction effectuée avec succès. |

**Piège 1. Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?**

Sans le montage du dossier `models/`, le conteneur ne trouve pas le modèle entraîné. Le health check indique que le modèle n'est pas chargé (`model_loaded=false`) et la prédiction ne peut pas être effectuée. Le modèle doit être fourni au lancement grâce à un volume Docker.

**Piège 2. Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?**

Les logs indiquent que Uvicorn écoute sur `127.0.0.1:8000` à l'intérieur du conteneur. Depuis la machine hôte, l'accès à `localhost:8002/health` échoue, car le serveur n'écoute que sur l'interface locale du conteneur. Il faut utiliser `--host 0.0.0.0` pour rendre l'API accessible depuis l'extérieur du conteneur.

## 5. Sprint 2 : Docker Compose

**Fichier `compose.yaml` utilisé :**

```yaml
services:
  api:
    build: .
    image: maintai:0.4.0
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models:ro

  ui:
    image: maintai:0.4.0
    command:
      - python
      - -m
      - streamlit
      - run
      - ui/app.py
      - --server.address=0.0.0.0
      - --server.port=8501
      - --server.headless=true
    environment:
      MAINTAI_API_URL: http://api:8000
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data:ro
    depends_on:
      - api
```

**Sortie de `docker compose ps` :**

```text
NAME        IMAGE           COMMAND                  SERVICE   CREATED          STATUS         PORTS
tp6-api-1   maintai:0.4.0   "uvicorn maintai.api…"   api       35 seconds ago   Up 19 seconds  0.0.0.0:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   "python -m streamlit…"   ui        30 seconds ago   Up 16 seconds  0.0.0.0:8501->8501/tcp
```

**Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?**

L'URL est `http://api:8000`. Elle provient de la variable d'environnement `MAINTAI_API_URL`, définie dans `compose.yaml`. Le nom `api` correspond au nom du service Docker Compose et permet à l'interface de communiquer avec l'API sur le réseau interne.

**Résultat des deux commandes `docker compose exec ui` :**

Avec le nom du service `api` :

```text
$ docker compose exec ui python -c "import urllib.request; print(urllib.request.urlopen('http://api:8000/health').read().decode())"

{"status":"ok","model_loaded":true}
```

Avec `localhost` :

```text
$ docker compose exec ui python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"

ConnectionRefusedError: [Errno 111] Connection refused
```

**Pourquoi la seconde échoue-t-elle ?**

La première commande fonctionne car Docker Compose utilise le nom du service `api` pour permettre la communication entre les conteneurs. La seconde échoue car `localhost` désigne le conteneur UI lui-même et non le conteneur API.

**Dernière ligne de `python -m pytest` à la fin du sprint 2 :**

```text
==================== 38 passed, 109 warnings in 135.68s (0:02:15) ====================
```

## 6. Décision : l'ADR 005

Nous avons choisi d'utiliser une image Docker unique `maintai:0.4.0` pour exécuter les deux services : l'API FastAPI et l'interface Streamlit. Docker Compose permet de lancer deux conteneurs indépendants à partir de cette image, tout en séparant les données, les modèles et les secrets grâce aux volumes et aux variables d'environnement.

## 7. Questions de compréhension

**1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.**

- Le code Python de l'API et de l'interface est intégré à l'image avec `COPY`.
- Les dépendances sont installées depuis `requirements-docker.txt`.
- Les modèles sont fournis au lancement avec un volume Docker en lecture seule.
- Les données sont fournies au lancement avec un volume Docker en lecture seule.
- La clé API est transmise au conteneur avec le fichier `.env` via `env_file`.

**2. Pourquoi la clé API n'est-elle jamais dans l'image ?**

La clé API est une information sensible. Elle ne doit pas être intégrée à l'image pour éviter de l'exposer lors du partage ou du déploiement. Elle est transmise au lancement grâce au fichier `.env`, qui est exclu de l'image par `.dockerignore`.

**3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?**

Docker permet de livrer le modèle avec son environnement d'exécution : Python, les bibliothèques et leurs versions, ainsi que l'API et l'interface. Cela garantit une exécution plus reproductible sur différentes machines.

## 8. Le rendu Git

- **Lien de la pull request :https://github.com/wiam1237/classification-des-reclamations-clients.git
- **Le tag `tp6` existe sur GitHub :** Non, pas encore créé.
- **`git status` avant le commit :** À vérifier après l'initialisation du dépôt. Le fichier `.gitignore` exclut déjà `.env`, `models/` et `data/*.csv`.

## 9. Ce qui reste flou

Les notions principales de Docker et Docker Compose sont comprises. Il reste à finaliser la partie Git : initialisation du dépôt, publication du projet sur GitHub, création du tag `tp6` et préparation de la pull request.