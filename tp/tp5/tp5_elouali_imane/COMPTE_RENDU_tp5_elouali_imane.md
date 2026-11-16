# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :2 ·  **Membres :ELOUALI IMANE  ·  **Date :** 16/11/2026 12:15

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :


================== 5 failed, 27 passed, 2 warnings in 35.88s ==================


Quels tests échouent, et pourquoi ?

Les 5 tests de `tests/test_tracking.py` échouent (`test_training_creates_a_run`, `test_run_records_metrics`, `test_run_records_data_version`, `test_run_stores_the_model`, `test_options_change_the_run`). La fonction `log_run` n'est pas encore écrite : elle renvoie `""` et n'enregistre rien dans MLflow. Les tests trouvent donc 0 run (« aucun run MLflow : log_run n'a rien enregistré »), et l'entraînement affiche « Run MLflow : » sans identifiant.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

J'avais créé un environnement virtuel neuf pour TP5 : avant `pip install -e .`, `maintai` n'y était pas installé. Dans le cas d'un environnement partagé avec le TP4, il aurait pointé vers le dossier du TP4. Après `pip install -e .`, le package est installé en mode éditable et pointe vers le dossier `TP5` : les modifications du code (comme `tracking.py`) sont prises en compte immédiatement, et `python -m maintai.train` utilise bien le code de TP5

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

"""Suivi des entraînements avec MLflow : chaque entraînement devient un « run » qu'on peut comparer.

Les runs sont enregistrés dans mlflow.db (dossier courant) ; on les regarde avec : mlflow ui
"""
import hashlib
import os
from pathlib import Path

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")  # coupe un message d'information de MLflow

import mlflow
import mlflow.sklearn

EXPERIMENT = "maintai"
TRUSTED_TYPES = ["sklearn.tree._tree.Tree"]  # nécessaire pour --model forest


def file_md5(path: Path) -> str:
    """Empreinte du fichier de données : la même que celle que DVC écrit dans le fichier .dvc."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement : paramètres, version des données, métriques et modèle. Renvoie l'id du run."""
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("data_md5", file_md5(data_path))
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES,
        )
    return run.info.run_id(.venv) 

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
====================================== 32 passed, 4 warnings in 35.00s =======================================
```

Vos runs (cinq), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.750 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| `python -m maintai.train --threshold 0.1` (votre essai) | 0.919 | 0.434 | 0.826 |

Identifiants des runs : `bf47c8483f434e6ea59e9d00fd269d30`, `1033eb41138646a497bafd85a38cf489`, `5c6a34a80e1646948cd8d674f07af837`, `19140944ac2f467cbd6acabafe133153`, `21f5600f5c3642b484b1a3684fe47630` (dans l'ordre du tableau). Baseline (toujours « pas de panne ») : accuracy 0.864, recall 0.

 l'association run ↔ commande vient de l'ordre des exécutions. Contrôlez les colonnes `C` et `model` dans `mlflow ui`, surtout pour `--C 0.01` et `--model forest`.

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Je choisirais la régression logistique avec **seuil 0.2** (run `5c6a34a8...`) : recall 0.838, precision 0.543. Une panne manquée coûte plus cher qu'une fausse alerte, donc le recall prime : ce seuil attrape environ 84 % des pannes, et un peu plus d'une alerte sur deux correspond à une vraie panne. Le seuil 0.1 a un meilleur recall (0.919) mais une précision de 0.434 et une accuracy (0.826) inférieure à celle du baseline (0.864) : trop de fausses alertes. Les runs à seuil 0.3 ratent une panne sur quatre ou plus. La forêt aléatoire n'est pas meilleure : à seuil égal (0.3), son recall (0.728) est inférieur à celui de la régression logistique (0.750), avec une précision plus faible.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

`scikit-learn==1.8.0`. MLflow enregistre avec le modèle les versions exactes des bibliothèques qui l'ont produit. Cela règle le problème du TP4 : un modèle sauvegardé avec une version de scikit-learn peut mal se charger, ou donner d'autres résultats, sur une machine qui en a une autre. Avec le `requirements.txt` du modèle, on sait quelles versions réinstaller.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

Dans `mlflow.db` (base SQLite : paramètres, métriques, tags) et dans le dossier `mlruns/` (modèles et artefacts), à la racine de `TP5/TP5`. Ils ne vont pas dans Git : le `.gitignore` les exclut. Ce sont des fichiers générés, potentiellement lourds, propres à chaque machine ; chacun peut les reproduire en relançant les entraînements.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` (version v1) :

