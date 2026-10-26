Auteur : wiam1237
Email : wiamraoub@gmail.com

# Étude de conception — Maintenance prédictive des équipements

Groupe : Projet maintenance prédictive · Version : finale · Date : 26/10/2026

## 1. Contexte et utilisateurs
- Utilisateur principal (un rôle précis) : responsable de maintenance industrielle / chef de maintenance d’un site de production.
- Le système aide à anticiper les pannes de machines à partir de mesures de fonctionnement, afin de planifier une intervention avant une défaillance coûteuse.
- Les utilisateurs bénéficient d’une alerte ciblée sur les équipements à risque, plutôt que d’une inspection systématique ou d’une réaction après la panne.

## 2. Problème et décision
- Décision que l'utilisateur prend avec le système : décider s’il faut programmer une intervention de maintenance ou continuer le fonctionnement normal de la machine.
- Fréquence : plusieurs fois par jour, selon la fréquence de collecte des capteurs sur les machines.
- Coût d'une erreur, et pour qui :
  - un faux négatif (machine en panne non détectée) coûte cher au responsable de maintenance et à l’entreprise : arrêt brutal, production perdue, retards logistiques, réparations urgentes ;
  - un faux positif (alerte sans panne réelle) génère des coûts de vérification et une perte de confiance, mais reste moins coûteux qu’une panne non détectée.

## 3. Approche par sous-problème
| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| Détection de pannes à partir de capteurs | Machine learning supervisé (classification binaire) | Les relations entre température, vibration, charge et durée de fonctionnement sont complexes et non linéaires ; des seuils fixes seraient trop rigides et peu robustes. |
| Sélection du modèle | Comparaison de modèles classiques (baseline, régression logistique, arbre de décision, forêt aléatoire, k-NN) | Une seule méthode ne permet pas de comparer les performances sur la vraie tâche métier et de choisir le meilleur compromis entre détection des pannes et stabilité. |
| Évaluation | Mesure sur un jeu de test séparé, avec métriques de classification | Une simple précision globale masque le risque de manquer des pannes réelles, surtout avec des classes déséquilibrées. |

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---:|---|
| `data/exemple_pannes.csv` | Données synthétiques de maintenance prédictive, sans licence spécifique indiquée dans le projet | 5 000 lignes | Non ; il ne s’agit pas de données personnelles, uniquement de mesures techniques. |

Description des colonnes :
- `temperature_c` : température de fonctionnement
- `vibration_mm_s` : niveau de vibration
- `load_pct` : charge de l’équipement
- `runtime_hours` : durée de fonctionnement
- `failure` : cible binaire (`0` = pas de panne, `1` = panne)

Le jeu est équilibré au sens du type de données, mais pas au sens de la cible : 4 122 observations sans panne et 878 pannes.

## 5. Métriques, baseline et critères d'acceptation
- Baseline et son score : baseline `DummyClassifier(strategy="most_frequent")` avec un recall de 0,000 sur le jeu de test.
- Métrique principale, et pourquoi : le `recall` est la métrique principale, car l’objectif est de minimiser les faux négatifs. En maintenance prédictive, il est plus coûteux de manquer une panne réelle que de déclencher une alerte inutile.
- Critères d'acceptation (métrique, nombre, jeu de données, condition) :
  - la métrique principale est le `recall` sur le jeu de test ;
  - le modèle retenu doit améliorer sensiblement la baseline ;
  - le critère opérationnel est un recall supérieur à 0,50 ;
  - le test est effectué sur un sous-ensemble non vu lors de l’entraînement, en découpage aléatoire stratifié 80/20.

Résultats observés sur le modèle retenu :
- `recall` : 0,597
- `accuracy` : 0,839
- `precision` : 0,538
- `f1` : 0,566

## 6. Architecture prévue
L’architecture est un pipeline de machine learning standard :
1. chargement des données depuis le CSV ;
2. sélection des variables explicatives ;
3. découpage apprentissage / test ;
4. prétraitement des variables numériques ;
5. entraînement de plusieurs modèles candidats ;
6. évaluation sur le jeu de test ;
7. sélection du meilleur modèle selon le `recall` ;
8. sauvegarde du modèle final et des métriques dans `models/model.joblib` et `models/metrics.json`.

