# Choix du modèle

Date : [26/10/2026] · Groupe : [Sanaa Kastass]

## Contexte
Le projet prédit le nombre de repas servis à la cantine afin d'aider à ajuster la préparation des repas. La MAE est la métrique principale, car elle mesure directement l'erreur moyenne en nombre de repas et reste facile à interpréter.

## Données et découpage
Le jeu utilisé est `data/cantine_repas.csv` (340 lignes), avec `repas_servis` comme cible. Les 9 variables d'entrée sont `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances` et `repas_semaine_precedente`; la colonne `date` sert au tri chronologique et n'est pas utilisée comme variable. Le découpage est chronologique : 272 lignes pour l'entraînement et les 68 jours les plus récents pour le test (20 %).

## Résultats sur le jeu de test

| Modèle | Métrique principale | Autres métriques |
|---|---|---|
| Baseline (DummyRegressor) | MAE : 70,271 repas | RMSE : 88,416 ; R² : -0,151 |
| Régression linéaire | MAE : 22,239 repas | RMSE : 28,170 ; R² : 0,883 |
| Arbre de décision | MAE : 42,010 repas | RMSE : 54,766 ; R² : 0,558 |
| Forêt aléatoire | MAE : 31,825 repas | RMSE : 41,647 ; R² : 0,745 |
| K plus proches voisins (KNN) | MAE : 36,212 repas | RMSE : 46,037 ; R² : 0,688 |

## Décision
Le modèle retenu est la régression linéaire, qui obtient la plus faible MAE. Elle bat la baseline de 48,032 repas de MAE (environ 68,4 % de réduction de l'erreur, de 70,271 à 22,239). Aucun seuil d'acceptation chiffré n'étant indiqué dans l'étude de conception, il n'est pas possible de conclure formellement sur ce critère; le modèle satisfait toutefois le critère de comparaison défini par le projet, qui est de battre la baseline.

## Limites
Le jeu de test ne contient que 68 lignes, et ces résultats mesurent la performance sur cette période chronologique, pas une garantie pour les périodes futures. La MAE moyenne peut masquer des erreurs plus importantes sur certains jours ou menus. La première valeur manquante de `repas_semaine_precedente` est imputée par le prétraitement; les performances dépendent aussi de la qualité et de la représentativité du fichier fourni.
