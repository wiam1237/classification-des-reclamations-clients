# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Nom :** Sanaa Kastass (`SANAAk2003`)  ·  **Groupe :** non renseigné  ·  **Date :** 26/10/2026
**Membres du groupe :** non renseignés

> Complétez les espaces avec vos résultats et vos propres explications. Collez les sorties réelles du terminal entre les blocs de code ; ne recopiez pas un résultat attendu si vous ne l'avez pas obtenu.

## 1. Mise en place et état initial

Commandes exécutées depuis `TP/TP1` :

```text
python -m maintai.dataset
python -m maintai.train
python -m pytest
```

Résultat avant les modifications :

```text
Non relevé avant que le schéma et la fonction predict() soient complétés.
```

Le polycopié indique comme résultat attendu **3 failed, 10 passed**. Dans `tests/test_api.py`, les quatre tests qui passent déjà dans le starter sont `test_health`, `test_out_of_range_value_is_rejected`, `test_missing_field_is_rejected` et `test_openapi_documents_predict`.

Pourquoi les deux tests 422 passent-ils pour une mauvaise raison au départ ?

Réponse : `SensorReading` ne déclare encore aucun champ, et `extra="forbid"` refuse les quatre champs du relevé comme champs inconnus. Le 422 ne prouve donc pas encore que les bornes ou les champs obligatoires sont correctement définis. En d'autres termes, même une requête correcte est rejetée parce que le schéma n'accepte pas encore ses champs.

## 2. Schéma d'entrée : `maintai/api/schemas.py`

Les quatre champs doivent être de type `float`. Choisissez des limites physiquement plausibles pour un moteur, et non les extrêmes observés dans le jeu synthétique.

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique de mes limites |
|---|---|---:|---:|---|
| `temperature_c` | `float` | -40 °C | 150 °C | Plage de température retenue pour le moteur ; les températures en dehors de cette plage sont considérées hors domaine. |
| `vibration_mm_s` | `float` | 0 mm/s | 50 mm/s | Une vitesse vibratoire ne peut pas être négative ; la limite haute permet de détecter aussi des vibrations anormalement fortes. |
| `load_pct` | `float` | 0 % | 100 % | Une charge exprimée en pourcentage va de l'arrêt à la charge nominale. |
| `runtime_hours` | `float` | 0 h | 100 000 h | Un compteur d'heures ne peut pas être négatif ; la limite haute est une plage applicative à confirmer avec les spécifications de la machine. |

Résultat de l'étape intermédiaire (schéma modifié seul) :

```text
Cette exécution intermédiaire n'a pas été capturée avant l'implémentation de predict(). Le comportement attendu décrit dans le TP est NotImplementedError pour les relevés valides, car ils atteignent alors predict().
```

Quel message d'erreur remplace alors les erreurs 422 des relevés valides ? Pourquoi est-ce un bon signe à cette étape ?

Réponse : `NotImplementedError`. C'est le signe que le schéma accepte désormais les relevés valides et que la requête est arrivée jusqu'à `predict()`, dont le corps reste à implémenter à cette étape.

Dans `/docs`, les bornes et descriptions des champs apparaissent dans le schéma de `SensorReading` pour `POST /v1/predict`. Vérifiez aussi qu'un relevé normal est accepté et qu'une température de 500 °C est refusée en 422.

## 3. Prédiction et modèle absent

Collez ici votre fonction `predict()` terminée :

```python
predictor = state.get("predictor")
if predictor is None:
	raise HTTPException(
		status_code=503,
		detail="Modèle indisponible. Exécutez python -m maintai.train puis redémarrez l'API.",
	)
return PredictionOut(**predictor.predict(reading.model_dump()))
```

Pourquoi l'API répond-elle **503 Service Unavailable** si le modèle n'est pas chargé, plutôt que 500 ?

Réponse : 503 signale que le service ne peut momentanément pas traiter la demande, ici parce que le modèle doit être généré/chargé. 500 indiquerait plutôt une erreur inattendue dans le serveur. Il faut exécuter `python -m maintai.train`, puis redémarrer l'API.

Pourquoi le modèle est-il chargé une seule fois au démarrage, et non à chaque requête ?

Réponse : le chargement du modèle est coûteux ; le faire une seule fois au démarrage évite de répéter ce travail pour chaque requête et permet de réutiliser le même prédicteur.

### Décision d'architecture : ADR 002

Fichier créé : `docs/adr/002-validation.md` (copie de `docs/adr/000-modele.md`).

- Justification physique de mes limites : voir le tableau de la section 2. Les limites doivent être confirmées par rapport aux spécifications du moteur et de ses capteurs réels.
- Décision si le modèle manque : l'API démarre et répond 503.
- Avantage de cette option : `/health` reste accessible et indique `model_loaded: false`, ce qui facilite le diagnostic avant l'entraînement.
- Inconvénient de cette option : les prédictions restent indisponibles tant que le modèle n'a pas été entraîné et que l'API n'a pas été redémarrée.

