# Choix du modèle

**Date :** 26/10/2026 · **Groupe :** [Noms des membres]

## Contexte

Le projet MaintAI vise à prédire les pannes de machines à partir des données de capteurs afin d’aider l’équipe de maintenance à identifier les machines nécessitant une inspection. La métrique principale retenue est le **Recall**, car il est essentiel de détecter les pannes réelles et de limiter les faux négatifs, qui peuvent entraîner un arrêt de la ligne de production.

## Données et découpage

- **Fichier :** `data/exemple_pannes.csv`
- **Nombre de lignes :** 5 000 enregistrements.
- **Variable cible :** `failure` (panne ou absence de panne).
- **Colonnes utilisées :** les variables explicatives disponibles, à l’exclusion de la cible `failure`.
- **Type de tâche :** classification binaire.
- **Découpage :** aléatoire, avec une graine fixée à 42.
- **Taille du jeu de test :** 20 % des données, soit environ 1 000 enregistrements, contre 4 000 pour l’entraînement.

## Résultats sur le jeu de test

| Modèle | Recall | Accuracy | Précision | F1-score |
|---|---:|---:|---:|---:|
| Baseline | 0,000 | 0,824 | 0,000 | 0,000 |
| Régression logistique | 0,574 | 0,889 | 0,737 | 0,645 |
| Arbre de décision | **0,597** | 0,839 | 0,538 | 0,566 |
| Random Forest | 0,545 | 0,873 | 0,671 | 0,602 |
| K-Nearest Neighbors (KNN) | 0,540 | 0,878 | 0,699 | 0,609 |

## Décision

Le modèle retenu est **l’Arbre de décision (DecisionTree)**, car il obtient le meilleur Recall, avec une valeur de 0,597, soit **59,7 % des pannes réelles détectées** sur le jeu de test.

Par rapport à la baseline, dont le Recall est nul, l’Arbre de décision apporte une amélioration de 59,7 points de pourcentage. Cependant, la Régression logistique présente une meilleure Accuracy (88,9 %) et un meilleur F1-score (0,645). Le choix de l’Arbre de décision privilégie donc la détection des pannes plutôt que la performance globale.

Le modèle détecte environ six pannes réelles sur dix. Son Recall reste perfectible : le critère d’acceptation ne peut être déclaré atteint que si le seuil attendu dans l’étude de conception est inférieur ou égal à 0,597.

## Limites

Les résultats dépendent du découpage des données et de leur représentativité. Malgré une Accuracy élevée, la baseline ne détecte aucune panne, ce qui montre que cette métrique seule est insuffisante pour ce problème. L’Arbre de décision manque encore environ 40,3 % des pannes réelles. Enfin, ces résultats ne garantissent pas les mêmes performances sur des machines réelles, et une validation sur des données industrielles supplémentaires serait nécessaire.