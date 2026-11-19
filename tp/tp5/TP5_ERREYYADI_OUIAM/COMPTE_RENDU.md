# Compte rendu – TP5 : Suivi des entraînements avec MLflow et versionnement des données avec DVC

**Groupe :** G2  
**Membre :** ERREYYADI Ouiam


---

## 1. Mise en place

**Dernière ligne obtenue après l'installation des dépendances et l'exécution des tests :**

```text
32 passed, 4 warnings in 9.77s
```

**Quels tests échouaient initialement, et pour quelle raison ?**

Au départ, les cinq tests du fichier `tests/test_tracking.py` échouaient, car la fonction `log_run` n'était pas encore implémentée. Après avoir développé cette fonction, l'ensemble des tests a été validé : 32 tests réussis. Les quatre avertissements restants concernent certaines dépendances (Starlette/HTTPX et SQLAlchemy), ainsi que l'exemple d'entrée utilisé par MLflow. Ils n'affectent pas le bon déroulement des tests.

**Avant et après l'exécution de `pip install -e .`, où se trouvait le package `maintai` ?**

Avant l'installation, l'environnement utilisait la version du package associée au TP4. Après l'exécution de `pip install -e .` depuis le répertoire du TP5, le package est configuré en mode éditable et pointe vers le code source du TP5. Le chemin exact de l'installation précédente n'ayant pas été enregistré, il peut être vérifié à l'aide de la commande :

```bash
python -m pip show maintai
```

Il suffit ensuite de consulter les champs `Location` et `Editable project location`.

---

## 2. Sprint 1 : Suivi des entraînements avec MLflow

### 2.1. Implémentation de la fonction `log_run`

La fonction `log_run`, développée dans `maintai/tracking.py`, permet d'assurer la traçabilité de chaque entraînement. Elle enregistre les paramètres du modèle, l'empreinte des données utilisées, les métriques obtenues ainsi que le modèle entraîné.

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

**Résultat des tests à la fin du Sprint 1 :**

```text
32 passed, 4 warnings in 9.77s
```

### 2.2. Comparaison des entraînements MLflow

Quatre entraînements ont été réalisés avec différents paramètres, puis comparés dans l'interface MLflow, en mode « Model training ».

| Commande exécutée | Run MLflow | Recall | Précision | Accuracy |
|---|---|---:|---:|---:|
| `python -m maintai.train --model forest` | `gentle-shrew-699` | 0.728 | 0.562 | 0.886 |
| `python -m maintai.train --threshold 0.2` | `hilarious-bear-847` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --C 0.01` | `painted-roo-545` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train` | `invincible-wasp-543` | 0.750 | 0.622 | 0.904 |

Les quatre entraînements ont été effectués sur la version v1 des données, identifiée par l'empreinte MD5 suivante :

`b7fec4274774842dc1f48202c6013490`

Le nombre d'exemples d'entraînement est de 4 000 pour chaque essai.

### 2.3. Choix du modèle pour MaintAI

Le run `hilarious-bear-847` constitue le choix provisoire le plus adapté à MaintAI. Il présente le meilleur rappel (*recall*), avec une valeur de 0.838, ce qui signifie qu'il détecte une proportion plus importante des pannes réelles.

Ce critère est particulièrement important dans notre cas, puisqu'une panne non détectée représente un coût supérieur à celui d'une fausse alerte.

Cependant, ce modèle présente une précision de 0.543, la plus faible parmi les quatre essais. Il génère donc davantage de fausses alertes. Le choix définitif devra tenir compte du coût acceptable de ces alertes et être confirmé par une validation sur des données représentatives.

**Identifiant du run retenu :** `c83e9ea5946b4d258932046d6b7348e6`.

### 2.4. Version de scikit-learn et reproductibilité

Dans le fichier `requirements.txt` du modèle enregistré sur MLflow, la version de scikit-learn indiquée est :

`scikit-learn==1.8.0`

