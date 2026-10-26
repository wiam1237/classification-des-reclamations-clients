# ADR 002 : Validation des données d’entrée

Date : 26/10/2026 · Auteurs : [imane elouali]

## Contexte

L’API MaintAI reçoit des données de capteurs utilisées pour prédire les pannes des machines. Des valeurs irréalistes peuvent compromettre la fiabilité des prédictions ; il faut donc définir des limites pour chaque donnée et gérer l’indisponibilité du modèle.

## Options étudiées

1. **Accepter toutes les valeurs** : simplifie le traitement, mais risque de produire des prédictions incorrectes avec des données irréalistes.
2. **Valider les valeurs et gérer les erreurs** : améliore la fiabilité, mais nécessite de définir des limites et de traiter les erreurs.

## Décision

Nous choisissons la validation des données avec Pydantic. La température doit être comprise entre -40 et 150 °C, les vibrations entre 0 et 100 mm/s, la charge entre 0 et 100 %, et la durée de fonctionnement entre 0 et 200 000 heures.

Une donnée hors limites entraîne une réponse HTTP 422. Si le modèle de prédiction est indisponible, l’API renvoie une réponse HTTP 503 au lieu de tenter une prédiction impossible.

## Conséquences

La validation empêche les valeurs hors limites d’être utilisées pour la prédiction et rend les erreurs plus explicites. Il faut toutefois veiller à ce que les limites correspondent aux données réalistes des machines et à ce que l’indisponibilité du modèle soit correctement signalée.