Le pipeline est simple, reproductible et facilement extensible à d’autres modèles ou à des données plus riches.

## 7. Choix technologiques
- Langage : Python
- Bibliothèque de données : pandas
- Apprentissage automatique : scikit-learn
- Prétraitement : `SimpleImputer`, `StandardScaler`, `OneHotEncoder` (si besoin de variables catégorielles) et `ColumnTransformer`
- Modèles comparés : baseline, régression logistique, arbre de décision, forêt aléatoire, k-NN
- Sauvegarde du modèle : `joblib`
- Validation : métriques sklearn (`recall_score`, `accuracy_score`, `precision_score`, `f1_score`)

Le choix de scikit-learn est motivé par sa simplicité, sa bonne documentation, sa compatibilité avec les tests du projet et sa capacité à réaliser rapidement une comparaison robuste de modèles classiques.

## 8. Risques, éthique, confidentialité
- Risque technique : sous-performance sur de nouvelles données ou sur un autre site, en raison d’un changement de contexte de fonctionnement.
- Risque métier : certains modèles peuvent déclencher des alertes trop nombreuses ou trop peu fréquentes selon la période de production.
- Risque éthique : l’alerte automatique peut modifier les habitudes de travail et créer une dépendance décisionnelle excessive à un système de score.
- Confidentialité : les données utilisées sont techniques et non personnelles, mais il faudrait rester vigilant si des informations liées à des employés ou à des installations sensibles sont ajoutées dans de futures versions.

## 9. Limites et hors périmètre
- Le jeu de données est synthétique et ne remplace pas un vrai historique de maintenance industrielle.
- Le découpage est aléatoire stratifié, ce qui ne reflète pas forcément la logique chronologique d’un système réel où la maintenance doit être prévue avant la panne.
- La quantité de données est limitée à 5 000 lignes, ce qui peut limiter la robustesse des estimations.
- Le projet ne couvre pas la détection des causes racines, ni la planification automatique des interventions, ni l’intégration à un système de supervision industriel.
- Le modèle principal est optimisé pour le `recall`, ce qui améliore la détection des pannes mais peut réduire la précision lorsque les alertes sont nombreuses.

Le périmètre reste donc celui d’un prototype de détection de panne à partir de capteurs, avec une validation de performance avant un déploiement industriel plus large.

---

# Étude de conception — Variante cantines repas

Groupe : Projet cantines repas · Version : finale · Date : 26/10/2026

## 1. Contexte et utilisateurs
- Utilisateur principal : gestionnaire de cantine scolaire / responsable de restauration collective.
- Le système aide à prévoir le nombre de repas à préparer chaque jour afin d’éviter les ruptures de stock et les surstocks.
- Les utilisateurs bénéficient d’une meilleure planification des achats, du personnel et de la préparation.

## 2. Problème et décision
- Décision que l'utilisateur prend avec le système : estimer le nombre de repas à commander et à préparer pour la journée.
- Fréquence : quotidiennement, sur la base des données de fréquentation et du contexte de la journée.
- Coût d'une erreur, et pour qui :
  - un faux négatif (sous-estimation) entraîne des ruptures de repas, des clients insatisfaits et des coûts de gestion d’urgence ;
  - un faux positif (surestimation) crée du gaspillage alimentaire, des coûts supplémentaires et une utilisation inefficace des ressources.

## 3. Approche par sous-problème
| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| Prévision de fréquentation | Régression supervisée | Les facteurs de fréquentation varient selon le jour, le menu, la météo, les vacances et les examens, ce qui rend les seuils manuels peu fiables. |
| Sélection du modèle | Comparaison de modèles de régression (baseline, régression linéaire, Ridge, forêt aléatoire, k-NN, arbre de décision) | Une seule méthode ne permet pas de mesurer la qualité de la prévision sur la vraie tâche métier et de choisir le meilleur compromis entre précision et robustesse. |
| Évaluation | Mesure sur un jeu de test chronologique, avec métriques de régression | Une simple moyenne peut masquer des erreurs importantes sur certains jours. |

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---:|---|
| `data/cantine_repas - cantine_repas.csv` | Données de fréquentation de cantine scolaire, sans licence spécifique mentionnée dans le projet | 340 lignes | Non ; il ne s’agit pas de données personnelles, uniquement de variables de fréquentation et de contexte. |