Cette information permet de fixer explicitement la version de la bibliothèque utilisée pendant l'entraînement. Elle évite ainsi les problèmes de compatibilité pouvant apparaître lors du rechargement du modèle avec une version différente, notamment les problèmes de reproductibilité rencontrés au TP4.

### 2.5. Stockage des résultats MLflow

Les expériences et leurs artefacts sont enregistrés localement dans les éléments suivants :

- `mlflow.db` : base de données contenant les informations relatives aux expériences et aux runs.
- `mlruns/` : répertoire regroupant les résultats et les artefacts des entraînements.

Ces fichiers ne sont pas destinés à être versionnés avec Git, car ils sont générés localement et peuvent occuper un espace important. Le dépôt Git doit principalement conserver le code source et les fichiers nécessaires au suivi du projet.

---

## 3. Sprint 2 : Versionnement des données avec DVC

### 3.1. Création du fichier de suivi DVC

Après l'exécution de la commande :

```bash
dvc add data/sensors.csv
```

DVC a généré le fichier `data/sensors.csv.dvc`, qui contient les informations permettant d'identifier et de retrouver la version correspondante du jeu de données.

Pour la version v1, l'empreinte MD5 relevée est :

```yaml
outs:
- md5: b7fec4274774842dc1f48202c6013490
  hash: md5
  path: sensors.csv
```

Le fichier DVC complet peut également contenir la taille du fichier, mais cette information n'a pas été conservée dans les résultats disponibles.

### 3.2. Comparaison entre le MD5 de DVC et celui de MLflow

L'empreinte MD5 de la version v1 est identique dans le fichier DVC et dans le paramètre `data_md5` enregistré par MLflow :

`b7fec4274774842dc1f48202c6013490`

Cette correspondance confirme que les quatre entraînements réalisés précédemment utilisent bien la même version des données.

Après la génération de la version v2, une nouvelle empreinte a été obtenue :

`31ef5ebb63ef2331a31dfe009ef8796a`

On peut ainsi identifier précisément la version du jeu de données utilisée pour chaque entraînement.

### 3.3. Pourquoi versionner le fichier `.dvc` plutôt que le CSV avec Git ?

Le fichier `data/sensors.csv` contient directement les données, dont le volume peut devenir important et dont les différentes versions doivent être conservées.

DVC prend en charge ce versionnement en stockant le contenu des fichiers dans son cache ou dans un stockage dédié. De son côté, Git conserve le fichier `data/sensors.csv.dvc`, qui contient notamment l'empreinte permettant d'identifier et de retrouver la version correspondante.

Cette organisation permet de séparer le versionnement du code de celui des données volumineuses.

### 3.4. Modification du jeu de données

Après avoir généré 8 000 relevés avec la commande :

```bash
python -m maintai.dataset --n 8000 --seed 7
```

La commande `dvc status` a indiqué que le fichier de données avait été modifié :

```text
data/sensors.csv.dvc:
    changed outs:
        modified: data/sensors.csv
```

Ce résultat signifie que le contenu actuel de `data/sensors.csv` ne correspond plus à la version enregistrée dans le fichier de suivi DVC.

### 3.5. Comparaison des versions v1 et v2

| Version | Commit Git | Empreinte MD5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---:|
| v1 | `09045bd` | `b7fec427` | 5 001 |
| v2 | `497a74b` | `31ef5ebb` | 8 001 |

La version v1 contient 5 000 relevés, tandis que la version v2 en contient 8 000. Dans les deux cas, le nombre total de lignes inclut également la ligne d'en-tête du fichier CSV.

### 3.6. Restauration de la version v1 puis de la version v2

Pour revenir à la version v1, les commandes suivantes ont été exécutées :

```bash
git checkout 09045bd -- data/sensors.csv.dvc
dvc checkout
```

Cette opération a permis de restaurer le fichier contenant 5 001 lignes, soit 5 000 relevés et une ligne d'en-tête.

Pour revenir ensuite à la version v2, le fichier de suivi correspondant au commit `497a74b` a été restauré, puis `dvc checkout` a été exécuté.

Le fichier CSV contient alors 8 001 lignes, correspondant à 8 000 relevés et à son en-tête.

