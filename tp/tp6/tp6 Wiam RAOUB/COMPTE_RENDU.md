# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** G2  ·  **Membres :** Wiam RAOUB  ·  **Date :** 23 novembre 2026  ·  **Heure :** 11:36

> Les valeurs indiquées comme « à relever » ne sont pas conservées dans le projet ou l'historique disponible. Ne pas les remplacer par des estimations.

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) : à relever sur le poste utilisé.

Versions Docker vérifiées :

```
Client: 29.1.3
Server: 29.8.2
```

Dernière ligne de `python3 -m pytest -q` après la mise en place :

```
38 passed, 3 warnings in 13.01s
```

## 2. Image et conteneur (pendant le premier build)

1. Quelle différence entre une image et un conteneur ?

   Une image est le modèle immuable qui contient le système de fichiers, le code et les dépendances nécessaires. Un conteneur est une instance en cours d'exécution de cette image, avec sa configuration et ses connexions réseau.

2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?

   Docker peut mettre en cache l'installation des dépendances. Les modifications fréquentes du code ne forcent donc pas à réinstaller toutes les bibliothèques, tant que le fichier des dépendances n'a pas changé.

3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?

   Le modèle sérialisé a été entraîné avec scikit-learn 1.8.0. Fixer la même version dans l'image réduit les risques d'incompatibilité au chargement du modèle et rend les déploiements plus reproductibles.

4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?

   Ils servent respectivement au suivi des entraînements, au versionnement des données et aux tests ; ils ne sont pas nécessaires pour servir les prédictions. Les exclure allège l'image et limite les dépendances installées en production.

## 3. Sprint 1 : le Dockerfile

Votre `Dockerfile` :

```dockerfile
# Image de MaintAI : le code et ses bibliothèques, sans les données ni le modèle.
# Construire : docker build -t maintai:0.4.0 .

FROM python:3.11-slim

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY maintai ./maintai
COPY ui ./ui

ENV MAINTAI_MODELS_DIR=/app/models \
    MAINTAI_DATA_PATH=/app/data/sensors.csv

EXPOSE 8000

CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Build | Durée | Taille de l'image (`docker images`) |
|---|---|---|
| premier build | non relevée | non relevée |
| après une modification de `maintai/predict.py` | non relevée | non relevée |

Taille de l'image `maintai:0.4.0` vérifiée le 23 novembre 2026 : **1 155 643 772 octets** (environ 1,16 Go).

Que signifie `CACHED` dans le journal du second build ?

Docker a réutilisé le résultat d'une étape identique d'un build précédent au lieu de l'exécuter à nouveau. Les durées de build ne sont pas disponibles ; elles doivent être mesurées pendant les deux builds demandés.

## 4. Sprint 1 : lancer un conteneur

Commande macOS utilisée pour publier le port hôte 8082 vers le port 8000 du conteneur :

```bash
docker run -d --name maintai-api \
  -p 8082:8000 \
  --env-file .env \
  -v "$PWD/models:/app/models:ro" \
  maintai:0.4.0
```

| Essai | Réponse observée |
|---|---|
| `GET /health` | `200 OK`, `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` sans clé | `401 Unauthorized` |
| `POST /v1/predict` avec la clé configurée localement | `200 OK` ; avec le relevé de test, probabilité `0.9553`, alerte `true`, seuil `0.3` |

La clé API est volontairement omise de ce compte rendu.

**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?

`/health` répond `200 OK` avec `"model_loaded": false`, car l'API peut démarrer sans modèle. Une requête valide à `/v1/predict` répond `503 Service Unavailable` avec un message indiquant que le modèle n'est pas chargé. Le répertoire du modèle est absent du conteneur parce qu'il est exclu de l'image ; le montage `-v` le fournit au lancement.

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?

Les logs indiquent qu'Uvicorn écoute sur `127.0.0.1:8000` dans le conteneur. Depuis l'hôte, `http://localhost:8002/health` échoue à se connecter : le serveur n'écoute que sur l'interface de boucle locale du conteneur. Il faut écouter sur `0.0.0.0` pour rendre le port accessible via le port publié par Docker. Cet essai n'a pas été exécuté ici ; cette réponse décrit le résultat attendu.

## 5. Sprint 2 : Docker Compose

Votre `compose.yaml` :

