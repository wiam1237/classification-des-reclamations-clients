# Compte rendu – Séance 5 – Tester, sécuriser et appeler l’API MaintAI

## 1. Objectif du TP

Le TP visait à tester, sécuriser et exploiter une API de prédiction de panne de capteurs développée dans le cadre de MaintAI. L’objectif principal était de valider le bon fonctionnement du projet, de protéger les points d’entrée sensibles avec une clé API, puis de vérifier le comportement attendu en production locale avec les outils standards du projet.

Le travail s’est articulé autour de plusieurs étapes :

- préparation de l’environnement et installation des dépendances ;
- génération du dataset synthétique ;
- entraînement du modèle de détection de panne ;
- sécurisation des routes de l’API ;
- exécution des tests automatiques ;
- lancement du serveur local ;
- validation de la route protégée `/v1/predict` sans clé API.

---

## 2. Préparation de l’environnement et installation des dépendances

Le projet a d’abord été préparé dans un environnement virtuel Python afin d’isoler les dépendances du projet.

Les commandes réalisées sont les suivantes :

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Les dépendances listées dans le fichier `requirements.txt` ont ainsi été installées dans le bon environnement, ce qui a permis de lancer le projet et de faire tourner les tests sans conflit avec le système Python global.

---

## 3. Génération du dataset

Le dataset synthétique a été généré à partir du module suivant :

```bash
python -m maintai.dataset
```

Cette commande produit les données utilisées par le modèle, en particulier le fichier de données dans le dossier `data/`.

Cette étape est essentielle, car les modèles de prédiction de panne reposent sur des relevés de capteurs synthétiques structurés selon les colonnes attendues par le projet.

---

## 4. Entraînement du modèle

Le modèle a ensuite été entraîné avec la commande suivante :

```bash
python -m maintai.train
```

Cette commande permet de :

- charger les données ;
- entraîner le modèle ;
- calculer les métriques d’évaluation ;
- sauvegarder les artefacts du modèle dans le dossier `models/`.

Le projet utilise les fichiers générés par le module `train.py` pour alimenter ensuite le moteur de prédiction lors des appels API.

---

## 5. Sécurisation de l’API avec la clé API

La sécurisation de l’API a été implémentée au niveau des routes protégées.

### 5.1. Fichier `maintai/api/security.py`

Le module `security.py` contient la fonction `require_api_key`, qui vérifie la présence et la validité de la clé API transmise dans le header `X-API-Key`.

Le comportement attendu est le suivant :

- si la clé n’est pas définie sur le serveur, la requête est refusée avec un `500 Internal Server Error` ;
- si la clé manque ou est invalide, la requête est refusée avec un `401 Unauthorized` ;
- si la clé est correcte, la requête est autorisée.

La vérification est faite en utilisant `secrets.compare_digest`, ce qui permet de comparer les chaînes de manière sécurisée et robuste.

### 5.2. Fichier `maintai/api/main.py`

Dans `main.py`, le routeur `/v1` est déclaré avec la dépendance `Depends(require_api_key)`. Cela protège automatiquement toutes les routes de l’API sous le préfixe `/v1`, notamment `/v1/predict`.

Autrement dit, toute demande qui n’inclut pas la clé API valide est automatiquement rejetée avant même d’atteindre la logique de prédiction.

---

## 6. Tests effectués

Les tests du projet ont été exécutés via :

```bash
python -m pytest
```

Résultat vérifié :

- 18 tests réussis
- 1 warning

Commande exécutée dans l’environnement virtuel du projet :

```bash
.\.venv\Scripts\python.exe -m pytest -q
```

Résultat réel obtenu :

```text
18 passed, 1 warning in 10.02s
```

Le warning observé est un avertissement de dépréciation lié à `starlette.testclient` / `httpx`, sans impact sur la validité fonctionnelle du projet.

---

## 7. Lancement du serveur et validation sécurisée

Le serveur a été lancé avec Uvicorn :

```bash
uvicorn maintai.api.main:app --host 127.0.0.1 --port 8001
```

Puis, avec la configuration chargée depuis le fichier `.env` :

```bash
uvicorn maintai.api.main:app --host 127.0.0.1 --port 8001 --env-file .env
```

L’application est ensuite accessible via la documentation Swagger à l’URL locale du serveur :

```text
http://127.0.0.1:8001/docs
```

### Test sans clé API

Une requête envoyée vers `/v1/predict` sans clé API a bien été refusée, avec le statut HTTP attendu :

```text
401 Unauthorized
```

Cela confirme que la protection par clé API est bien active et fonctionne comme prévu.

---

## 8. Résultat final

Le projet MaintAI a donc bien été validé sur les points suivants :

- génération du dataset réussie ;
- entraînement du modèle effectué ;
- API sécurisée au moyen d’une clé API ;
- tests fonctionnels validés ;
- route principale protégée correctement.

Le bilan final est favorable :

- 18 tests passent ;
- 1 warning non bloquant ;
- sécurité API activée et vérifiée.

---

## 9. Fichiers sensibles et gestion du dépôt GitHub

Dans le cadre du dépôt GitHub, les fichiers suivants sont et doivent rester exclus du versionnement :

- `.env`
- `.venv/`
- les fichiers contenant des clés API, mots de passe ou tokens
- les artefacts non nécessaires au code source du TP

Le fichier `.gitignore` du projet contient déjà les règles adaptées pour ignorer les éléments sensibles. Cette règle a été respectée afin de ne pas publier de secrets ou de variables d’environnement dans le dépôt distant.

---

## 10. Conclusion

La séance 5 a permis de consolider le projet MaintAI à travers plusieurs dimensions : validation logicielle, protection des points d’entrée, et mise en œuvre d’une API sûre et exploitable.

Le travail accompli montre que le projet est correctement fonctionnel, testable et protégé. La solution est prête à être partagée sous forme de code et de documentation, sans exposer les informations sensibles ou les données de configuration locales.

Aucune capture d’écran n’a été ajoutée au dépôt dans le cadre de ce TP, mais les commandes, résultats et validations décrits ci-dessus reflètent bien le travail réellement effectué dans le projet.
