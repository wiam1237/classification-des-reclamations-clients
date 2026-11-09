# Compte rendu · TP4 : MaintAI devient un package Python
 ·  *Membres :* imane elouali ·  *Date :* 09/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes  (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :


========================== 2 failed, 25 passed, 1 warning in 5.26s ==========================


Quels sont les deux tests qui échouent, et pourquoi ?

Les deux échecs sont dans `tests/test_package.py`, car `maintai` n'est pas encore installé comme package dans le `.venv` :
- `test_installed_version_matches_the_code` échoue avec `importlib.metadata.PackageNotFoundError: No package metadata was found for maintai`. Le test demande à Python la version installée de `maintai`, et pip ne connaît pas encore ce package.
- `test_command_is_declared` échoue avec `AssertionError: assert 'maintai-predict' in ['pyproject-build', 'normalizer', 'fastapi', ...]`. Le test cherche la commande `maintai-predict` parmi les commandes (`console_scripts`) déclarées par les packages installés. Elle n'existe pas encore, puisque `[project.scripts]` n'est pas rempli et que rien n'est installé.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

toml
dependencies = [
    "numpy>=1.26",
    "pandas>=2.2",
    "scikit-learn>=1.5",
    "joblib>=1.4",
    "httpx>=0.27",
]

[project.scripts]
maintai-predict = "maintai.cli:main"


Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

`dependencies` ne contient que ce dont le code de `maintai/` a besoin pour fonctionner partout : `pandas`, `numpy` et `scikit-learn` (données et modèle), `joblib` (lecture et écriture du modèle), `httpx` (client de l'API). `pytest` est un outil de test, utile seulement aux développeurs : il est dans le groupe `dev`. `fastapi` et `uvicorn` ne servent que si on lance l'API : ils sont dans le groupe `api` (et `streamlit` dans `ui`). Ainsi, un collègue qui veut seulement la commande `maintai-predict` n'installe pas tout cela. Les groupes s'installent à la demande, par exemple `pip install -e ".[api,dev]"`.

Sortie de `pip show maintai` (les quatre premières lignes) :


Name: maintai
Version: 0.2.0
Summary: Prédiction de panne de machines à partir de relevés de capteurs.
Home-page: 


Dernière ligne de `python -m pytest` à la fin du sprint 1 :


=============================== 27 passed, 1 warning in 5.24s ===============================


Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

Depuis un autre dossier, la commande `maintai-predict 72 6 85 15000` affiche `Probabilité de panne : 95 % (ALERTE)` : elle fonctionne partout, tant que l'environnement est activé. La deuxième commande affiche le chemin du fichier `maintai\__init__.py` situé dans mon dossier de projet `C:\Users\alvarium\Downloads\TP4\maintai-starter-tp4\maintai\`, et non dans `site-packages`. La ligne `Editable project location: C:\Users\alvarium\Downloads\TP4\maintai-starter-tp4` de `pip show` l'annonce : l'installation éditable (`pip install -e .`) a posé dans le `.venv` un lien vers mon dossier. Python y trouve donc directement le code que j'écris.

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

Oui, le changement est visible immédiatement, sans réinstaller. L'installation éditable ne copie rien : elle pointe vers mon dossier, donc Python relit le fichier `cli.py` modifié à chaque lancement de la commande. C'est pratique pendant le développement. Il faut ensuite remettre le message d'origine, car `tests/test_cli.py` attend le texte « Probabilité de panne ».

## 3. Sprint 2 : construire et installer le wheel

Sortie de `ls dist` après `python -m build` :


maintai-0.2.0.tar.gz  maintai-0.2.0-py3-none-any.whl


Contenu du wheel. Le modèle, les tests et `ui/` y sont-ils ? Pourquoi ?

Dans Git Bash, `tar -tf` a échoué (`tar: This does not look like a tar archive`), car un wheel est un fichier zip et non une archive tar. J'ai donc utilisé `python -m zipfile -l`, qui lit les zip :


File Name                                             Modified             Size
maintai/_init_.py                            2026-11-09 09:32:04           95
maintai/cli.py                                 2026-11-09 09:32:04         1338
maintai/client.py                              2026-11-09 09:32:04         1498
maintai/config.py                              2026-11-09 09:32:04         1505
maintai/data.py                                2026-11-09 09:32:04          787
maintai/dataset.py                             2026-11-09 09:32:04         1327
maintai/predict.py                             2026-11-09 09:32:04         1188
maintai/train.py                               2026-11-09 09:32:04         3058
maintai/api/_init_.py                        2026-11-09 09:32:04            0
maintai/api/main.py                            2026-11-09 09:32:04         1915
maintai/api/schemas.py                         2026-11-09 09:32:04         1186
maintai/api/security.py                        2026-11-09 09:32:04          747
maintai-0.2.0.dist-info/METADATA
maintai-0.2.0.dist-info/WHEEL                  2026-11-09 11:49:28           91
maintai-0.2.0.dist-info/entry_points.txt       2026-11-09 11:49:28           53
maintai-0.2.0.dist-info/top_level.txt          2026-11-09 11:49:28            8
maintai-0.2.0.dist-info/RECORD                 2026-11-09 11:49:28         1290


Non, ni le modèle (`models/`), ni les tests, ni `ui/` ne sont dans le wheel. La section `[tool.setuptools.packages.find]` avec `include = ["maintai*"]` ne retient que le dossier `maintai/` : le wheel contient seulement le code Python du package et ses métadonnées (`dist-info`, dont `entry_points.txt` qui déclare la commande). Le modèle est un fichier de données produit par l'entraînement, ce n'est pas du code.

Dans un environnement neuf (`~/essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | `Modèle introuvable : C:\Users\alvarium\essai\Lib\site-packages\models\model.joblib`, puis `Entraînez-le (python -m maintai.train) ou indiquez son dossier dans MAINTAI_MODELS_DIR.` |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | Trois `InconsistentVersionWarning` (StandardScaler, LogisticRegression, Pipeline : modèle écrit avec la version 1.8.0, lu avec la version 1.9.1), puis `Probabilité de panne : 95 % (ALERTE)` |
| après `pip install scikit-learn==1.8.0` | `Probabilité de panne : 95 % (ALERTE)`, sans avertissement |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

Le modèle a été entraîné et sauvegardé avec scikit-learn 1.8.0, la version imposée par `requirements.txt` dans l'environnement du TP4. Dans l'environnement neuf, l'installation du wheel a pris la dernière version autorisée par `scikit-learn>=1.5`, soit la 1.9.1. Relire un modèle avec une autre version que celle qui l'a écrit peut donner des résultats faux ou casser le code : scikit-learn prévient donc. La ligne de `models/model_info.json` qui l'explique est :


"sklearn_version": "1.8.0"
```

C'est la version utilisée à l'entraînement. En installant exactement cette version (pip install scikit-learn==1.8.0, qui a désinstallé la 1.9.1), l'avertissement disparaît.

## 4. Questions de compréhension

1. Quelle différence entre requirements.txt et la liste dependencies de pyproject.toml ?
   requirements.txt fixe des versions *exactes* (==) : c'est la recette pour reproduire exactement l'environnement, indispensable pour relire un modèle avec la version qui l'a écrit. dependencies donne des versions *minimales* (>=) : c'est ce qu'un package déclare pour pouvoir s'installer à côté d'autres packages sans conflit. L'un décrit un environnement précis, l'autre ce dont le code a besoin.
2. Quelle différence entre pip install -e . et pip install dist\maintai-0.2.0-py3-none-any.whl ?
   pip install -e . (éditable) pose un lien vers mon dossier de projet : mes modifications sont visibles tout de suite, c'est pour développer. Le wheel est un fichier (un zip) fabriqué par python -m build : l'installer fait une *copie* du code dans site-packages, figée à la version construite. Modifier le dossier du projet ne change plus rien ; il faut reconstruire et réinstaller. C'est ce qu'on livre à un collègue.
3. Qu'est-ce qu'un « point d'entrée » ([project.scripts]) ? Où pip crée-t-il le fichier maintai-predict.exe ?
   Un point d'entrée est la déclaration d'une commande du terminal, sous la forme nom-de-la-commande = "module:fonction" : ici maintai-predict = "maintai.cli:main", qui appelle la fonction main du fichier maintai/cli.py. À l'installation, pip crée un petit programme maintai-predict.exe dans le dossier Scripts du .venv, qui lance cette fonction. C'est pour cela que la commande n'est reconnue que si l'environnement est activé, et qu'il faut refaire pip install -e . si on la déclare après l'installation.

## 5. Le rendu Git

- Lien de la pull request : https://github.com/wiam1237/classification-des-reclamations-clients
- Le tag tp4 existe sur GitHub : oui / non 
- git status avant le commit : dist/, build/ ou maintai.egg-info/ apparaissaient-ils ? non (le .gitignore du starter les exclut ; le wheel se reconstruit, il ne va pas dans Git)

## 6. Ce qui reste flou

Je dois encore m'entraîner à écrire un pyproject.toml seul, en particulier à retrouver quelles bibliothèques vont dans dependencies et à bien fermer les guillemets : une erreur de syntaxe donne un TOMLDecodeError avec le numéro de ligne. J'ai aussi compris pourquoi livrer un modèle demande trois choses : le code (le wheel), le modèle (models/) et les versions exactes