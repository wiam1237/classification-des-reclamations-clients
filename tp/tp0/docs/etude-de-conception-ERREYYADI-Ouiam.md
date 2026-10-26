# Étude de conception — Détection de pannes d'équipements

Groupe : MaintAI  · Date : 26/10/2026

## 1. Contexte et utilisateurs
- **Contexte :** le projet étudie la prédiction d'une panne d'équipement à partir de mesures de fonctionnement.
- **Utilisateur principal envisagé :** technicien ou responsable de maintenance. Ce rôle est une hypothèse à confirmer avec le commanditaire.

## 2. Problème et décision
- **Décision envisagée :** utiliser la prédiction comme signal d'alerte pour prioriser l'inspection d'un équipement ; le modèle ne décide pas seul d'une intervention.
- **Fréquence :** une prédiction par observation de mesures. La fréquence réelle de collecte et d'utilisation reste à définir.
- **Coût d'une erreur :** une panne manquée peut retarder une inspection ; une fausse alerte peut entraîner une vérification inutile. Les coûts opérationnels et les conséquences réelles ne sont pas documentés et doivent être évalués avec les utilisateurs.

## 3. Approche par sous-problème
| Sous-problème | Approche | Pourquoi pas une approche plus simple |
|---|---|---|
| Charger les observations et séparer les variables d'entrée de la cible | Traitement de données avec pandas | Nécessaire pour appliquer le même traitement et le même découpage à tous les candidats. |
| Prédire la présence d'une panne (`failure`) | Apprentissage automatique supervisé : régression logistique, arbre de décision et forêt aléatoire | Une règle fixe nécessiterait des seuils métier documentés, qui ne sont pas fournis. La baseline majoritaire sert de référence simple. |
| Comparer les candidats | Évaluation sur un jeu de test indépendant de l'entraînement | Comparer sur les seules données d'entraînement ne mesure pas la généralisation. |

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---:|---|
| `data/exemple_pannes.csv` | Fourni avec le projet ; source externe et licence non documentées | 5 000 lignes, 5 colonnes | Les colonnes visibles ne contiennent pas de champ directement identifiant une personne. La provenance n'étant pas documentée, le statut complet des données reste à confirmer. |

Le fichier comporte les variables `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours` et la cible `failure`. Il contient 4 122 exemples sans panne et 878 avec panne. Aucune valeur manquante n'a été observée dans le fichier fourni.

## 5. Métriques, baseline et critères d'acceptation
- **Baseline :** classifieur qui prédit toujours la classe majoritaire (absence de panne) ; sur le jeu de test, accuracy = 0,824 et rappel = 0,000.
- **Métrique principale :** rappel de la classe panne, afin de mesurer la part des pannes effectivement détectées et de rendre visibles les pannes manquées. La précision et le F1 sont suivis en complément pour éclairer le compromis avec les fausses alertes.
- **Résultats de référence :** régression logistique : rappel = 0,847, précision = 0,527, F1 = 0,649, accuracy = 0,839. Arbre de décision : rappel = 0,545. Forêt aléatoire : rappel = 0,693.
- **Critères d'acceptation :** aucun seuil chiffré n'a été fourni. Les résultats ne permettent donc pas de déclarer formellement le modèle accepté. À définir avec les utilisateurs avant tout déploiement : rappel minimal attendu, niveau de fausses alertes tolérable, jeu de validation représentatif et procédure de revue humaine des alertes.

## 6. Architecture prévue
1. Lire le CSV configuré et retirer les lignes sans valeur de cible.
2. Séparer les variables d'entrée de la cible, puis créer un découpage entraînement/test reproductible (80/20, aléatoire et stratifié pour la classification).
3. Imputer et mettre à l'échelle les variables numériques ; imputer et encoder les variables catégorielles.
4. Entraîner la baseline et les modèles candidats dans un pipeline scikit-learn.
5. Calculer les métriques sur le jeu de test, retenir le meilleur modèle selon le rappel, puis enregistrer le pipeline dans `models/model.joblib` et les résultats dans `models/metrics.json`.

Cette architecture correspond à l'entraînement hors ligne du projet. Aucune interface utilisateur, collecte en temps réel ou intégration de production n'est actuellement définie.

