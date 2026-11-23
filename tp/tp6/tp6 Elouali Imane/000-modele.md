# ADR 000 : [titre de la décision]

Date : [23/11/2026] · Auteurs : [elouali-imane]

## Contexte
MaintAI comporte deux composants à exécuter : une API FastAPI pour les prédictions et une interface Streamlit pour l'utilisateur. Le projet doit être déployable facilement, tout en évitant d'intégrer les données, les modèles et les secrets dans l'image Docker.

## Options étudiées

1. Construire deux images distinctes : une pour l'API et une pour Streamlit. Cette solution permet de séparer les dépendances et les responsabilités, mais nécessite de maintenir deux images.
2. Construire une image unique utilisée par deux conteneurs. Cette solution simplifie la construction et garantit un environnement commun, mais l'image contient les dépendances des deux composants.

## Décision

Nous retenons une image unique nommée `maintai:0.4.0`, utilisée par les services `api` et `ui` de Docker Compose. L'API démarre avec Uvicorn et l'interface démarre avec Streamlit grâce à une commande personnalisée. Les dépendances sont installées depuis `requirements-docker.txt`, avec des versions figées.

Les données, les modèles et les secrets sont exclus de l'image grâce à `.dockerignore`, puis fournis au lancement par des volumes Docker et des variables d'environnement.

## Conséquences
 Une seule image est à construire et à maintenir.
- Les deux services partagent les mêmes dépendances installées.
- Le modèle est monté en lecture seule dans le conteneur API.
- Les données sont montées en lecture seule dans le conteneur UI.
- La clé API est transmise au service API par le fichier `.env`.
- L'image est plus complète qu'une image dédiée à un seul service.
- Il faut veiller à ne jamais versionner le fichier `.env` ni intégrer les données et modèles dans l'image.
