# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** G2  ·  **Membres :** wiam RAOUB ·  **Date :** 09/11/2026

> Les valeurs techniques ci-dessous correspondent au projet. Les informations personnelles et les étapes GitHub restent à compléter.

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
Résultat attendu avant l'installation du package : 2 failed, 25 passed.
```

Quels sont les deux tests qui échouent, et pourquoi ?

`test_installed_version_matches_the_code` et `test_command_is_declared` échouent tant que le projet n'est pas installé comme package. Le premier cherche les métadonnées de distribution `maintai`; le second cherche le point d'entrée `maintai-predict`. `pip install -e .` crée ces métadonnées et déclare la commande.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Sections `dependencies` et `[project.scripts]` :

```toml
dependencies = [
    "numpy>=2.4",
    "pandas>=3.0",
    "scikit-learn>=1.8",
    "joblib>=1.5",
    "httpx>=0.28",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

`pytest` sert uniquement aux tests et est dans le groupe optionnel `dev`. FastAPI sert à l'API, qui est une fonctionnalité optionnelle déclarée dans le groupe `api`. Les mettre dans `dependencies` installerait ces outils même pour les personnes qui utilisent seulement la prédiction en ligne de commande. Ils peuvent être installés avec `pip install -e ".[dev,api]"` si nécessaire.

Sortie de `pip show maintai` (quatre premières lignes observées dans l'environnement d'essai) :

```
Name: maintai
Version: 0.2.0
Summary: Prédiction de pannes à partir de relevés de capteurs
Home-page:
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
27 passed, 1 warning in 3.31s
```

L'avertissement observé est une dépréciation de `starlette.testclient` concernant l'utilisation de `httpx`; les tests passent.

Placez-vous dans un autre dossier et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces commandes ? Où Python trouve-t-il le code ?

Avec `pip install -e .`, la commande CLI affiche `Probabilité de panne : 95 % (ALERTE)` si le modèle du projet est disponible. L'import `maintai` pointe vers le dossier source `maintai/` du projet : l'installation éditable référence le code de travail, elle n'en installe pas une copie indépendante.

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

Oui. En mode éditable, le point d'entrée lance la fonction du module source. La modification du fichier est donc visible sans réinstallation (un redémarrage de la commande suffit).

## 3. Sprint 2 : construire et installer le wheel

Après `python -m build`, le wheel construit est :

```
dist/maintai-0.2.0-py3-none-any.whl
```

Sur macOS, `ls -l dist` remplace la commande Windows `dir dist`.

Contenu du wheel (`unzip -l dist/maintai-0.2.0-py3-none-any.whl`) :

```
maintai/__init__.py
maintai/cli.py
maintai/client.py
maintai/config.py
maintai/data.py
maintai/dataset.py
maintai/predict.py
maintai/train.py
maintai/api/__init__.py
maintai/api/main.py
maintai/api/schemas.py
maintai/api/security.py
maintai-0.2.0.dist-info/METADATA
maintai-0.2.0.dist-info/WHEEL
maintai-0.2.0.dist-info/entry_points.txt
maintai-0.2.0.dist-info/top_level.txt
maintai-0.2.0.dist-info/RECORD
```

Le wheel ne contient ni le modèle, ni les tests, ni `ui/`. La configuration setuptools n'inclut que les packages `maintai*`; les fichiers du modèle et les dossiers `tests/` et `ui/` ne font pas partie de ce package Python.

Dans un environnement neuf, résultats du test de la commande :

| Étape | Ce qui s'affiche |
|---|---|
| Sans `MAINTAI_MODELS_DIR` | `Modèle introuvable : /private/tmp/maintai-essai/lib/python3.13/site-packages/models/model.joblib`, puis le conseil d'entraîner le modèle ou de définir `MAINTAI_MODELS_DIR`. |
| Avec `MAINTAI_MODELS_DIR="/Users/wiam/Downloads/maintai-starter-tp4/models"` | `Probabilité de panne : 95 % (ALERTE)` |
| Après `pip install scikit-learn==1.8.0` | Pip indique `Requirement already satisfied: scikit-learn==1.8.0` dans l'environnement `maintai-essai`. La commande relancée affiche `Probabilité de panne : 95 % (ALERTE)`. |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

Il peut apparaître lorsque la version de scikit-learn qui charge le modèle sérialisé par joblib diffère de celle qui a servi à l'entraîner. La ligne concernée dans `models/model_info.json` est `"sklearn_version": "1.8.0"`. Dans l'essai réalisé, scikit-learn 1.8.0 était déjà installé (`Requirement already satisfied`) et aucune alerte d'incompatibilité n'a été affichée.

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?

   `requirements.txt` est une liste d'installation pratique pour recréer l'environnement du projet, ici avec des versions exactes. `dependencies` déclare les dépendances nécessaires au fonctionnement du package installé et leurs versions minimales. Les dépendances de développement et les fonctionnalités optionnelles sont séparées dans les groupes optionnels de `pyproject.toml`.

2. Quelle différence entre `pip install -e .` et `pip install dist/maintai-0.2.0-py3-none-any.whl` ?

   `pip install -e .` installe le projet en mode éditable : le package installé référence le code source du dossier de travail. L'installation du wheel installe une distribution construite et indépendante du dossier source. Le wheel distribué ici ne contient pas le modèle.

3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il la commande ?

   C'est une déclaration qui associe une commande shell à une fonction Python, ici `maintai-predict` à `maintai.cli:main`. Pip crée le lanceur dans le dossier `bin/` de l'environnement Unix/macOS (par exemple `venv/bin/maintai-predict`) ou `Scripts/` sous Windows (par exemple `venv\\Scripts\\maintai-predict.exe`).

## 5. Le rendu Git

- Lien de la pull request : aucune pour TP4. Le dossier `tp/tp4` a été poussé directement sur `main` dans [classification-des-reclamations-clients](https://github.com/wiam1237/classification-des-reclamations-clients/commit/3d42f0e8ab52f753ff911c98bd22c97d3966ae8e).
- Le tag `tp4` existe sur GitHub : oui. Le tag annoté `tp4` (`Rendu TP4`) pointe vers le commit `3d42f0e` sur `main`.
- `git status` avant le commit : dans le dépôt `classification-des-reclamations-clients`, `## main...origin/main` puis `?? tp/tp4/` (fichier marqueur non suivi). Les dossiers `dist/`, `build/` et `*.egg-info/` sont ignorés par le `.gitignore` du projet MaintAI.

## 6. Ce qui reste flou

Aucune question restante signalée. Le wheel installé dans l'environnement `maintai-essai` fonctionne avec le modèle externe défini par `MAINTAI_MODELS_DIR`; la prédiction testée affiche `Probabilité de panne : 95 % (ALERTE)`. Le dossier `tp/tp4` et le tag `tp4` sont présents sur GitHub.