### 3.7. Récupération des données avec `dvc pull`

Après la suppression du fichier `data/sensors.csv` et du répertoire `.dvc/cache`, la commande suivante a été exécutée :

```bash
dvc pull
```

DVC a récupéré les données depuis le stockage configuré et a affiché le résultat suivant :

```text
1 file fetched and 1 file added
```

Le fichier a ainsi été restauré avec succès et contient 8 001 lignes, soit les 8 000 relevés de la version v2 et la ligne d'en-tête.

Cette manipulation montre que DVC permet de récupérer les données même lorsque le fichier original et le cache local ont été supprimés.

---

## 4. Mise en relation du modèle et des données

### 4.1. Comparaison des entraînements sur les versions v1 et v2

Un nouvel entraînement a été effectué sur la version v2 afin de comparer ses résultats avec ceux obtenus sur la version v1, en conservant les mêmes paramètres.

| Version | MD5 (8 caractères) | Nombre d'exemples d'entraînement | Recall | Précision |
|---|---|---:|---:|---:|
| v1 | `b7fec427` | 4 000 | 0.838 | 0.543 |
| v2 | `31ef5ebb` | 6 400 | 0.824 | 0.567 |

Les deux entraînements utilisent les mêmes réglages :

- Modèle : régression logistique.
- Paramètre `C` : 1.0.
- Seuil de classification : 0.2.

Le run correspondant à la version v2 est `fun-dove-613`, avec l'identifiant :

`6f2ba3ea99e24c2bb9c6e18ba15d6a4a`

Son empreinte MD5 est `31ef5ebb63ef2331a31dfe009ef8796a`.

### 4.2. Analyse des résultats

La comparaison met en évidence quelques différences entre les deux versions.

Sur la version v1, le rappel atteint 0.838, contre 0.824 pour la version v2. La v1 présente donc un léger avantage pour la détection des pannes.

En revanche, la version v2 obtient une meilleure précision, avec 0.567 contre 0.543 pour la v1. Son accuracy progresse également, passant de 0.882 à 0.897.

Il faut toutefois éviter de conclure que la version v2 est globalement meilleure. En effet, le volume des données a changé, tout comme le nombre d'exemples utilisés pour l'entraînement. Les ensembles d'entraînement et de test ne sont donc pas identiques.

Puisque les pannes manquées représentent le risque le plus important pour MaintAI, la version v1 conserve le meilleur rappel parmi les deux expériences comparées. Néanmoins, le choix final doit être confirmé par une validation sur des données de test représentatives avant toute mise en production.

---

## 5. Décision : ADR 004

La décision technique est présentée dans le fichier :

`docs/adr/004-choix-du-modele.md`

L'ADR 004 prend désormais en compte les résultats des entraînements réalisés sur les versions v1 et v2, avec des paramètres identiques.

Cette comparaison permet de justifier le choix du modèle à partir de résultats mesurables, en accordant une importance particulière au rappel, puisque l'objectif prioritaire est de limiter les pannes non détectées.

---

## 6. Questions de compréhension

**1. Quelle est la différence entre Git, DVC et MLflow ? Que versionne chacun ?**

Ces trois outils interviennent à des niveaux complémentaires :

- **Git** assure le versionnement du code source et des fichiers de configuration ou de suivi du projet.
- **DVC** permet de versionner les données volumineuses et de retrouver leurs différentes versions grâce aux fichiers de suivi conservés dans Git.
- **MLflow** assure le suivi des expériences d'entraînement en enregistrant les paramètres, les métriques, les versions des données et les modèles produits.

Leur utilisation conjointe permet d'améliorer la traçabilité et la reproductibilité du projet.

**2. Pourquoi le stockage DVC est-il configuré avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe puisse partager les mêmes données ?**

Dans ce TP, le stockage DVC est configuré localement avec le chemin `~/dvc-stockage`. Cette configuration est propre à la machine utilisée et ne doit pas être partagée dans le dépôt Git.

