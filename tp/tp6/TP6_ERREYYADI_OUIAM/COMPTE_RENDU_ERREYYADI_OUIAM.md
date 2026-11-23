# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** G2
**Membres :** ERREYYADI Ouiam  
**Date :** 23/11/2026
**Heure :** 11:30

---

## 1. Mise en place (dans `TP/TP6`)

**Sortie de `docker run hello-world` et de `docker version` :**

```text
Docker Desktop a été installé et démarré correctement.
La commande docker compose a fonctionné et les conteneurs ont été lancés.
Sorties exactes de hello-world et docker version : non conservées.
```

**Dernière ligne de `python -m pytest` après la mise en place :**

```text
38 passed, 4 warnings
```

Les avertissements sont liés à MLflow et n'empêchent pas la réussite des tests.

---

## 2. Image et conteneur (pendant le premier build)

**1. Quelle différence entre une image et un conteneur ?**

Une image Docker est un modèle contenant l'application, ses dépendances et sa configuration. Un conteneur est une instance de cette image qui s'exécute.

**2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?**

Pour profiter du cache Docker. Les dépendances sont installées dans une couche séparée. Si le code de l'application change sans modification des dépendances, Docker peut réutiliser cette couche sans réinstaller tous les packages.

**3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?**

La version exacte garantit la reproductibilité de l'environnement. Avec `>=1.5`, Docker pourrait installer une version différente lors d'une nouvelle construction, ce qui peut provoquer des différences de comportement ou des problèmes de compatibilité.

**4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?**

Ces outils servent principalement au suivi des expériences, à la gestion des données et aux tests pendant le développement. Ils ne sont pas nécessaires à l'exécution normale de l'API. Leur exclusion permet de réduire la taille de l'image.

---

## 3. Sprint 1 : le Dockerfile

**Notre `Dockerfile` :**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-docker.txt requirements-docker.txt
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY maintai/ maintai/
COPY ui/ ui/

ENV MAINTAI_MODELS_DIR=/app/models
ENV MAINTAI_DATA_PATH=/app/data/sensors.csv

EXPOSE 8000

CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Mesures des builds :**

| Build | Durée | Taille de l'image |
|---|---|---|
| Premier build | Non mesurée | Image `maintai:0.4.0` créée |
| Après modification de `maintai/predict.py` | Non mesurée | Non mesurée |

**Que signifie `CACHED` dans le journal du second build ?**

`CACHED` signifie que Docker réutilise une couche déjà construite au lieu de l'exécuter à nouveau. Cela permet d'accélérer la construction de l'image.

---

## 4. Sprint 1 : lancer un conteneur

**Commande indicative pour lancer l'API seule :**

```powershell
docker run --rm --name test --env-file .env -p 8002:8000 -v "${PWD}/models:/app/models:ro" maintai:0.4.0
```

Cette commande est une proposition de test isolé ; le déploiement effectivement réalisé et vérifié a été fait avec Docker Compose.

**Résultats des essais :**

| Essai | Réponse |
|---|---|
| `GET /health` | HTTP 200, statut `ok`, modèle chargé (`true`) |
| `POST /v1/predict` sans clé | HTTP 401, clé API absente ou invalide |
| `POST /v1/predict` avec la clé | Prédiction réussie depuis l'interface Streamlit ; probabilité affichée : 95 % |

**Piège 1. Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?**

Sans le volume des modèles, le conteneur ne reçoit pas les fichiers du dossier `models` de la machine hôte. L'API peut démarrer, mais le modèle de prédiction risque de ne pas être chargé. `/health` peut alors signaler que le modèle n'est pas disponible et `/v1/predict` ne peut pas effectuer une prédiction normale.

**Piège 2. Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?**

Si Uvicorn écoute sur `127.0.0.1`, il écoute uniquement sur l'interface locale du conteneur. Les logs indiquent une écoute sur `127.0.0.1:8000`, mais l'accès depuis la machine hôte via le port publié peut échouer. Il faut utiliser `--host 0.0.0.0` pour rendre l'API accessible depuis l'extérieur du conteneur.

---

## 5. Sprint 2 : Docker Compose

**Notre `compose.yaml` :**

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
    env_file: .env
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
      MAINTAI_API_URL: "http://api:8000"
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data:ro
    depends_on:
      - api
```

**Sortie de `docker compose ps` :**

```text
NAME        IMAGE           COMMAND                  SERVICE   CREATED              STATUS              PORTS
tp6-api-1   maintai:0.4.0   "uvicorn maintai.api…"   api       About a minute ago   Up About a minute   0.0.0.0:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   "python -m streamlit…"   ui        About a minute ago   Up About a minute   0.0.0.0:8501->8501/tcp
```

**Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?**

L'URL est `http://api:8000`. Elle vient de la variable d'environnement `MAINTAI_API_URL` définie dans `compose.yaml`. Le nom `api` correspond au nom du service Docker Compose.

**Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`). Pourquoi la seconde échoue-t-elle ?**

Le test de résolution réseau entre les services n'a pas été conservé. Le comportement attendu est :

- `http://api:8000` fonctionne parce que Docker Compose fournit une résolution DNS interne entre les services.
- `http://localhost:8000` ne fonctionne pas depuis le conteneur UI, car `localhost` désigne le conteneur UI lui-même et non le conteneur API.

**Vérification réelle des variables d'environnement :**

```text
docker compose exec api python -c "import os; print(bool(os.getenv('MAINTAI_API_KEY')))"
True

docker compose exec ui python -c "import os; print(bool(os.getenv('MAINTAI_API_KEY')))"
True
```

**Dernière ligne de `python -m pytest` à la fin du sprint 2 :**

```text
38 passed, 4 warnings
```

---

## 6. Décision : l'ADR 005

La solution retenue consiste à utiliser une image Docker unique pour l'application MaintAI, réutilisée par les services API et UI dans Docker Compose. Les modèles, les données et les variables sensibles sont fournis séparément au lancement grâce aux volumes et au fichier `.env`, et non intégrés directement dans l'image.

---

## 7. Questions de compréhension

**1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.**

Dans l'image entrent Python, les dépendances installées depuis `requirements-docker.txt`, le code `maintai/` et le code `ui/`. Au lancement, les modèles et les données sont fournis par des volumes Docker, tandis que les variables d'environnement et la clé API sont transmises avec `env_file: .env`.

**2. Pourquoi la clé API n'est-elle jamais dans l'image ?**

Parce qu'une image Docker peut être partagée ou distribuée. Intégrer une clé API dans l'image exposerait un secret. Elle est donc fournie au lancement avec le fichier `.env`, qui reste local et ne doit pas être partagé.

**3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?**

Docker permet de livrer le modèle avec un environnement d'exécution reproductible : version de Python, dépendances, code de l'application, configuration et ports réseau. Il facilite ainsi le déploiement sur une autre machine sans devoir tout réinstaller manuellement.

---



## 8. Ce qui reste flou

Les mesures exactes de durée et de taille des builds, ainsi que les tests isolés avec `docker run` et le cas `127.0.0.1`, n'ont pas été réalisés ou conservés. Le fonctionnement de l'application avec Docker Compose, l'authentification API et la prédiction ont été vérifiés avec succès.

