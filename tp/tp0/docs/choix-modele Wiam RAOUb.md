Auteur : wiam1237

# Choix du modèle

Date : 26/10/2026 ·  Projet: maintenance prédictive

## Contexte
Le projet a pour objectif de prédire les pannes des machines à partir des données collectées par les capteurs de fonctionnement. La métrique principale utilisée est le recall, car il est essentiel de détecter le maximum de pannes réelles. En effet, en maintenance prédictive, ne pas détecter une panne peut entraîner un arrêt imprévu de la machine et provoquer des pertes opérationnelles importantes.
## Données et découpage
Le jeu de données utilisé est `data/exemple_pannes.csv`, composé de 5 000 lignes et 5 colonnes : `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours` et la cible `failure`. Les quatre variables de capteurs sont utilisées comme variables explicatives ; la cible est binaire (`0` = pas de panne, `1` = panne).

Le découpage est aléatoire stratifié avec un ratio 80/20, avec `random_state=42`, ce qui donne environ 4 000 observations pour l’entraînement et 1 000 pour le test. La cible est déséquilibrée (4 122 lignes sans panne contre 878 pannes), ce qui justifie le choix d’une métrique orientée détection des cas positifs.

## Résultats sur le jeu de test

| Modèle | Recall (métrique principale) | Accuracy | Precision | F1 |
|---|---:|---:|---:|---:|
| Arbre de décision | 0.597 | 0.839 | 0.538 | 0.566 |
| Régression logistique | 0.574 | 0.889 | 0.737 | 0.645 |
| Random Forest | 0.545 | 0.873 | 0.671 | 0.602 |
| K plus proches voisins | 0.540 | 0.878 | 0.699 | 0.609 |
| Baseline | 0.000 | 0.824 | 0.000 | 0.000 |

## Décision
Le modèle retenu est l’arbre de décision, car il obtient le meilleur recall sur le jeu de test, avec une valeur de 0,597, contre 0,000 pour la baseline. Il permet donc de détecter davantage de pannes réelles. Ce résultat répond au besoin principal du projet, qui est d’identifier le maximum de pannes potentielles, même si la précision est moins élevée que celle de la régression logistique.

Le critère d’acceptation est atteint, car le modèle dépasse la baseline et obtient un recall supérieur à 0,50. Ce seuil indique que le modèle présente un intérêt pour la détection des pannes, même si des améliorations restent nécessaires avant son utilisation en production.

## Limites
Ces résultats ne prennent pas en compte tous les scénarios possibles. Le jeu de test contient environ 1 000 observations, le découpage des données est aléatoire et les données utilisées sont synthétiques. De plus, le déséquilibre entre les classes peut influencer l’évaluation des performances, et certains modèles génèrent encore un nombre important de fausses alertes. Il sera donc nécessaire de tester le modèle sur de nouvelles données réelles et plus représentatives des conditions de maintenance industrielle afin de confirmer sa fiabilité.

---

# Choix du modèle — Variante cantines repas

Date : 26/10/2026 ·  Projet: cantines repas

## Contexte
Le projet vise à prédire le nombre de repas servis dans une cantine scolaire à partir de données de fréquentation et de contexte (jour, menu, météo, examens, vacances, etc.). La métrique principale est le MAE (Mean Absolute Error), car l’objectif est de minimiser l’erreur moyenne de prévision afin d’optimiser les achats, la préparation et l’organisation des ressources sans surstock ni rupture.

## Données et découpage
Le jeu de données utilisé est `data/cantine_repas - cantine_repas.csv`, composé de 340 lignes et 11 colonnes. Les variables explicatives incluent la date, le jour, le nombre d’inscrits, le type de menu, la température, les précipitations, la présence d’examens, les sorties scolaires, le statut de veille de vacances, ainsi que le nombre de repas servis la semaine précédente. La cible est `repas_servis`, une variable quantitative.

Le découpage est chronologique avec un ratio 80/20, en gardant les observations les plus récentes pour le test. Cela permet d’évaluer le modèle sur un horizon futur réel, sans fuite de données. L’ensemble de test contient environ 68 jours.

## Résultats sur le jeu de test

| Modèle | MAE (métrique principale) | RMSE | R² |
|---|---:|---:|---:|
| Régression linéaire | 22.239 | 28.170 | 0.883 |
| Ridge | 22.623 | 28.545 | 0.880 |
| Random Forest | 31.845 | 41.540 | 0.746 |
| K plus proches voisins | 36.212 | 46.037 | 0.688 |
| Arbre de décision | 46.000 | 59.710 | 0.475 |
| Baseline | 70.271 | 88.416 | -0.151 |

## Décision
Le modèle retenu est la régression linéaire, car il obtient le meilleur MAE sur le jeu de test : 22,239 contre 70,271 pour la baseline. L’amélioration est d’environ 48 repas en moyenne par jour, ce qui est très significatif pour une prévision de fréquentation dans une cantine. La régression linéaire est donc la plus adaptée au besoin métier : prévoir avec précision le nombre de repas à préparer pour mieux organiser les achats et les moyens de production.

Le critère d’acceptation est atteint : le modèle retenu améliore clairement la baseline sur la métrique principale et atteint un R² de 0,883, ce qui confirme une bonne capacité prédictive sur les données de test.

## Limites
Les résultats obtenus reposent sur un échantillon de seulement 340 jours, ce qui peut limiter la capacité du modèle à gérer des situations inhabituelles, comme les vacances ou les événements exceptionnels. Le découpage chronologique est adapté, car il permet de simuler les conditions réelles d’utilisation du modèle. Cependant, sa fiabilité dépend de la stabilité des tendances de consommation au fil du temps. Enfin, le modèle ne prend pas directement en compte certains facteurs externes, comme les changements de politique de restauration ou les variations soudaines du nombre de clients, qui peuvent influencer les prévisions.