Pour permettre à tous les membres du groupe d'accéder aux mêmes versions des données, il faudrait mettre en place un stockage distant accessible à tous, par exemple un serveur ou un espace de stockage cloud. Chaque membre devrait ensuite disposer des autorisations et de la configuration nécessaires pour y accéder.

**3. Livrer un modèle, c'est trois éléments (TP4). Lesquels et où les retrouve-t-on maintenant ?**

La livraison d'un modèle repose sur trois éléments complémentaires :

1. **Le modèle entraîné :** il est disponible localement dans `models/model.joblib` et sous forme d'artefact `model` dans MLflow.
2. **Le contrat d'entrée et le prétraitement :** ils sont représentés par `models/model_info.json` et par le pipeline enregistré avec le modèle.
3. **L'environnement logiciel :** il est décrit par les versions des dépendances dans `requirements.txt`, également enregistrées avec le modèle MLflow.

Ces trois éléments permettent de disposer du modèle, de comprendre les données qu'il attend et de réunir les conditions nécessaires à son exécution.

---

## 7. Le rendu Git

Les éléments suivants résument l'état du dépôt à la dernière vérification :

- **Pull Request :** elle reste à créer depuis la branche `tp5-wiam-raoub-dvc` vers la branche `main`.
- **Tag `tp5` :** son existence sur GitHub n'a pas encore été vérifiée. Les tags précédemment observés étaient `tp3` et `tp4`.
- **État du dépôt (`git status`) :** les fichiers `mlflow.db`, `mlruns/`, `data/sensors.csv` et `.dvc/cache` sont ignorés par Git. En revanche, les fichiers de suivi DVC, notamment les fichiers `.dvc` et `.dvcignore`, ont été ajoutés et commités.
- **Synchronisation :** la branche `tp5-wiam-raoub-dvc` a été poussée sur le dépôt distant et était synchronisée avec `origin/tp5-wiam-raoub-dvc` lors de la dernière vérification.

---

## 8. Points restant à clarifier

Le principal point de vigilance concerne la validation des performances du modèle sur des données de test représentatives.

En effet, le passage de la version v1 à la version v2 modifie le volume des données ainsi que les échantillons utilisés pour l'entraînement et le test. Les différences de métriques observées doivent donc être interprétées avec prudence.

Une validation complémentaire sera nécessaire avant de retenir définitivement un modèle pour le déploiement.

---

## 9. Grid Search et sélection des paramètres

Les différents réglages ont été comparés manuellement à travers quatre expériences enregistrées dans MLflow sur la version v1 des données. Aucun `GridSearchCV` automatique n'a été utilisé.

Le rappel (*recall*) a été retenu comme critère prioritaire, car une panne non détectée entraîne un coût plus important qu'une fausse alerte.

### 9.1. Résultats des expériences

| Modèle | C | Seuil | Recall | Précision | Accuracy |
|---|---:|---:|---:|---:|---:|
| Forêt aléatoire | — | 0.3 | 0.728 | 0.562 | 0.886 |
| Régression logistique | 1.0 | 0.2 | **0.838** | 0.543 | 0.882 |
| Régression logistique | 0.01 | 0.3 | 0.691 | **0.653** | **0.908** |
| Régression logistique | 1.0 | 0.3 | 0.750 | 0.622 | 0.904 |

### 9.2. Interprétation et choix final provisoire

Parmi les quatre expériences, la régression logistique avec `C=1.0` et un seuil de classification de `0.2` obtient le meilleur rappel, avec une valeur de 0.838.

Ce réglage est donc retenu provisoirement pour MaintAI, car il permet de limiter davantage les pannes non détectées. Ce choix implique toutefois une précision plus faible et, par conséquent, un nombre plus important de fausses alertes.

La comparaison entre les versions v1 et v2 confirme que ce réglage obtient un rappel de 0.838 sur la v1 et de 0.824 sur la v2.

Ainsi, le modèle retenu constitue le meilleur compromis parmi les essais réalisés au regard de la priorité donnée à la détection des pannes. Une validation sur des données de test représentatives reste néanmoins indispensable avant son déploiement.