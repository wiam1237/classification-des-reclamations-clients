# ADR 001 : Sécurisation de l'API MaintAI

Date : 02/11/2026 · Auteurs : ERREYYADI Ouiam

## Contexte

L'API MaintAI expose un endpoint de prédiction accessible par des requêtes HTTP. Il est nécessaire de protéger les routes contre les accès non autorisés et de limiter les origines pouvant communiquer avec l'API depuis un navigateur.

## Options étudiées

1. **Authentification par clé API dans l'en-tête HTTP** : simple à mettre en place avec FastAPI, elle permet de transmettre la clé dans `X-API-Key`. Elle nécessite toutefois de protéger la clé et de la renouveler régulièrement.

2. **Authentification sans protection** : facilite les appels à l'API, mais permet à n'importe quel client d'accéder aux prédictions.

3. **Politique CORS ouverte (`*`)** : facilite les tests depuis différentes origines, mais ne limite pas les sites autorisés à effectuer des requêtes depuis un navigateur.

4. **Politique CORS avec liste d'origines autorisées** : renforce le contrôle des communications, mais nécessite de configurer chaque origine utilisée.

## Décision

Nous avons retenu l'authentification par clé API transmise dans l'en-tête `X-API-Key`, avec une vérification centralisée par `require_api_key()` et une protection de toutes les routes `/v1` via `Depends()`.

La clé est stockée dans la variable d'environnement `MAINTAI_API_KEY`.

Nous avons également retenu une politique CORS restrictive basée sur une liste explicite d'origines autorisées, configurée par `MAINTAI_CORS_ORIGINS`. Pour notre interface de test, l'origine autorisée est `http://127.0.0.1:5501`.

Ces choix répondent au besoin de sécuriser l'accès à l'API tout en permettant à l'interface web de communiquer avec elle.

## Conséquences

- Les requêtes avec une clé absente ou invalide sont rejetées avec le code HTTP **401**.
- Les données non conformes au schéma sont rejetées avec le code HTTP **422**.
- Seules les origines déclarées dans la configuration CORS sont autorisées par le navigateur.
- La configuration des clés et des origines est centralisée dans le fichier `.env`, qui ne doit pas être ajouté au dépôt Git.
- L'ajout d'une nouvelle interface nécessite de déclarer son origine dans la configuration CORS.
- En production, il faudra prévoir HTTPS, la rotation des clés et un mécanisme d'authentification plus robuste.