# Étude de conception — Prévision du nombre de repas à la cantine

Groupe : Groupe 2 — RMAILI Amira · Version : brouillon (sections 4 et 5 réécrites en séance 3) · Date : 26/10/2026

## 1. Contexte et utilisateurs
- Utilisateur principal (un rôle précis) : le/la responsable de la cantine, qui commande les denrées et planifie la production.

## 2. Problème et décision
- Décision que l'utilisateur prend avec le système : combien de repas préparer demain (et commander en conséquence).
- Fréquence : chaque jour de service, en fin de journée ou tôt le matin.
- Coût d'une erreur, et pour qui : trop peu de repas → des élèves sans repas (plainte, image du service) ; trop de repas → gaspillage alimentaire et perte financière pour la cantine.

## 3. Approche par sous-problème
| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| Prévoir le nombre de repas du jour | ML : régression supervisée (tabulaire) | La moyenne ou la recopie de la semaine passée se trompent de 70 à 79 repas ; les règles écrites à la main (examens, menu, météo, inscrits) sont plus difficiles à calibrer qu'un modèle appris |
| Détecter les jours exceptionnels | Règles (calendrier : examens, sorties, veilles de vacances) | Ces informations sont connues à l'avance et fournies comme variables d'entrée |

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| `data/cantine_repas.csv` | Registre journalier de la cantine fourni dans le cadre du cours (licence : usage pédagogique ; à confirmer avec l'enseignant avant toute diffusion publique) | 340 lignes (jours de service du 09/09/2024 au 19/06/2026), 11 colonnes : `date`, `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances`, `repas_servis` (cible), `repas_semaine_precedente` | Non : ce sont des totaux par jour, sans nom ni identifiant d'élève |

Colonnes utiles : toutes sauf `date` (sert à trier) et `repas_servis` (cible). Points d'attention : 60 valeurs manquantes dans `repas_semaine_precedente` (premier jour de service après chaque période de vacances), imputées par la médiane ; les jours de vacances sont absents du fichier (les séries ont des trous). Le fichier est déjà disponible : le risque « pas de données » est écarté, mais 340 lignes restent un petit volume.

## 5. Métriques, baseline et critères d'acceptation
- Baseline et son score : toujours prédire la moyenne des repas de l'entraînement (`DummyRegressor`) : **MAE = 70,3 repas** sur le jeu de test. Référence métier : recopier le même jour de la semaine précédente : MAE = 79,0 repas (58 jours comparables).
- Métrique principale, et pourquoi : la **MAE**, en repas par jour. Elle se lit directement en repas de trop ou de moins, et traite pareillement une erreur de 10 repas, que le jour soit chargé ou calme ; la RMSE et le R² sont affichés à titre indicatif.
- Critères d'acceptation (métrique, nombre, jeu de données, condition) : **MAE ≤ 49 repas par jour (au moins 30 % sous la baseline de 70,3)**, mesurée sur le jeu de test de 20 % tenu à l'écart (les 68 derniers jours, découpage chronologique : entraînement sur le passé, test sur le futur) ; le modèle retenu doit aussi faire mieux que la recopie de la semaine précédente.

Traduction en réglages (`monprojet/config.py`) :

| Réglage | Valeur |
|---|---|
| DATA_PATH | `data/cantine_repas.csv` |
| TARGET | `repas_servis` |
| TASK | `regression` |
| MAIN_METRIC | `mae` |
| SPLIT (et TIME_COLUMN) | `chronologique` (`date`) |
| TEXT_COLUMN | `None` |

## 6. Architecture prévue
Chaîne simple : fichier CSV du registre → chargement et découpage (`data.py`) → préparation (imputation, mise à l'échelle, encodage des catégories) + modèle dans un `Pipeline` scikit-learn → évaluation et comparaison (`train.py`) → modèle sauvegardé (`models/model.joblib`) et scores (`models/metrics.json`). Une future interface (page ou script) lira le modèle pour proposer le nombre de repas du lendemain.

## 7. Choix technologiques
Python, pandas, scikit-learn, joblib, pytest, versions épinglées dans `requirements.txt` ; environnement virtuel `.venv` ; code versionné sur le dépôt GitHub du groupe. Modèles simples d'abord : un petit tableau de 340 lignes ne justifie pas de réseau de neurones.

## 8. Risques, éthique, confidentialité
- Données agrégées, sans élève identifiable : risque de confidentialité faible ; si on ajoutait un jour des données par élève (allergies, régimes), il faudrait un cadre RGPD.
- Risque principal : un modèle qui sous-estime (élèves sans repas) ; prévoir une marge de sécurité décidée par l'humain.
- Dérive : changement d'effectif, de prestataire ou de menus ; ré-entraîner régulièrement.

## 9. Limites et hors périmètre
Petit jeu de données (340 jours, test de 68 jours), peu de jours d'examens et de sorties, pas d'événements imprévus ; pas de prévision à plusieurs semaines ; pas de commande automatique des denrées ni de gestion des stocks.
