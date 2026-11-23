# ADR 005 : Utilisation d'une image Docker unique pour MaintAI

**Date :** 23/11/2026  
**Auteurs :** [ERREYYADI Ouiam]

## Contexte

Le projet MaintAI possède deux composants principaux : une API FastAPI pour effectuer les prédictions et une interface Streamlit pour communiquer avec l'utilisateur. Il faut pouvoir déployer ces deux composants facilement dans un environnement reproductible, tout en évitant de dupliquer inutilement les dépendances et le code.

## Options étudiées

1. **Option A : Utiliser une image Docker unique pour l'API et l'interface.**
   - Avantages : partage du même environnement Python, réduction de la duplication des dépendances et simplification de la maintenance.
   - Inconvénients : l'image contient les dépendances nécessaires aux deux composants, même si chaque conteneur n'en utilise qu'une partie.

2. **Option B : Créer deux images Docker différentes.**
   - Avantages : chaque image contient uniquement les dépendances nécessaires à son service, ce qui permet une meilleure séparation.
   - Inconvénients : nécessite deux configurations Docker et augmente la maintenance et la gestion des images.

## Décision

Nous avons choisi l'option A : utiliser une image Docker unique nommée `maintai:0.4.0` pour les services API et UI. Cette décision permet de partager le même environnement Python et de simplifier le déploiement des deux composants avec Docker Compose.

## Conséquences

Cette décision facilite la construction, la maintenance et le déploiement de l'application. Elle évite la duplication des dépendances et garantit un environnement commun aux deux services. Cependant, l'image peut être plus volumineuse qu'une image spécialisée pour chaque service. Les modèles, les données et les clés API restent fournis séparément au lancement à l'aide des volumes Docker et du fichier `.env`, afin de ne pas intégrer les données sensibles dans l'image.
