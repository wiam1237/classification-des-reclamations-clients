# Choix du modèle

Date : 26/10/2026 · Groupe : MaintAI

## Contexte
Le projet prédit si une observation d'équipement correspond à une panne (`failure = 1`) à partir de mesures de température, vibration, charge et durée de fonctionnement. Le rappel est retenu comme métrique principale afin de limiter les pannes manquées ; la précision et le F1 complètent l'analyse des fausses alertes.

## Données et découpage
Le fichier `data/exemple_pannes.csv` contient 5 000 lignes : 4 122 observations sans panne et 878 avec panne. Les quatre variables utilisées sont `temperature_c`, `vibration_mm_s`, `load_pct` et `runtime_hours`. Aucune valeur manquante n'a été observée dans ce fichier. Le découpage est aléatoire, stratifié sur la cible, avec `random_state=42` : 80 % pour l'entraînement et 20 % (1 000 lignes) pour le test. La source et la licence des données ne sont pas précisées dans le projet.

## Résultats sur le jeu de test

| Modèle | Rappel (principal) | Accuracy | Précision | F1 |
|---|---:|---:|---:|---:|
| Baseline (classe majoritaire) | 0,000 | 0,824 | 0,000 | 0,000 |
| Régression logistique | **0,847** | 0,839 | 0,527 | **0,649** |
| Arbre de décision | 0,545 | 0,851 | 0,582 | 0,563 |
| Forêt aléatoire | 0,693 | **0,862** | **0,592** | 0,639 |

## Décision
Le modèle retenu est la régression logistique, car il obtient le meilleur rappel (0,847) parmi les modèles comparés. Il dépasse la baseline de 0,847 point de rappel (84,7 points de pourcentage) ; celle-ci ne détecte aucune panne. La forêt aléatoire a l'accuracy et la précision les plus élevées, mais son rappel est inférieur (0,693). Aucun seuil d'acceptation chiffré n'étant défini dans l'étude de conception, il n'est pas possible de conclure formellement qu'un critère d'acceptation est atteint.

## Limites
Les scores proviennent d'un seul découpage aléatoire de 1 000 lignes et ne garantissent pas les performances sur des équipements ou périodes différents. Le jeu est déséquilibré (environ 17,6 % de pannes) ; le score d'accuracy seul serait donc insuffisant. Les coûts opérationnels des fausses alertes et des pannes manquées, la provenance des données et leur représentativité ne sont pas documentés. Une validation sur des données réelles et une évaluation avec un seuil d'acceptation défini sont nécessaires avant tout usage opérationnel.









# Choix du modèle — Prévision des repas de cantine

Date : 26/10/2026 · Groupe : CantineAI
## Contexte

L'objectif est d'estimer le nombre de repas à servir (`repas_servis`) à partir des informations du jour et de la fréquentation récente, pour aider à prévoir les quantités. Il s'agit d'une régression. La MAE (erreur absolue moyenne), exprimée en nombre de repas, est retenue comme métrique principale car elle s'interprète directement en écart moyen de prévision.

## Données et découpage

Le fichier `data/cantine_repas.csv` comprend 340 observations, du 9 septembre 2024 au 19 juin 2026. La cible varie de 248 à 695 repas servis, avec une moyenne de 499. Les variables utilisées sont `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances` et `repas_semaine_precedente`. La date sert uniquement à l'ordre temporel et n'est pas donnée comme variable au modèle.

Le découpage suit le temps : entraînement sur 272 observations du 9 septembre 2024 au 24 février 2026, puis test sur les 68 observations les plus récentes, du 25 février au 19 juin 2026. La colonne `repas_semaine_precedente` comporte 60 valeurs manquantes ; l'imputation médiane est réalisée dans le pipeline ajusté sur les données d'entraînement.

## Résultats sur le jeu de test

| Modèle | MAE (repas, principale) | RMSE (repas) | R² |
|---|---:|---:|---:|
| Baseline (prédiction de la moyenne d'entraînement) | 70,271 | 88,416 | -0,151 |
| Régression linéaire (`LinearRegression`) | **22,239** | **28,170** | **0,883** |
| Ridge (régression linéaire régularisée) | 22,623 | 28,545 | 0,880 |
| Arbre de décision | 46,000 | 59,710 | 0,475 |
| Forêt aléatoire | 31,825 | 41,647 | 0,745 |

## Décision

Le modèle retenu est la régression linéaire (`LinearRegression`) : elle obtient la plus faible MAE des modèles comparés, avec une erreur absolue moyenne d'environ 22 repas sur cette période de test. Sa MAE est inférieure de 48,032 repas à celle de la baseline, soit une baisse d'environ 68,4 %. Ridge, qui est une régression linéaire avec régularisation L2, obtient un résultat proche (MAE = 22,623). Le R² de 0,883 de la régression linéaire indique un bon ajustement sur ce test, sans garantir les performances futures.

Aucun seuil d'acceptation métier n'est fourni. Il faut convenir avec la cantine du niveau d'erreur acceptable, notamment selon les conséquences respectives d'un manque et d'un surplus de repas.

## Limites et précautions

- Les résultats reposent sur un seul découpage temporel de 68 jours ; une validation sur d'autres périodes est nécessaire.
- La disponibilité réelle de chaque variable au moment où la prévision est faite doit être confirmée. En particulier, météo et repas de la semaine précédente ne doivent être utilisés que si leurs valeurs sont connues à l'horizon de prévision choisi.
- Le nom d'une modalité du menu apparaît mal décodé dans le CSV (`v�g�tarien`) ; l'encodage et les valeurs de cette catégorie sont à vérifier.
- La provenance et la licence du jeu de données, les coûts de surproduction et de manque ainsi que le seuil opérationnel de tolérance ne sont pas documentés.
- La comparaison ne couvre pas de modèle saisonnier dédié ni de validation croisée temporelle.