## 4. Tests finaux

Sortie réelle de `python -m pytest` après avoir terminé le schéma et `predict()` :

```text
13 passed, 1 warning in 4.74s
```

Le TP attend **13 passed**. Résultat obtenu : **13 passed, 1 warning in 4.74s**. L'avertissement signale que l'utilisation de `httpx` avec `starlette.testclient` est dépréciée ; il n'empêche pas les tests de réussir.

## 5. Vérification de l'API

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`. Essayez les requêtes depuis `http://localhost:8000/docs` et copiez le code HTTP ainsi que le corps JSON renvoyé.

| Requête | Code HTTP obtenu | Corps JSON obtenu |
|---|---:|---|
| `GET /health` | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` avec `{"temperature_c":72.5,"vibration_mm_s":6.1,"load_pct":85,"runtime_hours":15000}` | 200 | `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-10-26T18:22:51Z"}` |
| `POST /v1/predict` avec le relevé précédent et `temperature_c` à `500` | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}` |
| `POST /v1/predcit` (route inexistante, faute de frappe) | 404 | `{"detail":"Not Found"}` |

Pour la requête invalide, quel composant refuse la valeur et à quel moment ?

Réponse : le schéma Pydantic `SensorReading` valide la requête dans FastAPI avant d'appeler `predict()`. La valeur 500 dépasse la borne maximale de 150 °C, donc FastAPI renvoie 422 sans appeler le modèle.

## 6. Questions de compréhension

1. **REST et FastAPI : quelle est la différence ?** REST est un ensemble de principes de conception d'API web ; FastAPI est une bibliothèque Python permettant de construire une API qui les applique. En bref, REST décrit des règles de conception, FastAPI est l'outil utilisé pour les mettre en œuvre.
2. **Quelles sont les trois utilisations du schéma Pydantic ?** Valider les entrées, générer la documentation OpenAPI `/docs`, et fournir à la fonction un objet Python typé. La même définition sert donc à contrôler, documenter et manipuler les données.
3. **Que désignent `localhost`, `8000` et `/v1/predict` dans `http://localhost:8000/v1/predict` ?** `localhost` est la machine locale, `8000` le port où le serveur écoute, et `/v1/predict` la route versionnée qui réalise la prédiction.
4. **Pourquoi inclure `/v1` dans l'adresse ?** Pour identifier la version du contrat de l'API et permettre de faire évoluer celui-ci sans casser les clients de l'ancienne version.
5. **Que désignent `maintai.api.main` et `app` dans `uvicorn maintai.api.main:app` ?** `maintai.api.main` désigne le module `maintai/api/main.py`, et `app` la variable de ce module qui contient l'application FastAPI.
6. **Quel code HTTP correspond à chaque situation ?** Température 500 °C : 422 ; route inconnue : 404 ; modèle absent : 503 ; clé API absente (lorsqu'elle sera mise en place) : 401 ; bug serveur : 500. Pour la température, le schéma Pydantic est validé par FastAPI avant l'appel à la fonction de prédiction.

## 7. Rendu Git et relecture

- Dépôt GitHub : https://github.com/wiam1237/classification-des-reclamations-clients
- Branche du TP : `tp1` (branche distante vérifiée)
- Emplacement du rapport : `tp/tp1/COMPTE_RENDU Sanaa Kastass.md`
- État local : le starter téléchargé n'est pas un clone Git ; le rapport sera ajouté au dépôt distant en clonant la branche `tp1` dans un dossier de travail séparé.
- Lien de la pull request : aucun lien fourni ou créé à ce stade ; le TP demande de pousser le rapport dans la branche `tp1`.
- Nom du relecteur et commentaire laissé : non disponibles ; à renseigner après relecture de la PR.
- Pull request fusionnée : sans objet pour le push du rapport dans la branche existante ; état à vérifier avec le groupe pour le rendu final du TP.
- Tag `tp1` présent sur GitHub : non vérifié.
- Vérification du relecteur : les tests locaux passent (`13 passed`). Un coéquipier doit encore relire ce rapport et laisser un commentaire conformément au TP.

## 8. Bilan personnel

Ce qui m'a posé problème et comment je l'ai résolu : il fallait distinguer un 422 causé par un schéma encore vide d'un 422 causé par une vraie valeur hors limites. J'ai vérifié que les quatre champs étaient déclarés, puis que les tests et la requête à 500 °C donnaient respectivement le succès attendu et le 422 de validation.

Ce qui reste flou : les bornes physiques définitives de vibration et de durée de fonctionnement dépendent du moteur et des capteurs réellement utilisés ; elles doivent être confirmées à partir de leurs spécifications.
