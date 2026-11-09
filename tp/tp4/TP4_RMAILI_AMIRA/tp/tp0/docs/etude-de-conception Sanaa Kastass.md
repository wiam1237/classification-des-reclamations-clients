# Étude de conception — Prévision des repas servis en cantine

Groupe : Sanaa Kastass · Version : prototype évalué · Date : 26/10/2026

## 1. Contexte et utilisateurs
L'outil estime le nombre de repas qui seront servis chaque jour dans une cantine scolaire. Il s'adresse principalement à la personne responsable de la planification des repas et des commandes, afin de mieux ajuster les quantités préparées.

## 2. Problème et décision
- Décision : estimer le nombre de portions à préparer et aider à planifier les achats, avec validation par le personnel de la cantine.
- Fréquence : une prévision par jour de service, à partir des informations disponibles avant la préparation.
- Coût d'une erreur : une sous-estimation peut entraîner un manque de repas; une surestimation peut provoquer du gaspillage et des coûts supplémentaires. Les prédictions sont une aide à la décision, pas une commande automatique.

## 3. Approche par sous-problème
| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| Estimer le nombre de repas servis | Régression supervisée (régression linéaire, arbre, forêt aléatoire, KNN) | Une moyenne fixe ne tient pas compte des variations liées aux inscriptions, au menu, à la météo ou aux événements. Une baseline moyenne est conservée pour mesurer l'apport réel des modèles. |
| Comparer et choisir un modèle | Évaluation sur une période chronologique tenue à l'écart | Un découpage aléatoire peut mélanger passé et futur et donner une estimation trop optimiste pour une prévision temporelle. |

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| `data/cantine_repas.csv` | Fichier fourni avec le projet; source d'origine et licence non précisées dans les documents disponibles | 340 observations quotidiennes, du 09/09/2024 au 19/06/2026; 11 colonnes | Aucune donnée directement identifiante n'apparaît dans les colonnes. Vérifier la provenance et les règles de partage du fichier avant une diffusion externe. |

La cible est `repas_servis`. Les variables utilisées sont `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances` et `repas_semaine_precedente`. La colonne `date` sert au tri chronologique et n'est pas fournie au modèle. La cible ne comporte aucune valeur manquante; `repas_semaine_precedente` en comporte 60, traitées par imputation médiane dans le prétraitement numérique.

## 5. Métriques, baseline et critères d'acceptation
- Baseline et son score : `DummyRegressor` prédisant la moyenne de l'entraînement; sur le jeu de test chronologique, MAE = 70,271 repas (RMSE = 88,416; R² = -0,151).
- Métrique principale : MAE (erreur absolue moyenne), exprimée en nombre de repas et donc interprétable directement pour la planification. Les métriques complémentaires sont la RMSE et le coefficient R².
- Critère provisoire pour ce prototype : sur les 20 % les plus récents du jeu, le modèle retenu doit avoir une MAE inférieure à celle de la baseline. La régression linéaire obtient une MAE de 22,239 repas (RMSE = 28,170; R² = 0,883) et satisfait ce critère. Aucun seuil métier maximal n'ayant été fixé avant les essais, le niveau acceptable pour une utilisation opérationnelle reste à valider avec le responsable de cantine.

## 6. Architecture prévue
Le programme charge le CSV, retire les lignes sans cible, puis sépare les observations par date : les 80 % les plus anciennes servent à l'entraînement et les 20 % les plus récentes au test. Le prétraitement impute les valeurs numériques manquantes par la médiane et les standardise; les variables catégorielles sont imputées par la modalité la plus fréquente puis encodées en indicateurs. Cinq candidats sont comparés : une baseline, une régression linéaire, un arbre de décision, une forêt aléatoire et KNN. Le meilleur modèle selon la MAE est enregistré dans `models/model.joblib`; les métriques sont enregistrées dans `models/metrics.json`.

## 7. Choix technologiques
- Python pour le code du projet.
- pandas pour lire et manipuler le fichier CSV.
- scikit-learn pour le découpage, le prétraitement, les modèles et les métriques.
- joblib et JSON pour sauvegarder le modèle entraîné et les résultats.
- pytest pour vérifier le chargement, le découpage, les candidats et l'évaluation.

## 8. Risques, éthique, confidentialité
- Les prévisions peuvent être erronées; le personnel garde la décision finale et doit pouvoir tenir compte d'informations récentes absentes du fichier.
- Les biais ou changements dans les habitudes, les menus, les inscriptions ou les conditions météo peuvent dégrader les résultats. Il faut surveiller l'erreur dans le temps et réentraîner avec des données actualisées.
- Le jeu observé ne contient pas de noms ni d'identifiants individuels. Il faut néanmoins confirmer sa provenance, sa licence et les conditions d'utilisation avant tout partage ou usage réel.
- Le modèle ne doit pas être utilisé seul pour réduire les portions disponibles ou prendre une décision affectant les élèves.

## 9. Limites et hors périmètre
Le test chronologique porte sur 68 observations seulement; ses résultats ne garantissent pas la performance future. La MAE de 22,239 repas est une moyenne et peut masquer des erreurs plus fortes certains jours. La qualité des prévisions dépend de la qualité des données et de la disponibilité des variables au moment où la prévision serait faite. Le projet ne traite ni la collecte automatique des données, ni le déploiement d'une application, ni l'optimisation des achats ou des menus. La licence et la provenance exacte des données restent à documenter.
