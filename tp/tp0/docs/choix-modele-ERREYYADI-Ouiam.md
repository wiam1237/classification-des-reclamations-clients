# Choix du modèle — Détection des pannes d’équipements

**Date :** 26/10/2026 · **Groupe :** MaintAI

## Contexte

Le projet vise à déterminer si une observation de fonctionnement d’un équipement correspond à une panne (`failure = 1`), à partir de mesures relatives à la température, aux vibrations, à la charge et à la durée de fonctionnement. Le rappel est retenu comme métrique principale afin d’évaluer la capacité du modèle à détecter les pannes. La précision et le score F1 sont également considérés pour compléter l’analyse, notamment au regard des fausses alertes.

## Données et stratégie de découpage

Le fichier `data/exemple_pannes.csv` comporte 5 000 observations, dont 4 122 sans panne et 878 avec panne. Les variables utilisées sont `temperature_c`, `vibration_mm_s`, `load_pct` et `runtime_hours`. Aucune valeur manquante n’a été observée dans le fichier.

Les données sont réparties de manière aléatoire et stratifiée selon la cible, avec `random_state=42` : 80 % des observations sont consacrées à l’entraînement et 20 % au test, soit 1 000 lignes. La source et la licence du jeu de données ne sont pas précisées dans le projet.

## Résultats obtenus sur le jeu de test

| Modèle | Rappel (métrique principale) | Accuracy | Précision | F1 |
|---|---:|---:|---:|---:|
| Baseline (classe majoritaire) | 0,000 | 0,824 | 0,000 | 0,000 |
| Régression logistique | **0,847** | 0,839 | 0,527 | **0,649** |
| Arbre de décision | 0,545 | 0,851 | 0,582 | 0,563 |
| Forêt aléatoire | 0,693 | **0,862** | **0,592** | 0,639 |

## Décision

La régression logistique est retenue, car elle présente le rappel le plus élevé parmi les modèles évalués (0,847). Elle surpasse la baseline de 0,847 en valeur absolue, soit 84,7 points de pourcentage, alors que cette dernière ne détecte aucune panne. La forêt aléatoire obtient les meilleures valeurs d’accuracy et de précision, mais son rappel est inférieur (0,693).

L’étude de conception ne définissant aucun seuil d’acceptation quantitatif, il n’est pas possible de conclure formellement que le modèle satisfait aux exigences opérationnelles.

## Limites

Les résultats reposent sur un unique découpage aléatoire comprenant 1 000 observations de test. Ils ne garantissent donc pas des performances équivalentes sur d’autres équipements ou périodes. En outre, le jeu de données est déséquilibré (environ 17,6 % d’observations de panne), ce qui rend insuffisante l’interprétation de l’accuracy prise isolément.

Les coûts opérationnels associés aux fausses alertes et aux pannes non détectées, ainsi que la provenance et la représentativité des données, ne sont pas documentés. Avant tout usage opérationnel, une validation sur des données réelles et une évaluation au regard d’un seuil d’acceptation défini sont nécessaires.

# Choix du modèle — Prévision des repas de cantine

**Date :** 26/10/2026 · **Groupe :** CantineAI

## Contexte

Ce projet a pour objectif d’estimer le nombre de repas à servir (`repas_servis`) à partir des informations relatives à la journée et à la fréquentation récente, afin d’appuyer la planification des quantités. Il s’agit d’un problème de régression. La MAE (erreur absolue moyenne), exprimée en nombre de repas, est retenue comme métrique principale, car elle correspond directement à l’écart moyen entre les prévisions et les valeurs observées.

## Données et stratégie de découpage

Le fichier `data/cantine_repas.csv` comprend 340 observations couvrant la période du 9 septembre 2024 au 19 juin 2026. La variable cible varie de 248 à 695 repas servis et sa moyenne est de 499. Les variables utilisées sont `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances` et `repas_semaine_precedente`. La date sert uniquement à établir l’ordre chronologique des observations ; elle n’est pas fournie au modèle comme variable prédictive.

Le découpage respecte l’ordre temporel : 272 observations, du 9 septembre 2024 au 24 février 2026, sont utilisées pour l’entraînement ; les 68 observations les plus récentes, du 25 février au 19 juin 2026, constituent le jeu de test. La variable `repas_semaine_precedente` contient 60 valeurs manquantes. Celles-ci sont imputées par la médiane au sein d’un pipeline ajusté sur les données d’entraînement.

## Résultats obtenus sur le jeu de test

| Modèle | MAE (repas, métrique principale) | RMSE (repas) | R² |
|---|---:|---:|---:|
| Baseline (prédiction de la moyenne d’entraînement) | 70,271 | 88,416 | -0,151 |
| Régression linéaire (`LinearRegression`) | **22,239** | **28,170** | **0,883** |
| Ridge (régression linéaire régularisée) | 22,623 | 28,545 | 0,880 |
| Arbre de décision | 46,000 | 59,710 | 0,475 |
| Forêt aléatoire | 31,825 | 41,647 | 0,745 |

## Décision

La régression linéaire (`LinearRegression`) est retenue, car elle présente la MAE la plus faible parmi les modèles comparés. Sur la période de test, son erreur absolue moyenne est d’environ 22 repas. Par rapport à la baseline, sa MAE diminue de 48,032 repas, soit une réduction d’environ 68,4 %.

Le modèle Ridge, qui correspond à une régression linéaire régularisée par pénalité L2, produit des résultats proches (MAE de 22,623). Le R² de 0,883 obtenu par la régression linéaire indique un bon ajustement sur le jeu de test considéré, sans toutefois garantir des performances similaires sur des données futures.

Aucun seuil d’acceptation métier n’a été défini. Il conviendra donc de déterminer avec l’équipe de la cantine le niveau d’erreur tolérable, en tenant compte des conséquences respectives d’un manque et d’un surplus de repas.

## Limites et précautions

- Les résultats reposent sur un seul découpage temporel, comprenant 68 jours de test. Une évaluation sur d’autres périodes est nécessaire pour apprécier la stabilité des performances.
- La disponibilité effective de chaque variable au moment où la prévision est produite doit être vérifiée. En particulier, les données météorologiques et le nombre de repas de la semaine précédente ne doivent être utilisés que si elles sont connues à l’horizon de prévision retenu.
- Une modalité de la variable `menu` apparaît mal décodée dans le fichier CSV (`v�g�tarien`). L’encodage et les valeurs de cette catégorie doivent être vérifiés.
- La provenance et la licence du jeu de données, les coûts associés à la surproduction ou au manque de repas, ainsi que le seuil de tolérance opérationnel ne sont pas documentés.
- La comparaison n’inclut ni modèle saisonnier dédié ni validation croisée temporelle.