```yaml
# MaintAI en deux conteneurs : l'API et l'interface Streamlit.
# Lancer : docker compose up --build      Arrêter : docker compose down

services:
  api:
    build: .
    image: maintai:0.4.0
    env_file: .env
    ports:
      - "8082:8000"
    volumes:
      - ./models:/app/models:ro

  ui:
    image: maintai:0.4.0
    command:
      ["python", "-m", "streamlit", "run", "ui/app.py",
       "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
    environment:
      MAINTAI_API_URL: http://api:8000
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data:ro
    depends_on:
      - api
```

Sortie de `docker compose ps` vérifiée :

```
NAME        IMAGE           SERVICE   STATUS        PORTS
tp6-api-1   maintai:0.4.0   api       Up            0.0.0.0:8082->8000/tcp
tp6-ui-1    maintai:0.4.0   ui        Up            0.0.0.0:8501->8501/tcp
```

Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?

Elle affiche `http://api:8000`, fourni par la variable d'environnement `MAINTAI_API_URL` dans `compose.yaml`. Dans le réseau Compose, `api` est le nom de service qui permet à l'interface de joindre le conteneur API.

Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`) :

```text
http://api:8000/health :
{"status":"ok","model_loaded":true}

http://localhost:8000/health :
Connection refused
```

Pourquoi la seconde échoue-t-elle ?

Dans le conteneur `ui`, `localhost` désigne le conteneur de l'interface lui-même, et non le conteneur `api`. Le nom de service `api` doit être utilisé pour communiquer entre conteneurs.

Dernière ligne de `python3 -m pytest -q` à la fin du sprint 2 :

```
38 passed, 3 warnings in 13.01s
```

## 6. Décision : l'ADR 005

Le fichier `docs/adr/005-image-docker.md` n'est pas présent dans le projet ; la décision ci-dessous résume l'architecture Docker actuelle.

L'image contient le code MaintAI et ses dépendances épinglées, mais ni données, ni modèle, ni secret. Au lancement, les données et le modèle sont montés en lecture seule, tandis que la clé API est injectée avec `env_file: .env`.

## 7. Questions de compréhension

1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.

   Le code des dossiers `maintai/` et `ui/`, ainsi que les bibliothèques épinglées de `requirements-docker.txt`, entrent dans l'image. Le modèle arrive via le montage `./models:/app/models:ro`, les données via `./data:/app/data:ro`, et la clé API depuis `.env` grâce à `env_file`.

2. Pourquoi la clé API n'est-elle jamais dans l'image ?

   Une image peut être partagée, stockée dans un registre ou inspectée ; une clé intégrée pourrait donc être divulguée et rester dans les couches de l'image. La fournir à l'exécution permet de la garder hors de l'image et de la remplacer sans reconstruire celle-ci.

3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?

   Docker fournit un environnement reproductible avec une version de Python et des dépendances définies, emballe le service dans une image et permet de le lancer avec une configuration, des volumes et des ports contrôlés. Le modèle lui-même reste un artefact externe monté au lancement.

## 8. Le rendu Git

- Pull request : aucune ; les fichiers ont été poussés directement sur `main`. Commits : [ajout initial](https://github.com/wiam1237/classification-des-reclamations-clients/commit/116a5f02cc7046f67ab8177fa3ce066b82781e40) et [réorganisation dans le dossier demandé](https://github.com/wiam1237/classification-des-reclamations-clients/commit/9eba1bdbf72351d2e33388a8620f192cedfcbfec).
- Tag `tp6` sur GitHub : oui, créé sur la version finale du TP6.
- `git status` avant le premier commit : le clone GitHub était propre (`main...origin/main`). Après préparation, seuls les fichiers destinés à `tp/tp6/tp6 Wiam RAOUB/` ont été ajoutés ; `.env`, `models/` et les fichiers CSV générés en ont été exclus. Le dossier local `/Users/wiam/Downloads/TP6` n'est pas lui-même un dépôt Git.

## 9. Ce qui reste flou

À relever si demandé dans le rendu : la sortie de `docker run hello-world`, les durées des deux builds, la taille de l'image immédiatement après chacun de ces builds, et les informations du dépôt distant (PR et tag `tp6`). Le fichier `docs/adr/005-image-docker.md` mentionné dans l'énoncé est absent du projet fourni.
