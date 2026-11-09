# Étude de conception — Classification des réclamations clients

Groupe : [G2] · Version : finale · Date : 09/11/2026

> Les éléments entre crochets [...] sont des hypothèses à vérifier ou adapter selon le contenu réel du dépôt.

## 1. Contexte et utilisateurs

- Organisation ou situation : Un service client (entreprise de services, par ex. télécom, banque, transport ou e-commerce) reçoit chaque jour des réclamations écrites par mail, formulaire web ou réseaux sociaux. Aujourd'hui, un agent lit chaque message et choisit à la main la catégorie (facturation, livraison, produit défectueux, qualité de service, etc.) pour l'envoyer à la bonne équipe. Ce tri est lent, répétitif et varie d'un agent à l'autre.
- Utilisateur principal (un rôle précis) : le **conseiller du service client chargé du tri des réclamations entrantes** (agent de niveau 1 qui oriente chaque réclamation vers l'équipe compétente).

## 2. Problème et décision

- Décision que l'utilisateur prend avec le système : à quelle catégorie (et donc à quelle équipe) affecter cette réclamation, et si elle est à traiter en priorité. Le système propose une catégorie avec un score de confiance ; l'agent valide ou corrige.
- Fréquence : [environ 200 à 500] réclamations par jour, soit une décision par réclamation, en continu pendant les heures ouvrables.
- Conséquence d'une erreur, et pour qui :
  - Pour le **client** : sa réclamation est envoyée à la mauvaise équipe, le délai de réponse s'allonge et la frustration augmente (risque de départ).
  - Pour l'**entreprise** : temps perdu en réaffectations, non-respect des délais de traitement, perte de réputation si une réclamation urgente (fraude, facturation abusive) est traitée en retard.
  - Pour l'**agent** : retravailler des dossiers mal orientés.

## 3. Approche par sous-problème

| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| Nettoyage et normalisation du texte (minuscules, accents, ponctuation, mots vides, mélange français/darija/anglais) | Règles (expressions régulières, listes de mots vides) | C'est déjà l'approche la plus simple ; pas besoin d'apprentissage |
| Classification de la réclamation en catégories (multi-classes) | ML classique : vectorisation TF-IDF + Régression logistique ou SVM linéaire | Les règles à mots-clés seules échouent quand le vocabulaire varie et que les formulations sont libres ; le ML apprend ces variations à partir d'exemples étiquetés. Pas besoin de DL : le jeu de données est de taille modeste et TF-IDF + modèle linéaire est rapide, expliquable et peu coûteux |
| Gestion de l'incertitude (réclamations ambiguës ou hors catégorie) | Règle de seuil sur la probabilité du modèle : sous le seuil, renvoi vers validation humaine | Forcer une catégorie à chaque fois produirait des erreurs silencieuses ; un seuil simple suffit |
| Détection de l'urgence (mots comme « fraude », « débité deux fois », « coupure ») | Règles de mots-clés + signal du modèle [optionnel] | Une liste de termes critiques est transparente et facile à auditer ; un modèle dédié n'est pas justifié sans données d'urgence étiquetées |
| Rédaction automatique d'une réponse au client | **Non retenu** (LLM/RAG envisageable plus tard) | Hors du besoin actuel : le besoin est le tri, pas la réponse ; un LLM ajouterait coût, risque d'hallucination et sortie de données |

## 4. Données

| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| Réclamations clients étiquetées par catégorie [à préciser : jeu public type CFPB Consumer Complaints, Kaggle, ou jeu fourni/construit par le groupe] | [Source et licence à indiquer, ex. domaine public ou CC0 / Kaggle ; vérifier la licence exacte] | [environ X milliers de réclamations ; N catégories ; à compléter avec les chiffres du dépôt] | Oui possible : noms, téléphones, e-mails, numéros de compte ou de contrat dans le texte libre. À anonymiser avant tout usage (remplacement par des jetons du type `[NOM]`, `[TEL]`) |
| Liste de mots-clés par catégorie et termes d'urgence (pour la baseline et les règles) | Construite par le groupe | Quelques dizaines de termes | Non |

## 5. Métriques, baseline et critères d'acceptation

- Baseline et son résultat : classifieur à **règles de mots-clés** (un dictionnaire de termes par catégorie, la catégorie avec le plus de correspondances l'emporte), et à titre de repère le **classifieur majoritaire** (toujours la classe la plus fréquente). Résultat : [F1 macro ≈ 0,xx pour les règles, ≈ 0,xx pour le majoritaire ; à mesurer sur le jeu de test et à compléter].
- Métrique principale et pourquoi : **F1-score macro** (moyenne du F1 par classe), car les catégories sont probablement déséquilibrées et une simple exactitude (accuracy) masquerait de mauvaises performances sur les classes rares mais coûteuses. On suit aussi le **rappel sur les catégories critiques** (fraude, facturation) car rater une réclamation urgente coûte plus cher qu'une fausse alerte.
- Critères d'acceptation (un nombre, un jeu de données, une condition) : F1 macro ≥ **0,80** sur le jeu de test (20 % des données, jamais utilisé pour l'entraînement ni le réglage), **et** au moins **10 points de mieux** que la baseline à règles, **et** rappel ≥ 0,85 sur les catégories critiques.

## 6. Architecture prévue (après la séance 5)

```
Réclamation (texte)
        │
        ▼
[Interface web : formulaire / saisie agent]
        │
        ▼
[API backend (Python)]
   ├─► Prétraitement (nettoyage + anonymisation des données personnelles)
   ├─► Vectorisation TF-IDF
   ├─► Modèle de classification (Régression logistique / SVM)
   └─► Règles : seuil de confiance + mots d'urgence
        │
        ▼
Catégorie proposée + score + indicateur d'urgence
        │
        ▼
[Agent : valide ou corrige]  ──►  Correction enregistrée (réentraînement futur)
```

Tout s'exécute **en local / sur le serveur de l'organisation** : aucune donnée ne quitte l'organisation, car aucune API externe n'est appelée.

## 7. Choix technologiques (après la séance 5)

| Besoin | Outil | Justification |
|---|---|---|
| Langage et manipulation de données | Python, pandas | Standard pour le ML, écosystème riche, connu du groupe |
| Vectorisation et modèle de classification | scikit-learn (TF-IDF, LogisticRegression / LinearSVC) | Rapide, léger, expliquable, suffisant pour un jeu de données de taille modeste ; pas besoin de GPU |
| Prétraitement de texte | `re`, NLTK ou spaCy (modèle français) | Tokenisation, mots vides, lemmatisation pour le français |
| Évaluation | scikit-learn metrics (F1 macro, matrice de confusion) | Mesure directement les critères d'acceptation |
| Interface de démonstration | Streamlit ou Flask [selon le dépôt] | Permet à l'agent de tester une réclamation et de voir la catégorie proposée rapidement |
| Versionnement et reproductibilité | Git/GitHub, `requirements.txt` | Suivi du travail du groupe et exécution reproductible |
| Sauvegarde du modèle | joblib | Charger le modèle entraîné sans réentraîner à chaque lancement |
