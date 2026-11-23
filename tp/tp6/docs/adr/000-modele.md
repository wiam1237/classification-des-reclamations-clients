# ADR 000 : Séparer l'image Docker des données, du modèle et des secrets

Date : 23/11/2026 · Auteurs : Wiam RAOUB  **Heure :** 11:36

## Contexte
MaintAI doit pouvoir être construit et exécuté de façon reproductible dans des conteneurs Docker, sans inclure les données locales, le modèle entraîné ou la clé API dans l'image. Le modèle et les données peuvent évoluer indépendamment du code, et la clé API doit rester secrète.

## Options étudiées
1. Inclure le code, les dépendances, les données, le modèle et la clé API dans une seule image : lancement simple, mais image liée à des données et à un modèle précis ; toute mise à jour ou rotation de clé exige de reconstruire et redistribuer l'image.
2. Construire une image avec le code et ses dépendances, puis fournir le modèle et les données par volumes et les secrets par configuration au lancement : image réutilisable et secrets séparés, mais lancement nécessitant les fichiers et variables appropriés.

## Décision
Retenir l'option 2. L'image Python 3.11-slim contient le code MaintAI et les dépendances épinglées de `requirements-docker.txt` ; Docker Compose monte `models/` et `data/` en lecture seule et fournit la clé API via `.env`.

## Conséquences
Une même image peut être réutilisée avec différents modèles, jeux de données et clés sans être reconstruite. Les fichiers nécessaires doivent exister sur la machine avant le lancement, et `.env`, `models/` et `data/` doivent rester exclus de l'image ; la clé ne doit pas être partagée ni versionnée. Compose lance l'API sur le port interne 8000 (publié sur 8082 sur l'hôte) et l'interface Streamlit sur 8501 ; l'interface appelle l'API avec le nom de service `api`.