## 7. Choix technologiques
- **Python**, **pandas** et **NumPy** pour le chargement et le traitement des données.
- **scikit-learn** pour les pipelines de prétraitement, les modèles et les métriques.
- **joblib** pour sauvegarder le pipeline entraîné ; **pytest** pour les tests.
- Les dépendances sont listées dans `requirements.txt`.

## 8. Risques, éthique, confidentialité
- Le jeu est déséquilibré : une bonne accuracy seule peut masquer une détection insuffisante des pannes.
- Les faux négatifs et faux positifs ont des conséquences opérationnelles différentes ; leur arbitrage doit être validé avec les équipes de maintenance.
- Les résultats d'un unique découpage aléatoire ne garantissent pas la performance sur de nouvelles machines, sites ou périodes.
- La source, la licence, la méthode de collecte et la représentativité du jeu doivent être documentées avant toute réutilisation ou décision opérationnelle.
- Les prédictions doivent rester une aide à la décision, avec vérification humaine, jusqu'à validation sur des données réelles et définition d'un processus de suivi.
- Aucun identifiant personnel n'apparaît parmi les colonnes du fichier examiné ; vérifier la provenance et les conditions de partage avant d'utiliser d'autres données.

## 9. Limites et hors périmètre
- Le jeu fourni ne documente ni sa provenance ni ses conditions de collecte ; sa représentativité réelle est inconnue.
- L'évaluation repose sur un seul découpage fixe et ne comprend ni validation croisée, ni test temporel, ni analyse par équipement.
- Aucun seuil de décision, coût d'erreur ou critère d'acceptation métier n'a été établi.
- Le déploiement, la surveillance des dérives, le réentraînement, l'explicabilité destinée aux opérateurs et l'intégration à un système de maintenance sont hors périmètre du prototype.





# Étude de conception — Prévision des repas de cantine

Groupe :  CantineAI · Version : à valider · Date : 26/10/2026

## 1. Contexte et utilisateurs
- **Contexte :** estimer le nombre de repas qui seront servis à la cantine à partir des inscriptions et des informations associées à chaque jour.
- **Utilisateur principal envisagé :** gestionnaire de cantine ou responsable de la restauration scolaire. Ce rôle est à confirmer avec le commanditaire.

## 2. Problème et décision
- **Décision envisagée :** utiliser la prévision pour aider à ajuster les quantités de repas à préparer et les achats. La prédiction ne doit pas remplacer le jugement du personnel.
- **Fréquence :** une prévision par journée de service, idéalement avant de commander les ingrédients et de préparer les repas. L'horaire exact et l'horizon de prévision restent à définir.
- **Coût d'une erreur :** une sous-estimation peut entraîner un manque de repas ; une surestimation peut causer du gaspillage et des coûts supplémentaires. Le coût relatif de ces erreurs doit être précisé par l'équipe de la cantine.

## 3. Approche par sous-problème
| Sous-problème | Approche | Pourquoi pas une approche plus simple |
|---|---|---|
| Charger et préparer les observations quotidiennes | Traitement tabulaire avec pandas et prétraitement scikit-learn | Permet de gérer de façon cohérente les valeurs manquantes et les catégories du menu. |
| Estimer le nombre de repas servis (`repas_servis`) | Régression supervisée ; comparaison d'une régression linéaire, de Ridge, d'un arbre de décision et d'une forêt aléatoire | Une moyenne constante fournit une baseline utile, mais ne tient pas compte des facteurs de fréquentation observés. |
| Évaluer la qualité de prévision | Test chronologique sur les observations les plus récentes | Un découpage aléatoire risquerait de tester sur des dates antérieures à certaines données d'entraînement et refléterait moins bien une prévision future. |

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---:|---|
| `data/cantine_repas.csv` | Fourni avec le projet ; source externe et licence non documentées | 340 observations, 11 colonnes, du 09/09/2024 au 19/06/2026 | Aucune colonne directement identifiante n'est visible. La provenance et les modalités de collecte ne sont pas documentées ; le statut doit être confirmé avant tout nouvel usage. |

