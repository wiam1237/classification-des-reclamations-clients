# ADR 000 : Choix du modèle de prédiction de panne

Date : 09/11/2026 · Auteurs : Wiam Raoub

## Contexte
Le projet MaintAI doit prédire le risque de panne à partir de relevés de capteurs (température, vibration, charge, heures de fonctionnement). Le modèle doit être entraîné à partir de données synthétiques, exposé via une API FastAPI, puis exploitable dans une interface Streamlit et dans un client web simple.

La contrainte principale est d’obtenir un système robuste, simple à déployer et facile à maintenir, avec des performances suffisantes pour un usage de démonstration et d’évaluation technique.

## Options étudiées
1. Modèle linéaire simple : StandardScaler + LogisticRegression
   - Avantages : rapide à entraîner, facile à interpréter, faible coût mémoire/CPU, très bien adapté à des données tabulaires de taille modeste, simple à sérialiser et à intégrer dans l’API.
   - Inconvénients : moins performant sur des relations fortement non linéaires ou des interactions complexes entre variables.

2. Modèle plus complexe : arbres, forêts aléatoires ou modèles à forte capacité
   - Avantages : peut mieux capter des dépendances non linéaires et des interactions entre variables.
   - Inconvénients : plus difficile à expliquer, plus lent à entraîner et à déployer, plus coûteux à maintenir, et pas nécessaire pour un premier MVP fonctionnel.

## Décision
Nous retenons un pipeline scikit-learn composé de `StandardScaler` suivi d’un `LogisticRegression`.

Ce choix correspond aux besoins du TP : un problème de classification binaire sur des variables numériques, un jeu de données synthétique de taille raisonnable, un modèle facilement sauvegardable (`joblib`), et une API qui doit produire une probabilité de panne fiable et interprétable. Le modèle linéaire offre un bon équilibre entre performance, lisibilité et simplicité de mise en production.

## Conséquences
Cette décision facilite :
- l’entraînement rapide et reproductible,
- la sérialisation et le chargement du modèle,
- la comparaison avec une baseline simple,
- l’intégration dans FastAPI et Streamlit,
- la compréhension des facteurs influençant le risque de panne.

Elle rend plus difficile :
- la capture de relations non linéaires complexes entre capteurs,
- l’optimisation de la performance sur des cas plus réalistes ou plus bruités.

À surveiller :
- la qualité des données réelles si elles remplacent les données synthétiques,
- l’évolution du seuil de décision (`threshold`) selon les exigences métier,
- la possibilité d’évoluer vers un modèle plus complexe si les performances deviennent insuffisantes.
