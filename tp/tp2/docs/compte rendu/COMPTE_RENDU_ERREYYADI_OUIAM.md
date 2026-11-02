# Compte rendu — TP2 : Tester, sécuriser et appeler l'API MaintAI

**ERREYYADI Ouiam**  
**Date : 02/11/2026**

> Remplir chaque partie de ce document et le remettre avec la Pull Request du TP2. Les sorties du terminal doivent être copiées entre les blocs de code.

---

## 1. Activité 1 : Casser son API (dans `tp/tp1`)

### Les cinq requêtes

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---:|---:|
| 1 | Champ manquant | 422 | 422 |
| 2 | Valeur absurde | 422 | 422 |
| 3 | Texte au lieu d'un nombre | 422 | 422 |
| 4 | Champ supplémentaire | 422 | 422 |
| 5 | Mauvaise route | 404 | 404* |

**Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?**

Non, aucune de nos prévisions n'était fausse. Les cinq requêtes ont retourné les codes HTTP attendus : 422 pour les données invalides et 404 pour la route inexistante.

Cela montre que l'API valide correctement les données reçues et détecte les routes qui n'existent pas.

### Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `tp/tp1`)

```text
==================== 19 passed, 1 warning in 4.60s ====================
```

J'ai obtenu 19 tests au lieu des 18 prévus, car mon projet contient un test supplémentaire dans le fichier `test_demo.py` : `test_500_degres_est_refuse`. Ce test vérifie que l'API refuse une température de 500 °C.

Les 18 tests prévus par le TP sont donc complétés par ce test supplémentaire.

**À quoi sert `@pytest.mark.parametrize` ? Combien de tests Pytest compte-t-il pour votre fonction, et pourquoi ?**

Le décorateur `@pytest.mark.parametrize` permet d'exécuter une même fonction de test avec plusieurs jeux de paramètres, sans devoir créer une fonction différente pour chaque scénario.

Dans notre cas, Pytest compte cinq tests pour la fonction `test_requete_refusee`, car la liste `CAS_REFUSES` contient cinq cas distincts. Chaque jeu de paramètres génère une exécution indépendante du test. Cela permet de vérifier plusieurs situations invalides avec une seule fonction.

---

## 2. Ruff

### Sortie de `ruff check .` dans `tp/tp1`

```text
All checks passed!
```

### Sortie de `ruff check . --fix`

```text
Found 4 errors (4 fixed, 0 remaining).
```

### Sortie de `ruff format .`

```text
19 files left unchanged
```

### Sortie de `python -m pytest`

```text
================ 19 passed, 1 warning in 4.64s =================
```

**Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?**

`ruff check .` effectue une analyse statique du code Python. Il détecte notamment les erreurs de style, les problèmes d'importation et certaines mauvaises pratiques, sans exécuter le programme.

En revanche, `python -m pytest` exécute les tests automatisés afin de vérifier le comportement du programme et de s'assurer que les résultats obtenus correspondent aux résultats attendus.

Ainsi, Ruff vérifie la qualité du code, tandis que Pytest vérifie son fonctionnement.

---

## 3. Mise en place du TP2 (dans `tp/tp2`)

La sortie actuellement vérifiable correspond à l'état du projet après la mise en place de la sécurisation de l'API :

```text
======================== 18 passed, 1 warning in 3.76s ========================
```

Je n'ai pas conservé de sortie fiable du premier lancement, juste après la mise en place initiale du TP2. Je ne peux donc pas confirmer précisément quels tests échouaient à cette étape ni les codes HTTP obtenus.

Si les tests portant sur l'absence ou l'invalidité de la clé échouaient en recevant 200 au lieu de 401, cela pouvait s'expliquer par l'absence de la dépendance d'authentification sur le routeur.

---

## 4. La clé API (sprint 1)

### Fonction `require_api_key()` dans `maintai/api/security.py`

```python
def require_api_key(
    x_api_key: str | None = Header(default=None),
) -> None:
    """Vérifie la présence et la validité de la clé API du client."""
    expected_key = get_settings().api_key

    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur",
        )

    if x_api_key is None or not secrets.compare_digest(
        x_api_key, expected_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
```

### Configuration du routeur dans `maintai/api/main.py`

```python
router = APIRouter(
    prefix="/v1",
    dependencies=[Depends(require_api_key)],
)
```

**Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?**