La cible est `repas_servis` (248 à 695 repas, moyenne de 499). Les variables candidates sont `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances` et `repas_semaine_precedente`. La date sert à ordonner les lignes pour l'évaluation temporelle. La variable `repas_semaine_precedente` contient 60 valeurs manquantes.

## 5. Métriques, baseline et critères d'acceptation
- **Type de problème :** régression.
- **Baseline :** prédiction constante de la moyenne calculée sur l'entraînement ; sur le test temporel, MAE = 70,271 repas, RMSE = 88,416 repas et R² = -0,151.
- **Métrique principale :** MAE, exprimée en nombre de repas, afin que l'écart moyen entre prévision et valeur observée soit directement interprétable. RMSE et R² sont rapportés en complément.
- **Résultats de référence :** régression linéaire : MAE = 22,239, RMSE = 28,170, R² = 0,883 ; Ridge (régression linéaire régularisée) : MAE = 22,623, RMSE = 28,545, R² = 0,880 ; arbre de décision : MAE = 46,000, RMSE = 59,710, R² = 0,475 ; forêt aléatoire : MAE = 31,825, RMSE = 41,647, R² = 0,745.
- **Critères d'acceptation :** aucun seuil chiffré n'est défini. La cantine doit préciser l'erreur moyenne tolérable, les limites acceptables de surplus/manque et la période de validation avant toute utilisation opérationnelle.

## 6. Architecture prévue
1. Lire le fichier CSV, conserver `repas_servis` comme cible et séparer la date des variables d'entrée.
2. Trier chronologiquement et réserver les observations les plus récentes pour le test ; le prototype utilise 272 jours pour l'entraînement et 68 jours pour le test.
3. Prétraiter les colonnes numériques par imputation médiane et mise à l'échelle, et les colonnes catégorielles par imputation puis encodage one-hot.
4. Entraîner la baseline et les modèles de régression dans des pipelines scikit-learn.
5. Comparer MAE, RMSE et R² sur le test temporel, puis sauvegarder le modèle retenu et les métriques.

Cette architecture décrit un prototype d'entraînement et d'évaluation hors ligne. La production quotidienne des prévisions et leur intégration au processus de commande ne sont pas encore implémentées.

## 7. Choix technologiques
- **Python**, **pandas** et **NumPy** pour la lecture et la préparation des données.
- **scikit-learn** pour le prétraitement, les modèles de régression et les métriques.
- **joblib** pour la sauvegarde des modèles ; **pytest** pour les tests.
- Les dépendances sont déclarées dans `requirements.txt`.

## 8. Risques, éthique, confidentialité
- Les erreurs de prévision peuvent créer soit du gaspillage, soit un manque de repas ; le compromis doit être discuté avec l'équipe de cantine.
- La variable de météo ne peut être utilisée que si une prévision météo est disponible au moment où la quantité est décidée. De même, `repas_semaine_precedente` doit être disponible à cet instant.
- Les 60 valeurs absentes de `repas_semaine_precedente` sont imputées dans le pipeline ; cette stratégie doit être réévaluée avec des données supplémentaires.
- Les données fournies ne montrent pas de champs directement identifiants, mais leur origine, leur licence et leur mode de collecte restent inconnus.
- Le menu « végétarien » semble mal encodé dans le fichier affiché ; l'encodage doit être nettoyé pour éviter des catégories inconsistantes.
- Les prévisions doivent rester une aide à la décision, vérifiée par le personnel, jusqu'à ce que leur fiabilité et leurs effets sur les commandes soient évalués en conditions réelles.

## 9. Limites et hors périmètre
- L'évaluation porte sur un seul bloc temporel de 68 observations et ne mesure pas la variabilité des performances selon la saison ou l'année scolaire.
- Aucune validation croisée temporelle, comparaison à une méthode saisonnière ni optimisation des modèles n'a été menée.
- Les résultats dépendent des variables candidates ; leur disponibilité réelle et leur qualité à l'horizon de prévision sont à confirmer.
- La source, la licence et la représentativité du jeu ne sont pas établies ; aucun critère d'acceptation métier n'a été fixé.
- L'interface de prévision, la connexion aux systèmes d'inscription/commande, le suivi des erreurs, le réentraînement et l'estimation financière du gaspillage sont hors périmètre du prototype.
