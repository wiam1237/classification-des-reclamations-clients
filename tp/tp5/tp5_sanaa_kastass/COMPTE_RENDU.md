# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** 2  ·  **Membres :** SANAA KASTASS  ·  **Date :** 16/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
5 failed, 27 passed
```

Quels tests échouent, et pourquoi ?

Les 5 tests de `tests/test_tracking.py` échouent (`test_training_creates_a_run`, `test_run_records_metrics`, `test_run_records_data_version`, `test_run_stores_the_model`, `test_options_change_the_run`). Ils vérifient qu'un run MLflow existe après un entraînement, mais la fonction `log_run` est encore vide (elle renvoie `""` sans rien enregistrer) : il n'y a donc aucun run à retrouver.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Avant, l'environnement (celui du TP4) avait `maintai` installé en mode éditable vers le dossier `TP/TP4`. Après `pip install -e .` lancé dans `TP/TP5`, le package pointe vers `TP/TP5` : `import maintai` utilise maintenant le code du TP5 (version qui contient `tracking.py`).

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
32 passed
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.750 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| `python -m maintai.train` (sur les données v2, 8000 relevés) | 0.741 | 0.650 | 0.916 |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Nous choisirions le run `--threshold 0.2` (régression logistique) : c'est celui qui a le meilleur recall (0.838), donc celui qui rate le moins de pannes. Il a une precision plus faible (0.543), donc plus de fausses alertes, mais c'est acceptable puisqu'une fausse alerte coûte moins cher qu'une panne manquée. La forêt aléatoire n'est pas meilleure : son recall (0.728) est inférieur à celui de la régression logistique avec le même seuil (0.750), et elle est plus lourde.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

Le `requirements.txt` du modèle indique `scikit-learn==1.8.0`. Au TP4, `models/` ne gardait que le dernier modèle, sans la version exacte des bibliothèques : recharger un modèle avec une autre version de scikit-learn pouvait le faire échouer ou donner des résultats différents. Maintenant, chaque run garde les versions exactes avec lesquelles le modèle a été entraîné.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

MLflow écrit dans `mlflow.db` (base SQLite : paramètres, métriques, tags) et dans le dossier `mlruns/` (les modèles et leurs artefacts), à la racine de `TP/TP5` (le dossier où on lance les commandes). Ces fichiers ne vont pas dans Git : ils sont propres à chaque machine, lourds, binaires pour la base, et reproductibles en ré-entraînant. Ils sont exclus par le `.gitignore`.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
COLLER_ICI_LA_SORTIE_DE: type data\sensors.csv.dvc
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

Les deux valeurs sont identiques. La fonction `file_md5` de `tracking.py` calcule la même empreinte que DVC : c'est ce qui relie un run MLflow à une version précise des données.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Un fichier de données peut être très gros (100 Mo ou plus) et Git garde chaque version pour toujours, ce qui alourdit le dépôt. DVC garde le fichier dans un cache puis dans un stockage, et ne met dans Git qu'un petit reçu (le `.dvc` : le md5 et la taille, quelques lignes). Git versionne donc le reçu, et DVC retrouve le fichier correspondant.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
COLLER_ICI_LA_SORTIE_DE: dvc status
```

(Il indique que `data/sensors.csv` est modifié par rapport au reçu : `modified: data\sensors.csv`.)

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | COMMIT_V1 | MD5_V1 | 5000 |
| v2 | COMMIT_V2 | MD5_V2 | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après le retour à la v1, `data/sensors.csv` contient 5000 lignes. Git a rétabli l'ancien reçu et `dvc checkout` a remis le fichier correspondant depuis le cache. Après `git checkout HEAD -- data/sensors.csv.dvc` puis `dvc checkout`, on retrouve la v2 : 8000 lignes.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

DVC récupère le fichier depuis le stockage (le dossier `dvc-stockage`) vers le cache, puis le remet dans `data/` : `data/sensors.csv` réapparaît, avec le contenu de la version indiquée par le reçu. C'est ce que fait un coéquipier qui n'a pas les données : il clone le dépôt Git et fait `dvc pull`.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | MD5_V1 | 4000 | 0.750 | 0.622 |
| v2 | MD5_V2 | 6400 | 0.741 | 0.650 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non. Le recall est quasiment le même (0.741 contre 0.750) et la precision est un peu plus haute (0.650 contre 0.622) : la différence est faible et ne permet pas de conclure. Surtout, les deux modèles ne sont pas évalués sur le même jeu de test : la v2 a un autre jeu de relevés (autre graine, 8000 lignes, autre taux de pannes) et donc un autre jeu de test (1600 lignes contre 1000). Une différence de métrique peut venir des données et pas du modèle. Pour comparer des modèles, il faut garder les mêmes données ; le `data_md5` permet de vérifier que c'est bien le cas.

## 5. Décision : l'ADR 004

L'ADR est dans `docs/adr/004-choix-du-modele.md`. Modèle retenu : régression logistique avec le seuil 0.2 (recall 0.838, precision 0.543), car une panne manquée coûte plus cher qu'une fausse alerte. Identifiant du run : `COLLER_ICI_LIDENTIFIANT_DU_RUN`. `data_md5` de la version des données utilisée (v1) : `COLLER_ICI_LE_MD5_COMPLET`.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   Git versionne le code (et le petit reçu `.dvc` de chaque fichier de données). DVC versionne les fichiers de données (dans un cache et un stockage) et les relie à Git par le reçu. MLflow garde la trace de chaque entraînement : paramètres, empreinte des données, métriques, modèle et versions des bibliothèques.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   Le chemin du stockage est un dossier de notre PC : il ne doit pas aller dans Git. L'option `--local` l'écrit dans `.dvc/config.local`, ignoré par Git. Pour partager les données, il faudrait un stockage accessible à tout le groupe (S3, Google Drive, un serveur, un disque partagé), déclaré dans la configuration commune.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   Le code (dans Git, et le wheel du TP4), les données (avec DVC : le reçu dans Git, le fichier dans le stockage) et le modèle (dans MLflow : un run avec son identifiant). Les versions exactes des bibliothèques sont dans le `requirements.txt` du modèle, enregistré par MLflow.

## 7. Le rendu Git

- Lien de la pull request : COLLER_ICI_LE_LIEN
- Le tag `tp5` existe sur GitHub : oui
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? non

## 8. Ce qui reste flou

La différence entre le cache et le stockage de DVC, et la manière de partager vraiment le stockage dans une équipe avec un serveur distant.