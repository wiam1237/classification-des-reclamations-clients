# Étude de conception — MaintAI : prédiction des pannes de machines

**Groupe :** ELOUALI IMANE · **Version :** Finale · **Date :** 26/10/2026

## 1. Contexte et utilisateurs

- **Utilisateur principal :** Technicien de maintenance industrielle.
- **Contexte :** MaintAI est un système de classification qui analyse les données des machines afin de prédire les risques de panne et d'aider à organiser la maintenance préventive.

## 2. Problème et décision

- **Décision que l'utilisateur prend avec le système :** Déterminer quelles machines nécessitent une vérification ou une intervention préventive.
- **Fréquence :** Après chaque collecte de données ou lors d'un contrôle périodique.
- **Coût d'une erreur, et pour qui :** Une panne non détectée peut entraîner un arrêt de production, des coûts de réparation et des pertes financières pour l'entreprise. Une fausse alerte peut provoquer une inspection inutile et mobiliser les techniciens.

## 3. Approche par sous-problème

| Sous-problème | Approche | Pourquoi pas une approche plus simple |
|---|---|---|
| Chargement et préparation des données | Règles et traitement avec Pandas | Les données doivent être structurées et préparées avant l'entraînement. |
| Prédiction des pannes | Machine Learning (classification) | Des règles fixes peuvent ne pas représenter les relations entre les variables des machines et les pannes. |
| Comparaison des modèles | Évaluation par métriques | Le score d'accuracy seul ne suffit pas pour évaluer la détection des pannes. |
| Sélection du meilleur modèle | Comparaison du recall | Le recall permet de mieux prendre en compte les pannes réelles qui ne sont pas détectées. |

## 4. Données

| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| `data/exemple_pannes.csv` | Fichier fourni avec le projet ; licence non précisée | 5 000 observations, selon la description du jeu de données | Aucune donnée personnelle identifiée dans le cadre du projet |

## 5. Métriques, baseline et critères d'acceptation

- **Baseline et son score :** Le modèle de référence prédit la classe majoritaire. Il obtient une accuracy de **82,4 %**, mais un recall de **0 %**, car il ne détecte aucune panne dans le jeu de test.
- **Métrique principale, et pourquoi :** Le **recall**, car il mesure la proportion de pannes réelles correctement détectées. Un recall faible signifie qu'un nombre important de pannes peut passer inaperçu.
- **Critères d'acceptation :** Le modèle doit dépasser le recall de la baseline et obtenir un résultat satisfaisant sur le jeu de test. Le seuil exact d'acceptation reste à définir avec les exigences du projet.
- **Résultat obtenu :** Le modèle DecisionTree obtient un recall de **59,7 %**, contre 0 % pour la baseline, soit une amélioration de **59,7 points de pourcentage**.

## 6. Architecture prévue

L'architecture du projet est organisée en plusieurs étapes :

1. Chargement du fichier CSV.
2. Préparation et séparation des données en ensembles d'entraînement et de test.
3. Entraînement de plusieurs modèles de classification.
4. Évaluation des modèles à l'aide de l'accuracy, du recall, de la précision et du F1-score.
5. Sélection du modèle présentant le meilleur recall.
6. Sauvegarde du modèle retenu dans `models/model.joblib` et des résultats dans `models/metrics.json`.

## 7. Choix technologiques

- **Python :** langage principal du projet.
- **Pandas :** manipulation et préparation des données.
- **Scikit-learn :** séparation des données, entraînement et évaluation des modèles.
- **Joblib :** sauvegarde du modèle entraîné.
- **JSON :** stockage des métriques d'évaluation.
- **Pytest :** exécution des tests pour vérifier le fonctionnement du projet.

## 8. Risques, éthique, confidentialité

- **Faux négatifs :** une panne réelle peut ne pas être détectée, ce qui peut entraîner un arrêt imprévu de la machine.
- **Faux positifs :** une machine peut être signalée à tort, entraînant une inspection inutile.
- **Qualité des données :** des données incomplètes, incorrectes ou peu représentatives peuvent réduire la fiabilité des prédictions.
- **Confidentialité :** le fichier utilisé ne semble pas nécessiter de données personnelles ; il faut néanmoins vérifier les données avant toute utilisation réelle.
- **Utilisation responsable :** les prédictions doivent aider les techniciens à prendre leurs décisions, et non remplacer entièrement leur expertise.

## 9. Limites et hors périmètre

- Le projet utilise un fichier CSV et ne collecte pas directement les données depuis des capteurs en temps réel.
- Les performances dépendent de la qualité et de la représentativité du jeu de données utilisé.
- Le recall obtenu par DecisionTree est de 59,7 % : environ 40,3 % des pannes réelles du jeu de test ne sont donc pas détectées.
- Le modèle doit être évalué sur des données industrielles réelles avant toute utilisation opérationnelle.
- La maintenance automatique, la connexion à des équipements industriels et le déploiement en production ne font pas partie du périmètre actuel.
