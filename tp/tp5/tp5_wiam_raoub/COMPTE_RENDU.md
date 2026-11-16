# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :2  ·  **Membres :** AMIRA RMAILI
·  **Date :** 16/11/2026    heure 12:15

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
================== 5 failed, 27 passed, 2 warnings in 35.88s ==================
```

Quels tests échouent, et pourquoi ?

Les 5 tests de `tests/test_tracking.py` échouent (`test_training_creates_a_run`, `test_run_records_metrics`, `test_run_records_data_version`, `test_run_stores_the_model`, `test_options_change_the_run`). La fonction `log_run` n'est pas encore écrite : elle renvoie `""` et n'enregistre rien dans MLflow. Les tests trouvent donc 0 run (« aucun run MLflow : log_run n'a rien enregistré »), et l'entraînement affiche « Run MLflow : » sans identifiant.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

J'avais créé un environnement virtuel neuf pour TP5 : avant `pip install -e .`, `maintai` n'y était pas installé. Dans le cas d'un environnement partagé avec le TP4, il aurait pointé vers le dossier du TP4. Après `pip install -e .`, le package est installé en mode éditable et pointe vers le dossier `TP5` : les modifications du code (comme `tracking.py`) sont prises en compte immédiatement, et `python -m maintai.train` utilise bien le code de TP5.

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
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
    return run.info.run_id
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
======================= 32 passed, 6 warnings in 31.73s =======================
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.750 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| (votre essai) `python -m maintai.train` sur la v2 des données (8000 relevés) | 0.741 | 0.650 | 0.916 |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Le run `--threshold 0.2` (identifiant `f1b4792b253b4ded9c759d34a2a9dbea`). Il a le meilleur recall (0.838 contre 0.750 pour le run de base), donc il manque le moins de pannes. Nous acceptons en échange une precision plus basse (0.543) : plus de fausses alertes. La forêt aléatoire n'est pas meilleure : elle est en dessous de la régression logistique de base sur les trois métriques (recall 0.728, precision 0.562, accuracy 0.886). Ici, le seuil a plus d'effet que le choix du modèle.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

Le `requirements.txt` du modèle indique `scikit-learn==1.8.0` (avec aussi `mlflow==3.18.0`, `numpy==2.4.4`, `pandas==3.0.2`, `skops==0.16.0`). Au TP4, le modèle était sauvegardé en `.joblib` sans aucune trace des versions des bibliothèques. Le recharger avec une autre version de scikit-learn pouvait échouer ou donner des résultats différents, sans qu'on sache pourquoi. Maintenant, chaque run garde les versions exactes, ce qui permet de recréer le même environnement.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

MLflow enregistre les paramètres et les métriques dans la base SQLite `mlflow.db`, et les modèles dans le dossier `mlruns/`, tous deux dans le dossier `TP5` (dossier courant). Ils ne vont pas dans Git : le `.gitignore` les exclut. Ce sont des fichiers locaux, binaires et volumineux, régénérables, qui changent à chaque entraînement, et qui contiennent des chemins propres à mon PC.

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

Les deux valeurs sont identiques : `73e0b7cb3c6f795c70c3ddf970b99c15` pour les 4 runs entraînés sur la v1 (de même, le run sur la v2 porte `93fdeef2...`, le md5 du `.dvc` de la v2). `file_md5()` calcule la même empreinte que DVC. À partir d'un run MLflow, on retrouve donc exactement la version des données : on cherche le commit Git qui contient ce reçu, puis `dvc checkout` ou `dvc pull` ramène le fichier.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Un fichier de données peut peser très lourd, et Git le gère mal : il garde chaque version pour toujours. Git ne garde donc qu'un reçu de quelques lignes (le md5 et la taille). Le fichier lui-même vit dans le cache et le stockage de DVC.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:
        changed outs:
                modified:           data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | `1491c38` (Données v1) | `73e0b7cb` | 5000 |
| v2 | `9d749c6` (Données v2) | `93fdeef2` | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après `git checkout 1491c38 -- data/sensors.csv.dvc` et `dvc checkout`, `data/sensors.csv` contient 5000 lignes. Git a restauré l'ancien reçu et DVC a ramené le fichier qui lui correspond. Après `git checkout HEAD -- data/sensors.csv.dvc` et `dvc checkout`, on retrouve 8000 lignes (v2).

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

`dvc pull` récupère le fichier depuis le stockage (`1 file fetched and 1 file added`) et recrée `data/sensors.csv` avec ses 8000 lignes. C'est la situation d'un coéquipier qui clone le dépôt : il a le reçu `.dvc` dans Git, et `dvc pull` lui donne les données.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | `73e0b7cb` | 4000 | 0.750 | 0.622 |
| v2 | `93fdeef2` | 6400 | 0.741 | 0.650 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non. Le recall est un peu plus bas sur la v2 (0.741 contre 0.750), la precision et l'accuracy sont un peu plus hautes (0.650 contre 0.622, 0.916 contre 0.904), mais ces écarts sont petits. Surtout, les deux modèles sont évalués sur des jeux de test différents (1000 relevés pour la v1, 1600 pour la v2, tirés de données différentes). Les scores ne mesurent donc pas la même chose et ne sont pas strictement comparables. Pour comparer proprement, il faudrait évaluer les deux modèles sur le même jeu de test. La traçabilité (`data_md5`) permet de savoir sur quelles données chaque résultat a été obtenu.

## 5. Décision : l'ADR 004

Voir `docs/adr/004-choix-du-modele.md`. Modèle retenu : régression logistique (C=1) avec un seuil de 0.2. Run MLflow : `f1b4792b253b4ded9c759d34a2a9dbea`. Données : v1, `data_md5` = `73e0b7cb3c6f795c70c3ddf970b99c15`.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   Git versionne le code, et un reçu de 4 lignes (`.dvc`) par fichier de données. DVC versionne les fichiers de données eux-mêmes, dans un cache et un stockage hors de Git. MLflow garde chaque entraînement : paramètres, `data_md5`, métriques, et le modèle avec les versions exactes des bibliothèques.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   Le stockage est un dossier de mon PC (`%USERPROFILE%\dvc-stockage`). Avec `--local`, son chemin est écrit dans `.dvc/config.local`, ignoré par Git, car ce chemin n'a de sens que sur mon ordinateur. Pour partager les données, il faudrait un stockage distant accessible à tout le groupe (S3, Google Drive, serveur SSH ou dossier réseau), déclaré dans `.dvc/config` (versionné) : chacun ferait alors `dvc pull`.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   Le code est dans Git (et dans le wheel du TP4). Les données sont dans DVC : le reçu dans Git, le fichier dans le stockage. Le modèle est dans MLflow : un run avec son identifiant, et son `requirements.txt` pour les versions exactes.

## 7. Le rendu Git

- Lien de la pull request : https://github.com/wiam1237/classification-des-reclamations-clients/tree/main/tp/tp5/tp5_wiam_raoub
- Le tag `tp5` existe sur GitHub : oui 
-  `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? non (le `.gitignore` les exclut ; `git status` indiquait « working tree clean »)

## 8. Ce qui reste flou

 comment partager le stockage DVC à plusieurs, ou comment comparer deux modèles sur le même jeu de test
