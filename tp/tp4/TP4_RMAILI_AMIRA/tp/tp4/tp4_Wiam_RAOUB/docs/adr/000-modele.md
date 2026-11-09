# ADR 000 : Modèle de prédiction des pannes

Date : 09/11/2026 · Auteurs : Wiam Raoub

## Contexte

MaintAI reçoit quatre mesures de capteurs (température, vibration, charge et heures de fonctionnement) et doit fournir une probabilité de panne ainsi qu'une alerte exploitable par la CLI et l'API. Le projet doit pouvoir s'entraîner localement sur des données synthétiques, sans téléchargement externe, et comparer ses résultats à une baseline.

## Options étudiées

1. Règles à seuils définies à la main : faciles à expliquer et à exécuter, mais elles exigent de choisir manuellement les seuils et ne sont pas apprises à partir des données.
2. Modèle d'ensemble d'arbres (par exemple une forêt aléatoire) : peut représenter des relations non linéaires, mais ajoute de la complexité par rapport au besoin de démonstration du projet.
3. Régression logistique avec standardisation : fournit des probabilités, reste simple à entraîner et à intégrer, et offre une base adaptée pour évaluer la prédiction de panne.

## Décision

Retenir une pipeline scikit-learn composée de `StandardScaler` et `LogisticRegression(max_iter=1000)`. La pipeline complète est sauvegardée avec joblib afin que le même prétraitement soit appliqué pendant l'entraînement et la prédiction. La décision d'alerte utilise un seuil configurable, fixé par défaut à `0.3` via `MAINTAI_THRESHOLD`, plutôt que le seuil standard de 0.5. Le modèle est évalué sur un jeu de test stratifié (20 %, graine 42) et comparé à une baseline `DummyClassifier` qui prédit toujours la classe majoritaire.

## Conséquences

- Le modèle renvoie une probabilité de panne et l'alerte est calculée à partir du seuil configuré.
- La pipeline et ses métadonnées (variables d'entrée, cible, seuil, date d'entraînement et version de scikit-learn) sont enregistrées dans `models/`; les métriques sont enregistrées séparément.
- Les données générées sont synthétiques et servent aux tests et à la démonstration. Elles ne permettent pas de conclure sur les performances en production ; un jeu de données réel validé sera nécessaire avant tout usage opérationnel.
- Le modèle sérialisé n'est pas inclus dans le wheel. Il faut l'entraîner localement ou fournir son dossier avec `MAINTAI_MODELS_DIR`.
- Le chargement d'un modèle joblib peut dépendre de la version de scikit-learn utilisée à l'entraînement ; la version est enregistrée dans `model_info.json` et doit être prise en compte lors du déploiement.
