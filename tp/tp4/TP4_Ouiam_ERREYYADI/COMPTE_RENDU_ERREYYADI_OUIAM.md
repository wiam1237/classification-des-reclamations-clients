# Compte rendu · TP4 : MaintAI devient un package Python

·  **Membres :**ERREYYADI Ouiam ·  **Date :** 09-11-2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
(collez ici)
```

Quels sont les deux tests qui échouent, et pourquoi ?

…

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

```toml
(collez ici)
```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

…

Sortie de `pip show maintai` (les quatre premières lignes) :

```
(collez ici)
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
(collez ici)
```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

…

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

…

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
(collez ici)
```

Contenu du wheel (`tar -tf dist\maintai-0.2.0-py3-none-any.whl`). Le modèle, les tests et `ui/` y sont-ils ? Pourquoi ?

```
(collez ici)
```

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | |
| après `pip install scikit-learn==1.8.0` | |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

…

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?
   …
2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?
   …
3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?
   …

## 5. Le rendu Git

- Lien de la pull request : …
- Le tag `tp4` existe sur GitHub : oui / non
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? oui / non

## 6. Ce qui reste flou

…
\# Compte rendu · TP4 : MaintAI devient un package Python

\*\*Groupe :\*\* …  ·  \*\*Membres :\*\* Ouiam ERREYYADI  ·  \*\*Date :\*\* 09/11/2026

\> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.\
\> Collez les sorties du terminal entre les lignes \`\`\` (trois accents graves).

\---

\## 1. Mise en place (dans \`TP/TP4\`, avec son propre \`.venv\`)

Dernière ligne de \`python -m pytest\` juste après \`pip install -r requirements.txt\` :

\`\`\`\
2 failed, 25 passed\
\`\`\`

Quels sont les deux tests qui échouent, et pourquoi ?

Les deux tests en échec sont liés à l'installation du package. L'installation des dépendances avec `pip install -r requirements.txt` ne suffit pas à installer le package `maintai` lui-même. Cette situation est corrigée par l'installation éditable avec `pip install -e .`.

\## 2. Sprint 1 : \`pyproject.toml\` et \`pip install -e .\`

Vos sections \`dependencies\` et \`[project.scripts]\` :

\`\`\`toml\
dependencies = [\
"numpy>=2.4",\
"pandas>=3.0",\
"scikit-learn>=1.8",\
"joblib>=1.5",\
"httpx>=0.28",\
]

[project.scripts]\
maintai-predict = "maintai.cli:main"\
\`\`\`

Pourquoi \`pytest\` et \`fastapi\` ne sont-ils pas dans \`dependencies\` ?

`pytest` est utilisé uniquement pour exécuter les tests. Il constitue donc une dépendance de développement et non une dépendance nécessaire à l'utilisation normale du package.

`fastapi` est utilisé pour développer l'API, mais il n'est pas nécessaire à l'exécution de la fonctionnalité principale de prédiction du package.

Sortie de \`pip show maintai\` (les quatre premières lignes) :

\`\`\`\
Name: maintai\
Version: 0.2.0\
Summary: Prédiction de pannes à partir de relevés de capteurs\
Home-page:\
\`\`\`

Dernière ligne de \`python -m pytest\` à la fin du sprint 1 :

\`\`\`\
\================= 27 passed, 1 warning in 6.63s =================\
\`\`\`

Placez-vous dans un autre dossier (\`cd %TEMP%\`) et lancez \`maintai-predict 72 6 85 15000\`, puis \`python -c "import maintai; print(maintai.\_\_file\_\_)"\`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de \`maintai\` ?

La commande `maintai-predict 72 6 85 15000` affiche :

\`\`\`\
Probabilité de panne : 95 % (ALERTE)\
\`\`\`

La commande `python -c "import maintai; print(maintai.__file__)"` affiche le chemin du fichier `__init__.py` du package. Grâce à l'installation éditable (`pip install -e .`), Python trouve le code directement dans le dossier source du projet, dans le répertoire `maintai`.

Modifiez le message affiché par \`maintai/cli.py\`, puis relancez \`maintai-predict\` sans réinstaller. Le changement est-il visible ? Pourquoi ?

Oui, le changement est visible sans réinstallation. L'installation éditable relie le package installé au dossier source du projet. Les modifications de `maintai/cli.py` sont donc directement prises en compte à la prochaine exécution de la commande.

\## 3. Sprint 2 : construire et installer le wheel

Sortie de \`dir dist\` après \`python -m build\` :

\`\`\`\
maintai-0.2.0.tar.gz\
maintai-0.2.0-py3-none-any.whl\
\`\`\`

Contenu du wheel (\`tar -tf dist\maintai-0.2.0-py3-none-any.whl\`). Le modèle, les tests et \`ui/\` y sont-ils ? Pourquoi ?

\`\`\`\
maintai/\
maintai-0.2.0.dist-info/\
\`\`\`

Le wheel contient le package Python `maintai` et ses métadonnées d'installation. Le modèle entraîné, les tests et le dossier `ui/` ne sont pas inclus, car ils ne sont pas déclarés dans la configuration actuelle comme fichiers à distribuer dans le wheel. Le modèle doit donc être fourni séparément et son chemin indiqué à l'aide de la variable d'environnement `MAINTAI_MODELS_DIR`.

Dans un environnement neuf (\`%TEMP%\essai\`), installez le wheel et lancez \`maintai-predict\` :

| Étape                                       | Ce qui s'affiche                                                                                        |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| sans `MAINTAI_MODELS_DIR`                   | `Modèle introuvable : C:\Users\pc\AppData\Local\Temp\essai\.venv\Lib\site-packages\models\model.joblib` |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | `Probabilité de panne : 95 % (ALERTE)`                                                                  |
| après `pip install scikit-learn==1.8.0`     | `Probabilité de panne : 95 % (ALERTE)`                                                                  |

D'où vient l'avertissement \`InconsistentVersionWarning\` ? Quelle ligne de \`models/model_info.json\` permet de le comprendre ?

L'avertissement `InconsistentVersionWarning` provient d'une différence entre la version de scikit-learn utilisée lors de l'entraînement du modèle et celle installée dans le nouvel environnement virtuel. Le modèle a été entraîné avec la version `1.8.0`. La ligne suivante dans `models/model_info.json` permet de le vérifier :

\`\`\`json\
"sklearn_version": "1.8.0"\
\`\`\`

Après l'installation de la version correspondante avec `pip install scikit-learn==1.8.0`, l'avertissement lié à cette différence de version disparaît.

\## 4. Questions de compréhension

1\. Quelle différence entre \`requirements.txt\` et la liste \`dependencies\` de \`pyproject.toml\` ?

Le fichier `requirements.txt` permet de définir les bibliothèques à installer pour préparer l'environnement de travail du projet. Il peut notamment contenir les dépendances nécessaires aux tests et au développement.

La liste `dependencies` de `pyproject.toml` déclare les dépendances indispensables au fonctionnement du package installé. Ces dépendances sont automatiquement prises en compte par `pip` lors de l'installation.

2\. Quelle différence entre \`pip install -e .\` et \`pip install dist\maintai-0.2.0-py3-none-any.whl\` ?

La commande `pip install -e .` effectue une installation éditable. Le package reste lié au dossier source du projet et les modifications du code sont prises en compte sans réinstallation.

La commande `pip install dist\maintai-0.2.0-py3-none-any.whl` installe le package à partir du fichier wheel construit. Il s'agit d'une installation classique d'une distribution du package.

3\. Qu'est-ce qu'un « point d'entrée » (\`[project.scripts]\`) ? Où pip crée-t-il le fichier \`maintai-predict.exe\` ?

Un point d'entrée permet de créer une commande exécutable qui appelle une fonction Python du package. Dans notre projet, `maintai-predict = "maintai.cli:main"` indique que la commande `maintai-predict` exécute la fonction `main` du module `maintai.cli`.

Sous Windows, `pip` crée le fichier `maintai-predict.exe` dans le dossier `Scripts` de l'environnement Python utilisé, par exemple `.venv\Scripts\maintai-predict.exe`.

\## 5. Le rendu Git

- Lien de la pull request : [https://github.com/wiam1237/classification-des-reclamations-clients/tree/main/tp/tp4](https://github.com/wiam1237/classification-des-reclamations-clients/tree/main/tp/tp4?utm_source=chatgpt.com)
- Le tag `tp4` existe sur GitHub : à vérifier.
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? à vérifier.

\## 6. Ce qui reste flou

Les principales difficultés rencontrées concernent la différence entre l'installation éditable et l'installation à partir d'un fichier wheel, ainsi que la gestion du modèle entraîné dans un environnement différent.

Ce TP a également permis de comprendre l'importance de la compatibilité des versions des bibliothèques, notamment scikit-learn, lors de l'entraînement et du chargement d'un modèle.

Enfin, la distinction entre les dépendances nécessaires au fonctionnement du package et celles utilisées uniquement pour le développement et les tests mérite d'être approfondie.