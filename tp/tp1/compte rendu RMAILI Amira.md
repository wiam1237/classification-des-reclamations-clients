# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** 2  ·  **Membres :** RMAILI Amira (compte rendu rédigé par RMAILI Amira)  ·  **Date :** 26/10/2026

> Rendu avec la pull request du TP1.

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
3 failed, 10 passed
```

Les 4 tests de `tests/test_api.py` qui passent déjà sont : `test_health`, `test_out_of_range_value_is_rejected`, `test_missing_field_is_rejected` et `test_openapi_documents_predict`. Les deux tests qui attendent un 422 passent « pour une mauvaise raison » : la classe `SensorReading` n'a encore aucun champ et `extra="forbid"` refuse tout champ inconnu, donc **n'importe quel** relevé est rejeté avec un 422, même un relevé valide. Le test de la température à 500 est vert alors que le schéma ne contrôle encore rien ; le test du champ manquant aussi. Un test vert ne prouve rien tant qu'on ne sait pas pourquoi il est vert.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | float | -40 | 150 | Plage des capteurs industriels ; au-delà de 150 °C à la sonde, le moteur est détruit ou le capteur défaillant ; -40 °C : atelier non chauffé |
| `vibration_mm_s` | float | 0 | 50 | Une vitesse efficace n'est jamais négative ; la zone dangereuse (ISO 10816) est autour de 7 à 18 mm/s, 50 laisse de la marge |
| `load_pct` | float | 0 | 150 | 0 % = à l'arrêt, 100 % = nominal, surcharge temporaire possible jusqu'à 150 % |
| `runtime_hours` | float | 0 | 100000 | Un compteur n'est pas négatif ; 100 000 h ≈ 11 ans de marche continue, plus que la vie d'un moteur |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
E   NotImplementedError
3 failed, 10 passed
```

Il y a toujours 3 échecs, mais l'erreur n'est plus un 422 : c'est `NotImplementedError`. C'est un bon signe : le schéma accepte désormais les relevés valides, la requête franchit la validation et arrive jusqu'à la fonction `predict()`, qui n'est simplement pas encore écrite. Les tests qui attendent 422 (500 °C, champ manquant) passent maintenant pour la bonne raison : c'est le schéma qui refuse.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
def predict(reading: SensorReading) -> PredictionOut:
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé : lancez « python -m maintai.train », puis redémarrez l'API.",
        )
    return PredictionOut(**predictor.predict(reading.model_dump()))
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

Un 500 signifie « bug dans le code du serveur » ; ici le code est correct, c'est le service qui est temporairement indisponible parce que le modèle n'a pas été chargé. Le 503 le dit au client (qui peut réessayer plus tard) et le message du `detail` indique comment réparer.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Lire et désérialiser `model.joblib` sur le disque est lent par rapport à une prédiction (quelques millisecondes pour une prédiction, beaucoup plus pour charger le fichier) : le refaire à chaque requête ralentirait l'API et la rendrait inutilisable avec beaucoup de clients. Chargé une fois dans `state`, le modèle est partagé par toutes les requêtes ; et si le fichier manque, on le sait dès le démarrage (`/health`).

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
============================== 13 passed, 1 warning in 6.64s ===============================
```

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | 200 | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | 200 | `{"failure_probability": 0.9553, "alert": true, "threshold": 0.3, "model_version": "<date d'entraînement>"}` (la probabilité peut différer légèrement selon vos données) |
| `POST /v1/predict` avec une température de 500 | 422 | `{"detail": [{"type": "less_than_equal", "loc": ["body", "temperature_c"], "msg": "Input should be less than or equal to 150", "input": 500, ...}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail": "Not Found"}` |

Dans `/docs`, où voit-on les bornes que vous avez choisies ?

Dans la route `POST /v1/predict`, rubrique « Schemas » / « SensorReading » et dans l'exemple de corps de requête : chaque champ y apparaît avec son type, sa description, et ses bornes (`minimum`, `maximum`).

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   REST est un ensemble de règles de conception d'une API web (URL claires, méthodes HTTP, codes précis, JSON, version). FastAPI est une bibliothèque Python avec laquelle on écrit une API qui suit ces règles ; uvicorn est le programme qui la fait tourner.
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   Valider les requêtes (code 422 avant d'appeler la fonction), documenter (page `/docs` générée automatiquement) et fournir à la fonction un objet Python typé (`reading.temperature_c` est un float déjà vérifié, `model_dump()` donne un dictionnaire).
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   `localhost` : la machine elle-même (le serveur tourne sur mon PC) ; `8000` : le port où uvicorn écoute ; `/v1/predict` : la route, un chemin choisi dans le code Python (pas un dossier du disque), en version 1.
4. Pourquoi `/v1` dans l'adresse ?
   Pour versionner l'API : on pourra faire évoluer le contrat (une `/v2` avec d'autres champs) sans casser les clients qui utilisent encore la `/v1`.
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   `maintai.api.main` est le fichier `maintai/api/main.py` (sans `.py`, avec des points) ; `app` est la variable de ce fichier qui contient l'application (`app = FastAPI(...)`).

## 7. Le rendu Git

- Lien de la pull request : https://github.com/wiam1237/classification-des-reclamations-clients/pull/[numéro]
- Le tag `tp1` existe sur GitHub : non (il se crée après la fusion de la pull request : `git tag tp1`, puis `git push --tags`)
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  [nom du relecteur] : « [son commentaire] »

## 8. Ce qui reste flou

- Comment choisir des bornes quand on n'a pas la fiche technique de la machine : j'ai pris des bornes larges fondées sur la physique (une température de 150 °C, une vibration de 50 mm/s), mais je ne suis pas sûre qu'elles soient justes pour un vrai moteur ; il faudrait demander à l'équipe de maintenance.
- Que faire d'un relevé valide mais très éloigné des données d'entraînement (par exemple 80 000 heures de fonctionnement alors que le modèle n'a vu que des valeurs jusqu'à 20 000) : le schéma l'accepte, mais la probabilité renvoyée est peu fiable.
- Quand préférer répondre 503 plutôt que refuser de démarrer : j'ai choisi le 503 dans l'ADR 002, mais je ne vois pas encore comment on s'aperçoit en pratique qu'un modèle manque avant qu'un client reçoive l'erreur.