```
outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

Elles sont identiques : `73e0b7cb3c6f795c70c3ddf970b99c15` pour le `md5` du `.dvc` et pour le `data_md5` des runs entraînés sur la v1. C'est ce qui relie un run à ses données : `file_md5()` de `tracking.py` calcule la même empreinte que DVC. À partir d'un run, on retrouve donc la version exacte des données. (Le run entraîné sur la v2 a, lui, `data_md5` = `93fdeef2cac1893c4f720c16457eea75`, comme le `.dvc` de la v2.)

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Git gère mal les gros fichiers de données et garde chaque version pour toujours dans l'historique. Le fichier `.dvc` est un « reçu » de quelques lignes (md5 et taille) : léger, il suit le code dans Git. DVC garde le fichier lui-même dans un cache et un stockage, et le restitue à partir du reçu. Git refuse d'ailleurs `git add data/sensors.csv` (le `.gitignore` l'exclut).

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:
        changed outs:
                modified:           data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | `c8b43ee` | `73e0b7cb` | 5000 |
| v2 | `42c6ea2` | `93fdeef2` | 8000 |

(Les nombres de lignes viennent des messages « 5000 relevés écrits » et « 8000 relevés écrits ».avec `python -c "import pandas as pd; print(len(pd.read_csv('data/sensors.csv')))"` après chaque `dvc checkout`.)

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

**À COMPLÉTER** avec ce que vous avez observé : la v1 doit contenir 5000 lignes et la v2 8000. Dans mon cas, j'ai d'abord vidé le cache (`.dvc/cache`) et fait `dvc pull` (qui n'a récupéré que la v2). Le `dvc checkout` vers la v1 a alors échoué (« Checkout failed ... Is your cache up to date? ») car la v1 n'était plus dans le cache. Après `git checkout c8b43ee -- data/sensors.csv.dvc` suivi de `dvc pull`, la v1 est revenue depuis le stockage ; puis `git checkout HEAD -- data/sensors.csv.dvc` et `dvc checkout` ramènent la v2. Réécrivez ce passage selon l'ordre réel de vos commandes et indiquez les comptes de lignes obtenus.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

`dvc pull` lit le reçu `.dvc`, ne trouve le fichier ni dans le dossier ni dans le cache, le récupère dans le stockage (`~/dvc-stockage`) et le remet dans `data/` : `1 file fetched and 1 file added`, avec `A data\sensors.csv`. C'est ce qui permet à un coéquipier qui n'a pas les données de les retrouver à l'identique. Attention : `dvc pull` ne récupère que les versions demandées par le reçu en vigueur ; pour une autre version, il faut d'abord changer le reçu avec Git, puis relancer `dvc pull`.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages (régression logistique, C = 1.0, seuil 0.3) :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 (`bf47c848...`) | `73e0b7cb` | 4000 | 0.750 | 0.622 |
| v2 (`9ec60dda...`) | `93fdeef2` | 6400 | 0.741 | 0.650 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non. Le recall de la v2 (0.741) est légèrement inférieur à celui de la v1 (0.750), et la précision légèrement supérieure (0.650 contre 0.622) : aucune amélioration nette. Surtout, les deux runs ne sont pas comparables directement : les données d'entraînement diffèrent (4000 contre 6400 relevés) et le jeu de test aussi (1000 contre 1600 relevés, avec un taux de panne de 13.6 % contre 12.8 %). Un écart de quelques points de recall correspond à quelques pannes seulement : c'est du bruit. Pour comparer proprement, il faudrait un même jeu de test, ou répéter l'expérience avec plusieurs tirages.

## 5. Décision : l'ADR 004

Modèle et seuil retenus : régression logistique, seuil **0.2**.
Identifiant du run : `5c6a34a80e1646948cd8d674f07af837`.
`data_md5` des données utilisées : `73e0b7cb3c6f795c70c3ddf970b99c15` (v1).
Contrainte : une panne manquée coûte plus cher qu'une fausse alerte, donc le recall prime (0.838).
Contrepartie acceptée : plus de fausses alertes (precision 0.543) et une accuracy plus basse (0.882, contre 0.904 au seuil 0.3).
Le détail est dans `docs/adr/004-choix-du-modele.md`

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   Git versionne le code (et le reçu `.dvc` de 4 lignes par fichier de données). DVC versionne les fichiers de données eux-mêmes, dans un cache et un stockage, à partir de ce reçu. MLflow garde la trace de chaque entraînement : paramètres, `data_md5`, métriques et modèle avec les versions exactes des bibliothèques.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   Le chemin d'un dossier de mon PC (`C:\Users\...\dvc-stockage`) ne doit pas aller dans Git : `--local` l'écrit dans `.dvc/config.local`, qui est ignoré par Git. Pour que le groupe partage les données, il faudrait un stockage accessible à tous (S3, Google Drive, serveur SSH, etc.) déclaré pour le projet, puis que chacun fasse `dvc pull`.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   Le code : dans Git (et le wheel du TP4). Les données : dans DVC (le reçu dans Git, le fichier dans le stockage). Le modèle : dans MLflow (un run, son identifiant), avec les versions exactes des bibliothèques dans le `requirements.txt` du modèle.

## 7. Le rendu Git

- Lien de la pull request : https://github.com/wiam1237/classification-des-reclamations-clients
- Le tag `tp5` existe sur GitHub :oui
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? non, le `.gitignore` les exclut

## 8. Ce qui reste flou

la différence entre `dvc fetch`, `dvc checkout` et `dvc pull`.