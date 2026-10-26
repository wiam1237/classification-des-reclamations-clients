# Choix du modèle

Date : 26/10/2026 · Groupe : Groupe 2 — RMAILI Amira

## Contexte
La cantine d'un établissement scolaire doit prévoir chaque jour le nombre de repas à préparer : trop peu, des élèves ne mangent pas ; trop, la nourriture est gaspillée. Le problème est une **régression** (cible : `repas_servis`). La métrique principale est la **MAE** (erreur absolue moyenne, en repas par jour), choisie parce qu'elle se lit directement en « nombre de repas de trop ou de moins » et que l'écart d'un repas coûte autant à 10 repas qu'à 100 (section 5 de l'étude de conception).

## Données et découpage
- Fichier : `data/cantine_repas.csv` — 340 jours de service (du 09/09/2024 au 19/06/2026), 11 colonnes.
- Variables utilisées (9) : `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances`, `repas_semaine_precedente`. La date sert uniquement à trier ; la cible est exclue des entrées.
- Valeurs manquantes : `repas_semaine_precedente` est vide 60 fois (première semaine après chaque période de vacances) ; elle est remplacée par la médiane dans le pipeline, calculée sur l'entraînement.
- Découpage **chronologique** : les 80 % les plus anciens pour l'entraînement (272 jours, 09/09/2024 → 24/02/2026), les 20 % les plus récents pour le test (68 jours, 25/02/2026 → 19/06/2026). Le modèle apprend le passé et est testé sur le futur. Graine : 42.

## Résultats sur le jeu de test

| Modèle | MAE (↓, principale) | Autres métriques (RMSE · R²) |
|---|---|---|
| Baseline (toujours la moyenne de l'entraînement) | 70,271 | 88,416 · −0,151 |
| Baseline « même jour la semaine précédente »¹ | 78,966 | — |
| **Régression linéaire** | **22,239** | 28,170 · 0,883 |
| Ridge (alpha = 1) | 22,623 | 28,545 · 0,880 |
| Forêt aléatoire (200 arbres) | 31,825 | 41,647 · 0,745 |
| Gradient boosting (histogrammes) | 39,015 | 51,049 · 0,616 |

¹ Calculée à part sur les 58 jours du test où la valeur de la semaine précédente existe (10 jours n'en ont pas) ; sur ces mêmes jours, la baseline « moyenne » obtient 72,3. C'est la référence « métier » : ce que ferait quelqu'un qui recopie la semaine passée.

Tous les modèles sont entraînés sur les mêmes 272 jours et mesurés sur les mêmes 68 jours.

## Décision
**Modèle retenu : la régression linéaire** (MAE 22,2 repas, soit environ 4 % de la moyenne de 525 repas par jour sur la période de test).

- Elle bat la baseline de **48 repas par jour** (70,3 → 22,2, soit **−68 %**), et la recopie de la semaine précédente de 57 repas.
- **Critère d'acceptation (section 5) : atteint.** Le critère était MAE ≤ 49 repas (au moins 30 % sous la baseline) sur les 68 derniers jours, découpage chronologique : 22,2 ≤ 49.
- Pourquoi un modèle simple gagne : la demande dépend surtout de relations quasi linéaires (nombre d'inscrits, vendredi/couscous plus fréquenté, examens qui vident la cantine d'environ 120 repas). Avec seulement 272 jours d'entraînement, la forêt et le gradient boosting sur-apprennent (MAE 32 et 39) ; la régression linéaire et Ridge sont à égalité (écart de 0,4 repas, non significatif), et on garde la plus simple et la plus facile à expliquer.

## Limites
- **Petit jeu de test** : 68 jours (≈ 14 semaines). Un écart de 0,4 repas entre linéaire et Ridge ne veut rien dire ; seul l'écart avec les modèles à arbres est net.
- **Test utilisé pour choisir** : on a comparé 4 modèles sur le même test et gardé le meilleur ; le score de 22,2 est donc légèrement optimiste. Aucun réglage d'hyperparamètres n'a été fait pour limiter ce biais. Une validation croisée temporelle donnerait une estimation plus honnête.
- **Cas rares mal couverts** : seulement 10 jours d'examens et 4 sorties scolaires dans le test ; les journées exceptionnelles (grève, panne, événement) n'existent pas dans les données.
- **Une seule saison complète en vue** : pas assez d'années pour apprendre une saisonnalité fine ; un changement de l'effectif ou du prestataire ferait dériver le modèle.
- `repas_semaine_precedente` suppose que l'historique de la semaine passée est disponible le jour de la prédiction (c'est le cas en pratique) ; les prévisions météo, elles, sont incertaines à plusieurs jours.
- Le modèle prédit un nombre moyen de repas : il ne dit pas combien prévoir en marge de sécurité pour éviter une rupture.
