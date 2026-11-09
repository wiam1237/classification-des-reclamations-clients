# ADR 000 : Transformation de MaintAI en package Python installable

Date : 09/11/2026 · Auteurs : Ouiam ERREYYADI

## Contexte

Le projet MaintAI doit évoluer d'une application Python exécutée depuis son dossier source vers un package Python installable et réutilisable. Il est nécessaire de structurer le projet, de déclarer ses dépendances et de permettre l'exécution de ses fonctionnalités depuis la ligne de commande, tout en conservant l'accès au modèle de prédiction.

## Options étudiées

1. **Conserver le projet sous forme de scripts Python** : solution simple à mettre en place, mais qui nécessite de lancer les scripts depuis le dossier du projet et rend la réutilisation moins pratique.

2. **Transformer le projet en package Python avec `pyproject.toml`** : permet de définir les métadonnées, les dépendances et le point d'entrée CLI. Cette solution demande une configuration supplémentaire et une gestion adaptée des fichiers du modèle.

## Décision

Nous avons choisi de transformer MaintAI en package Python installable en utilisant `pyproject.toml` et une installation éditable avec `pip install -e .`. Cette décision facilite le développement, les tests et l'utilisation de la commande `maintai-predict`, conformément à l'objectif du TP4.

## Conséquences

Cette décision facilite l'installation du projet, la gestion de ses dépendances, son utilisation en ligne de commande et sa réutilisation dans d'autres environnements Python.

En revanche, le modèle de prédiction doit être géré séparément du package installé, notamment dans le cas d'une installation depuis le fichier Wheel. Il faut donc surveiller la configuration du chemin d'accès au modèle avec `MAINTAI_MODELS_DIR`, ainsi que la compatibilité des versions des bibliothèques, notamment scikit-learn.