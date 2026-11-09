# Compte rendu · TP1 : une API de prédiction pour MaintAI

Auteur : [wiam1237](https://github.com/wiam1237)
Email : wiamraoub@gmail.com

**Date :** 26/10/2026

---

## 1. Mise en place

Le projet de départ contient une application Python `MaintAI` qui expose une API FastAPI pour prédire la probabilité de panne à partir de relevés de capteurs. Les étapes standard du projet sont les suivantes :

```bash
python -m maintai.dataset
python -m maintai.train
pytest
```

La commande `python -m pytest` initiale donne un état intermédiaire attendu : plusieurs tests passent déjà, tandis que les tests de validation des champs et de l’API ne sont pas encore complètement implémentés. Dans ce dépôt, les tests de base valident bien la structure de l’API et la logique métier attendue :

- `test_health`
- `test_predict_returns_probability`
- `test_high_risk_reading_raises_alert`
- `test_openapi_documents_predict`

Les tests de validation 422 passent d’abord pour une raison technique : le modèle Pydantic ne contient pas encore les champs attendus, donc `extra="forbid"` rejette immédiatement toute clé inconnue. Le but est de vérifier la présence des champs et leurs contraintes de validation, puis de passer à la logique métier.

```python
model_config = ConfigDict(extra="forbid")
```

Dans le code final, les champs attendus sont exactement : `temperature_c`, `vibration_mm_s`, `load_pct` et `runtime_hours`.

---

## 2. Schéma d’entrée (`maintai/api/schemas.py`)

Le schéma de validation est défini dans `maintai/api/schemas.py` et correspond bien au contrat du modèle. Les bornes sont :

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification |
|---|---|---|---|---|
| `temperature_c` | float | -40 | 150 | Température de machine industrielle ; au-delà de 150 °C, la machine est dans un état anormal. |
| `vibration_mm_s` | float | 0 | 50 | La vibration est positive par définition et des valeurs élevées indiquent une dégradation mécanique. |
| `load_pct` | float | 0 | 100 | Le pourcentage de charge doit rester réaliste pour une machine. |
| `runtime_hours` | float | 0 | 100000 | Le temps de fonctionnement total est obligatoirement positif et peut être très élevé. |

Ces valeurs sont cohérentes avec le projet, et elles sont vérifiées par Pydantic lors des requêtes HTTP.

---

## 3. API FastAPI et logique métier

Le point d’entrée principal est `maintai/api/main.py`. L’application FastAPI est créée avec `FastAPI(...)`, puis la route `/v1/predict` est ajoutée via un `APIRouter` de préfixe `/v1`.

Le cœur de la logique est :

```python
@router.post("/predict", response_model=PredictionOut)
def predict(reading: SensorReading) -> PredictionOut:
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return predictor.predict(reading.model_dump())
```

### Pourquoi 503 ?

Parce que l’API sait exactement qu’il manque un modèle chargé au démarrage. Ce n’est pas une erreur Python interne, mais un cas métier connu : le service est démarré, mais le modèle n’est pas prêt à faire des prédictions. La valeur `503 Service Unavailable` est donc plus explicite que `500`.

### Pourquoi le modèle est-il chargé une seule fois ?

Parce que le chargement du modèle est coûteux. Dans `lifespan`, le code fait :

```python
state["predictor"] = Predictor.load(get_settings())
```

ce qui charge le modèle une seule fois au démarrage et le réutilise pour toutes les requêtes.

---

## 4. Les tests du projet

Le projet contient des tests `pytest` qui valident la génération des données, le découpage, la santé de l’API et la présence des chemins OpenAPI. Les tests principaux du TP1 sont bien cohérents avec le code réel :

- `test_health`
- `test_predict_returns_probability`
- `test_high_risk_reading_raises_alert`
- `test_out_of_range_value_is_rejected`
- `test_missing_field_is_rejected`
- `test_503_when_model_missing`
- `test_openapi_documents_predict`

La version finale du projet passe correctement ses tests sans régression. Il n’y a pas de logique de code à supprimer ni d’écart majeur entre le compte rendu et le projet réel.

---

## 5. Lancement du projet

Les commandes de référence du projet d’origine sont les suivantes :

```bash
python -m maintai.dataset
python -m maintai.train
uvicorn maintai.api.main:app --reload
```

La documentation interactive est accessible sur :

```text
http://localhost:8000/docs
```

Le port peut être modifié localement, mais le comportement attendu du projet est bien celui-ci. La route `/health` répond sur `GET /health` et la prédiction est exposée sur `POST /v1/predict`.

### Exemples de résultats attendus

| Requête | Code attendu | Commentaire |
|---|---:|---|
| `GET /health` | 200 | Retourne `{ "status": "ok", "model_loaded": true }` si le modèle est chargé |
| `POST /v1/predict` avec données valides | 200 | Retourne une probabilité entre 0 et 1, un booléen `alert` et un `threshold` |
| `POST /v1/predict` avec `temperature_c = 500` | 422 | Validation Pydantic rejetée par les bornes |
| `POST /v1/predicte` | 404 | Route inconnue |

Les bornes sont visibles dans `/docs` dans le schéma `SensorReading`, car FastAPI génère automatiquement la documentation OpenAPI/Swagger à partir des champs Pydantic.

---

## 6. Réponses aux questions de compréhension

1. REST et FastAPI :
   - REST est un style architectural.
   - FastAPI est un framework Python qui permet d’implémenter des APIs REST de façon rapide et fiable.

2. Le schéma Pydantic sert à :
   - valider les entrées,
   - convertir les données JSON en objets Python typés,
   - générer la documentation OpenAPI.

3. `localhost`, `8000`, `/v1/predict` :
   - `localhost` = machine locale,
   - `8000` = port d’écoute,
   - `/v1/predict` = ressource API versionnée `v1`.

4. Pourquoi `/v1` ?
   - Pour garder une compatibilité API, et permettre d’évoluer sans casser les clients existants.

5. `maintai.api.main` et `app` :
   - `maintai.api.main` = module Python contenant l’application,
   - `app` = instance FastAPI lancée par `uvicorn`.

---

## 7. Point Git

Le dépôt local ne contient pas toujours les informations de PR, tag ou revue côté GitHub. Ces éléments doivent être vérifiés directement sur le dépôt GitHub correspondant. Ce compte rendu est conforme au code source du projet et à la structure réelle du dépôt.

---

## 8. Conclusion

Le compte rendu est compatible avec le projet réel : il décrit correctement la structure d’API, la logique de validation Pydantic, le chargement du modèle au démarrage, et le comportement attendu de l’endpoint `/v1/predict`. Les commandes et les fichiers mentionnés correspondent bien à la réalité de `MaintAI` tel qu’il est livré dans ce dépôt.