Description des colonnes :
- `date` : date de la journée
- `jour` : jour de la semaine
- `inscrits` : nombre d’inscrits
- `menu` : type de repas
- `temperature_c` : température
- `pluie_mm` : pluie
- `examens` : présence d’examens
- `sortie_scolaire` : présence d’une sortie scolaire
- `veille_vacances` : veille de vacances
- `repas_servis` : cible quantitative (nombre de repas servis)
- `repas_semaine_precedente` : nombre de repas servis la semaine précédente

Le jeu contient 340 jours de données et la cible est quantitative : le nombre de repas servis varie selon le contexte de la journée.

## 5. Métriques, baseline et critères d'acceptation
- Baseline et son score : baseline `DummyRegressor(strategy="mean")` avec un MAE de 70,271 sur le jeu de test.
- Métrique principale, et pourquoi : le `mae` est la métrique principale, car l’objectif est de minimiser l’erreur moyenne de prévision pour organiser les achats et la production sans surstock ni rupture.
- Critères d'acceptation (métrique, nombre, jeu de données, condition) :
  - la métrique principale est le `mae` sur le jeu de test ;
  - le modèle retenu doit améliorer la baseline ;
  - le seuil de validation est un MAE nettement inférieur à la baseline ;
  - le test est effectué sur un sous-ensemble futur avec un découpage chronologique 80/20.

Résultats observés sur le modèle retenu :
- `mae` : 22,239
- `rmse` : 28,170
- `r2` : 0,883

## 6. Architecture prévue
L’architecture est un pipeline de régression standard :
1. chargement des données depuis le CSV ;
2. sélection des variables explicatives ;
3. découpage apprentissage / test selon l’ordre chronologique ;
4. prétraitement des variables numériques et catégorielles ;
5. entraînement de plusieurs modèles de régression ;
6. évaluation sur le jeu de test ;
7. sélection du meilleur modèle selon le `mae` ;
8. sauvegarde du modèle final et des métriques dans `models/model.joblib` et `models/metrics.json`.

Le pipeline est simple, reproductible et facilement extensible à de nouveaux indicateurs ou à de plus longues séries historiques.

## 7. Choix technologiques
- Langage : Python
- Bibliothèque de données : pandas
- Apprentissage automatique : scikit-learn
- Prétraitement : `SimpleImputer`, `StandardScaler`, `OneHotEncoder` et `ColumnTransformer`
- Modèles comparés : baseline, régression linéaire, Ridge, forêt aléatoire, k-NN, arbre de décision
- Sauvegarde du modèle : `joblib`
- Validation : métriques sklearn (`mean_absolute_error`, `mean_squared_error`, `r2_score`)

Le choix de scikit-learn est motivé par sa simplicité, sa documentation claire et sa capacité à comparer rapidement plusieurs modèles de régression de manière reproductible.

## 8. Risques, éthique, confidentialité
- Risque technique : sous-performance sur des périodes très atypiques ou des changements de comportement de fréquentation.
- Risque métier : erreur de prévision pouvant entraîner du gaspillage alimentaire ou une insuffisance de repas.
- Risque éthique : le système doit rester un outil d’aide à la décision, sans automatiser une gestion sans contrôle humain.
- Confidentialité : les données utilisées sont de type de fréquentation et de contexte, sans informations personnelles sensibles.

## 9. Limites et hors périmètre
- Le jeu de données couvre 340 jours seulement, ce qui peut limiter la robustesse sur des périodes exceptionnelles.
- Le découpage chronologique est adapté au besoin, mais ne capture pas nécessairement des événements imprévus comme des grèves, des fermetures ou des changements de politique de restauration.
- Le projet ne couvre pas la planification automatique des achats ni la gestion des stocks, qui sont des étapes en aval de la prévision.
- Le modèle principal est optimisé pour le `mae`, ce qui réduit l’erreur moyenne mais n’est pas forcément optimal pour des pics de demande très localisés.

Le périmètre reste donc celui d’un prototype de prévision de fréquentation de cantine, avec une validation de performance avant un déploiement plus large dans un service de restauration.