Si les deux tests concernés sont ceux qui vérifient l'absence et l'invalidité de la clé, ils échouent parce que la fonction `require_api_key()` n'est pas encore associée au routeur.

En effet, écrire la fonction dans `security.py` ne suffit pas : il faut également l'ajouter comme dépendance du routeur avec `Depends(require_api_key)` pour qu'elle soit exécutée lors des requêtes.

### Dernière ligne de `python -m pytest` à la fin du sprint 1

```text
======================== 18 passed, 1 warning in 3.76s ========================
```

### Résultats des requêtes HTTP

Après avoir lancé :

```powershell
uvicorn maintai.api.main:app --reload --env-file .env
```

Les résultats obtenus sont les suivants :

| Requête | Code obtenu | Réponse (corps JSON) |
|---|---:|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability":0.9475,"alert":true,"threshold":0.3,"model_version":"2026-11-02T12:08:40Z"}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | Erreur de validation indiquant que la température doit être inférieure ou égale à 150. |

Pour le dernier cas, le détail de la réponse est :

```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "temperature_c"],
      "msg": "Input should be less than or equal to 150",
      "input": 500,
      "ctx": {"le": 150}
    }
  ]
}
```

**500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?**

Sans clé, la dépendance d'authentification rejette la requête avec le code 401 avant que la validation des données ne soit effectuée.

Avec une clé valide, la requête passe l'étape d'authentification et atteint la validation Pydantic. Celle-ci refuse la température de 500 °C, car la valeur maximale autorisée est de 150 °C. L'API retourne donc 422.

