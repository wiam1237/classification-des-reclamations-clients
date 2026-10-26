# Compte rendu · TP1 : une API de prédiction pour MaintAI
 **Date :** 26/10/2026


---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
7 passed, 4 failed
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ?

- `test_health`
- `test_predict_returns_probability`
- `test_high_risk_reading_raises_alert`
- `test_openapi_documents_predict`

Les deux tests qui attendent un code 422 passent « pour une mauvaise raison » parce que le schéma `SensorReading` n'avait pas encore de champs. Avec `extra="forbid"`, tous les champs envoyés dans le JSON sont considérés comme des clés inconnues. Donc un payload valide ou presque est rejeté avant même la validation métier des bornes. En pratique, le 422 est provoqué par le fait qu'il n'y a pas de champ déclaré dans le modèle, et non par la logique de validation.

Exemple :

```python
model_config = ConfigDict(extra="forbid")
```

Avec ce paramètre, les entrées comme `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours` sont refusées si le modèle ne les définit pas.

---

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | float | -40 | 150 | La température d'une machine industrielle peut être très basse au démarrage, mais des valeurs de fonctionnement normales restent en dessous de 150 °C ; au-delà, on considère un état anormal. |
| `vibration_mm_s` | float | 0 | 50 | La vibration est positive par définition et des niveaux très élevés indiquent un risque de dégradation mécanique. |
| `load_pct` | float | 0 | 100 | Le pourcentage de charge doit rester entre 0 et 100 % ; au-delà, la donnée n'est pas réaliste pour une charge de travail. |
| `runtime_hours` | float | 0 | 100000 | Le temps de fonctionnement total est intrinsèquement positif et ne peut pas être négatif ; la borne supérieure couvre les machines à forte durée de fonctionnement. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
11 passed, 2 failed
```

Les tests qui échouent sont ceux qui attendent la logique `predict()` : `test_503_when_model_missing` et le test de `predict()` complet. Le message principal est un `NotImplementedError` ou, plus précisément, un échec lié à la route `/v1/predict` qui n'a pas encore été implémentée.

C'est un bon signe, car cela montre que la structure de l'API et la validation du schéma fonctionnent déjà : il reste uniquement la logique métier à ajouter.

---

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
def predict(reading: SensorReading) -> PredictionOut:
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return predictor.predict(reading.model_dump())
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

Parce que le modèle n'est pas disponible au moment de l'appel, mais c'est une condition métier connue et attendue : l'API est démarrée mais le fichier du modèle n'a pas encore été entraîné ou trouvé. `503 Service Unavailable` est plus explicite qu'un `500 Internal Server Error` et indique au client que le service n'est pas prêt pour traiter la prédiction.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Parce que le chargement du modèle est coûteux en temps et en mémoire. Le code utilise `lifespan` avec `state["predictor"] = Predictor.load(...)`, ce qui permet de charger le modèle une seule fois au démarrage de l'application, puis de réutiliser l'objet en mémoire pour toutes les requêtes.

---

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
13 passed, 1 warning in 1.23s
```

Le warning vient de FastAPI/Starlette sur `TestClient` avec `httpx` : c'est un avertissement de dépréciation, pas un échec de tests.

---

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, puis lancement avec `uvicorn maintai.api.main:app --reload --port 8081` (car le port 8000 était déjà occupé), on obtient les résultats suivants.

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | 200 | `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-10-26T12:25:51Z"}` |
| `POST /v1/predict` avec une température de 500 | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail":"Not Found"}` |

Dans `/docs`, où voit-on les bornes que vous avez choisies ?

Dans la section du schéma `SensorReading`, sous les champs de la requête. FastAPI affiche automatiquement les contraintes `ge` et `le` dans le Swagger UI. On voit notamment les limites en rouge ou dans le modèle de données, comme `temperature_c <= 150`, `vibration_mm_s <= 50`, `load_pct <= 100`, `runtime_hours <= 100000`.

---

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   - REST est un style d'architecture pour les API, basé sur les ressources et les verbes HTTP.
   - FastAPI est un framework Python qui permet de créer facilement des APIs REST avec validation automatique, génération de documentation OpenAPI et sérialisation JSON.

2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   - Valider les données entrantes.
   - Convertir les entrées JSON vers des objets Python typés.
   - Générer automatiquement la documentation OpenAPI/Swagger.

3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   - `localhost` : l'ordinateur courant.
   - `8000` : le port d'écoute du serveur.
   - `/v1/predict` : le chemin de la ressource API, versionnée en `v1`.

4. Pourquoi `/v1` dans l'adresse ?
   Parce que l'API est versionnée. Cela évite les ruptures de compatibilité et permet d'ajouter des évolutions futures sans casser les clients existants.

5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   - `maintai.api.main` : le module Python qui contient l'application FastAPI.
   - `app` : l'objet FastAPI instancié dans ce module, utilisé par uvicorn pour démarrer le serveur.

---

## 7. Le rendu Git

- Lien de la pull request : À compléter
- Le tag `tp1` existe sur GitHub : à vérifier / à compléter
- Qui a relu la pull request, et quel commentaire a-t-il laissé ? À compléter

---

## 8. Ce qui reste flou

- Vérification du dépôt Git distant et du tag `tp1`.
- Nom exact du relecteur GitHub et commentaire qu'il a laissé sur la PR.
- Le port exact utilisé dans l'environnement final peut varier selon les services déjà présents sur la machine (`8000` souvent occupé, donc `8081` peut être utilisé pour tester localement).