**Relancez Uvicorn sans `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?**

Le code obtenu est **500**, si la variable `MAINTAI_API_KEY` n'est pas définie dans l'environnement du serveur.

Dans ce cas, le serveur ne possède pas de clé de référence pour vérifier celle du client. Il retourne donc une erreur 500 avec le message « Clé API non configurée sur le serveur ».

Le code 401 concerne une clé client absente ou incorrecte lorsque le serveur possède bien une clé configurée.

---

## 5. La page web (sprint 2)

### Code `fetch` dans `web/index.html`

```javascript
document.getElementById("go").addEventListener("click", async () => {
  const button = document.getElementById("go");

  const reading = Object.fromEntries(
    FEATURES.map(f => [
      f,
      Number(document.getElementById(f).value)
    ])
  );

  const url = document.getElementById("url").value.trim().replace(/\/+$/, "");
  const key = document.getElementById("key").value.trim();

  if (!key) {
    show("err", "Veuillez saisir votre clé API.");
    return;
  }

  button.disabled = true;
  show("ok", "Prédiction en cours...");

  try {
    const response = await fetch(`${url}/v1/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": key
      },
      body: JSON.stringify(reading)
    });

    const data = await response.json();

    if (!response.ok) {
      show("err", `Erreur ${response.status} : ${JSON.stringify(data)}`);
      return;
    }

    show("ok", "Prédiction réussie :\n" +
      JSON.stringify(data, null, 2));

  } catch (error) {
    show("err", "Impossible de contacter l'API : " + error.message);
  } finally {
    button.disabled = false;
  }
});
```

### Résultats affichés par la page web

La page est servie sur `http://127.0.0.1:5501`.

| Essai | Résultat affiché |
|---|---|
| Relevé normal avec une bonne clé | Prédiction réussie : probabilité de défaillance de 0,9475 et alerte activée. |
| Température de 500 °C avec une bonne clé | Erreur 422 : température supérieure à la limite autorisée de 150 °C. |
| Relevé normal avec une fausse clé | Erreur 401 : clé API absente ou invalide. |

### Expérience CORS

**Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?**

L'interface servie depuis `http://127.0.0.1:5501` fonctionne, car cette origine est autorisée dans la configuration CORS.

En revanche, une origine non autorisée, comme `http://127.0.0.1:9999`, est rejetée par le serveur. Lorsque la page est exécutée depuis cette origine, le navigateur bloque la communication avec l'API et affiche une erreur CORS dans la console.

**Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?**

`curl.exe` n'applique pas la politique CORS. CORS est une protection imposée par les navigateurs aux scripts web. Le serveur peut donc répondre à une requête curl, alors que le navigateur peut empêcher une page web de lire la réponse si l'origine n'est pas autorisée.

---

## 6. Les tests de l'activité 1 dans le TP2

**Copiez `test_casser.py` dans `tp/tp2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?**

Quatre cas échouent avec le code **401 Unauthorized**, car ils appellent une route protégée de l'API (`/v1/predict`) sans fournir de clé API valide.

Le cinquième cas, qui utilise une mauvaise route (`/v1/inconnue`), obtient quand même le code **404 Not Found**. En effet, aucune route correspondante n'existe : la dépendance d'authentification du routeur n'est donc pas exécutée pour cette requête.

**Dernière ligne de `python -m pytest` avec `headers=HEADERS`**

Après avoir ajouté l'en-tête `X-API-Key` aux requêtes du fichier `test_casser.py`, les cinq scénarios ont été exécutés avec succès.

```text
collected 23 items

tests\test_api.py .......          [ 30%]
tests\test_casser.py .....         [ 52%]
tests\test_data.py ...             [ 65%]
tests\test_security.py .....       [ 86%]
tests\test_train.py ...            [100%]

23 passed, 1 warning in 2.65s
```

Les cinq tests de résistance sont donc validés : les quatre données invalides retournent le code 422 et la route inexistante retourne le code 404. Au total, les 23 tests du projet TP2 réussissent.

## 7. Questions de compréhension

### 1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?

- **401 Unauthorized :** l'authentification est absente ou invalide.
- **422 Unprocessable Entity :** la requête contient des données qui ne respectent pas les règles de validation.
- **403 Forbidden :** l'accès à la ressource ou à l'action est refusé, même si la requête est comprise et que l'autorisation nécessaire fait défaut.

### 2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?

La clé API est un secret qui ne doit pas être exposé publiquement.

Le fichier `.env` contient la configuration locale et la véritable clé API. Il doit être exclu du dépôt Git grâce au fichier `.gitignore`.

Le fichier `.env.example` contient un modèle des variables nécessaires, sans véritable secret. Il peut être ajouté au dépôt afin de montrer aux autres développeurs comment configurer le projet.

### 3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?

Une clé placée dans l'URL risque d'être enregistrée dans l'historique du navigateur, les journaux du serveur ou les liens partagés.

L'en-tête HTTP `X-API-Key` permet d'éviter ces expositions courantes. Cependant, l'utilisation de HTTPS reste indispensable pour protéger la clé pendant sa transmission.

### 4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?

`secrets.compare_digest` effectue une comparaison conçue pour limiter les différences de durée d'exécution selon les caractères comparés. Cela réduit les risques d'attaques par analyse temporelle (*timing attacks*).

### 5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?

Une origine est définie par trois éléments : le schéma (HTTP ou HTTPS), l'hôte et le port.

Les deux URL ne correspondent pas à la même origine, car leurs ports sont différents : 5500 et 8000.

---

## ## 8. Le rendu Git

- **Dépôt GitHub :** [classification-des-reclamations-clients](https://github.com/wiam1237/classification-des-reclamations-clients)
- **Dossier de rendu :** `tp/tp2`
- **Branche principale :** `main`
- **Branche de travail TP2 :** `tp2-maintai`
- **Intégration :** la branche `tp2-maintai` a été fusionnée directement dans `main`, puis publiée sur GitHub.
- **Pull Request :** aucune Pull Request n'a été créée, car la fusion a été réalisée directement en ligne de commande.
- **Tag `tp2` :** à vérifier sur GitHub.
- **Compte rendu :** rangé dans `tp/tp2/docs/compte rendu/COMPTE_RENDU_ERREYYADI_OUIAM.md`.
- **Fichiers sensibles :** le fichier `.env` et l'environnement virtuel `.venv` ne sont pas inclus dans le dépôt.
- **Dernier commit relatif à l'organisation du compte rendu :** `91df937` — « Organiser les comptes rendus ».
- **État Git final :** `working tree clean`, branche `main` synchronisée avec `origin/main`.

Le TP2 a donc été intégré à la branche principale et publié sur GitHub. Le compte rendu est également organisé dans le dossier prévu à cet effet.
---

## 9. Ce qui reste flou

La différence entre `localhost` et `127.0.0.1` est importante pour CORS.

Même sur le même ordinateur et avec le même port, ces deux hôtes constituent des origines différentes. Il faut donc autoriser dans la configuration CORS l'origine exacte utilisée pour ouvrir la page web.

Par exemple, `http://localhost:5501` et `http://127.0.0.1:5501` sont deux origines distinctes.