# Étude de conception — Détection des pannes d’équipements

**Groupe :** MaintAI · **Date :** 26/10/2026

## 1. Contexte et utilisateurs

Ce projet porte sur la prédiction des défaillances d’équipements à partir de mesures décrivant leurs conditions de fonctionnement.
 L’utilisateur principal envisagé est un technicien ou un responsable de maintenance. 
 Cette hypothèse devra toutefois être confirmée auprès du commanditaire.

## 2. Problématique et décision visée

La prédiction est conçue comme un indicateur destiné à orienter et à hiérarchiser les inspections. Elle ne constitue pas, à elle seule, une décision d’intervention. Le système produira une prédiction pour chaque observation de mesures ; la fréquence effective de collecte et d’utilisation reste à définir.

Les erreurs de prédiction sont susceptibles d’entraîner des conséquences distinctes : une panne non détectée peut retarder une inspection, tandis qu’une fausse alerte peut conduire à une vérification inutile.
 Les coûts opérationnels associés et leurs conséquences réelles ne sont pas documentés ; ils devront être évalués avec les utilisateurs concernés.

## 3. Approche retenue par sous-problème

| Sous-problème | Approche retenue | Justification |
|---|---|---|
| Charger les observations et distinguer les variables d’entrée de la variable cible | Traitement des données au moyen de pandas | Cette approche permet d’appliquer un traitement et un découpage cohérents aux différents modèles candidats. |
| Prédire la présence d’une panne (`failure`) | Apprentissage supervisé par régression logistique, arbre de décision et forêt aléatoire | Une règle déterministe nécessiterait des seuils métier documentés, qui ne sont pas disponibles. Un classifieur prédisant systématiquement la classe majoritaire est utilisé comme référence simple. |
| Comparer les modèles candidats | Évaluation sur un jeu de test indépendant des données d’entraînement | Une évaluation réalisée uniquement sur les données d’entraînement ne permettrait pas d’estimer la capacité de généralisation des modèles. |

## 4. Données

| Jeu de données | Source et licence | Volume | Présence de données personnelles |
|---|---|---:|---|
| `data/exemple_pannes.csv` | Fichier fourni avec le projet ; la source externe et la licence ne sont pas documentées | 5 000 lignes et 5 colonnes | Les colonnes examinées ne comportent pas de champ directement identifiant une personne. En l’absence d’information sur la provenance, le statut des données reste à confirmer. |

Le fichier contient les variables `temperature_c`, `vibration_mm_s`, `load_pct` et `runtime_hours`, ainsi que la cible `failure`.
 Il comprend 4 122 observations sans panne et 878 observations avec panne. Aucune valeur manquante n’a été relevée dans le fichier fourni.

## 5. Métriques, référence et critères d’acceptation

Le modèle de référence est un classifieur qui prédit systématiquement la classe majoritaire, correspondant à l’absence de panne. 
Sur le jeu de test, il obtient une accuracy de 0,824 et un rappel de 0,000.

Le rappel de la classe « panne » constitue la métrique principale, car il mesure la proportion de pannes effectivement détectées et met en évidence les pannes manquées. 
La précision et le score F1 sont également suivis afin de caractériser le compromis entre détection et fausses alertes.

Les résultats de référence sont les suivants : la régression logistique atteint un rappel de 0,847, une précision de 0,527, un score F1 de 0,649 et une accuracy de 0,839. 
L’arbre de décision obtient un rappel de 0,545 et la forêt aléatoire, un rappel de 0,693.

Aucun seuil quantitatif d’acceptation n’a été fourni. 
Il n’est donc pas possible de déclarer formellement le modèle acceptable à ce stade. Avant tout déploiement, il conviendra de définir avec les utilisateurs le rappel minimal attendu, le niveau de fausses alertes tolérable, la représentativité du jeu de validation et la procédure de revue humaine des alertes.

## 6. Architecture prévue

1. Lire le fichier CSV configuré et exclure les lignes dépourvues de valeur cible.
2. Séparer les variables d’entrée de la cible, puis constituer un découpage reproductible entre entraînement et test (80/20), aléatoire et stratifié.
3. Imputer les valeurs manquantes et mettre à l’échelle les variables numériques ; imputer et encoder les variables catégorielles.
4. Entraîner le modèle de référence et les modèles candidats au sein de pipelines scikit-learn.
5. Calculer les métriques sur le jeu de test, sélectionner le modèle présentant le meilleur rappel, puis enregistrer le pipeline dans `models/model.joblib` et les résultats dans `models/metrics.json`.

Cette architecture correspond à un processus d’entraînement hors ligne. À ce stade, aucune interface utilisateur, collecte en temps réel ou intégration dans un environnement de production n’est définie.

## 7. Choix technologiques

- **Python**, **pandas** et **NumPy** sont utilisés pour le chargement et le traitement des données.
- **scikit-learn** fournit les outils de prétraitement, les modèles et les métriques d’évaluation.
- **joblib** permet de sauvegarder le pipeline entraîné ; **pytest** est utilisé pour les tests.
- Les dépendances du projet sont répertoriées dans `requirements.txt`.

## 8. Risques, considérations éthiques et confidentialité

- Le jeu de données est déséquilibré ; une accuracy élevée, considérée isolément, pourrait donc masquer une capacité insuffisante à détecter les pannes.
- Les faux négatifs et les faux positifs peuvent avoir des conséquences opérationnelles différentes. L’arbitrage entre ces risques doit être validé avec les équipes de maintenance.
- Les performances mesurées sur un seul découpage aléatoire ne garantissent pas la généralisation à de nouvelles machines, à d’autres sites ou à des périodes différentes.
- La source, la licence, la méthode de collecte et la représentativité des données doivent être documentées avant toute réutilisation ou prise de décision opérationnelle.
- Jusqu’à la validation du modèle sur des données réelles et à la définition d’un processus de suivi, ses prédictions doivent être considérées comme une aide à la décision soumise à une vérification humaine.
- Aucun identifiant personnel n’apparaît dans les colonnes examinées. La provenance des données et les conditions de partage devront néanmoins être vérifiées avant l’utilisation d’autres jeux de données.

## 9. Limites et éléments hors périmètre

- La provenance et les conditions de collecte du jeu fourni ne sont pas documentées ; sa représentativité réelle demeure inconnue.
- L’évaluation repose sur un unique découpage fixe et ne comprend ni validation croisée, ni test temporel, ni analyse par équipement.
- Aucun seuil de décision, coût d’erreur ou critère d’acceptation métier n’a été établi.
- Le déploiement, la surveillance des dérives, le réentraînement, l’explicabilité destinée aux opérateurs et l’intégration à un système de maintenance ne relèvent pas du périmètre de ce prototype.



# Étude de conception — Prévision des repas de cantine

**Groupe :** CantineAI · **Date :** 26/10/2026

## 1. Contexte et utilisateurs

Ce projet vise à estimer le nombre de repas qui seront servis à la cantine à partir des inscriptions et des informations associées à chaque journée. L’utilisateur principal envisagé est le gestionnaire de cantine ou le responsable de la restauration scolaire. 
Ce rôle devra être confirmé auprès du commanditaire.

## 2. Problématique et décision visée

La prévision a pour objectif d’aider le personnel à ajuster les quantités de repas à préparer ainsi que les achats nécessaires. 
Elle constitue un outil d’aide à la décision et ne se substitue pas au jugement du personnel.

Une prévision est envisagée pour chaque journée de service, idéalement avant la commande des ingrédients et la préparation des repas. 
L’horaire de production de la prévision et son horizon restent à préciser.

Une sous-estimation pourrait entraîner un nombre insuffisant de repas, tandis qu’une surestimation pourrait occasionner du gaspillage et des coûts supplémentaires. 
Le coût relatif de ces erreurs devra être défini par l’équipe de la cantine.

## 3. Approche retenue par sous-problème

| Sous-problème | Approche retenue | Justification |
|---|---|---|
| Charger et préparer les observations quotidiennes | Traitement de données tabulaires avec pandas et prétraitement au moyen de scikit-learn | Cette approche permet de traiter de manière cohérente les valeurs manquantes et les variables catégorielles relatives aux menus. |
| Estimer le nombre de repas servis (`repas_servis`) | Régression supervisée avec comparaison d’une régression linéaire, de Ridge, d’un arbre de décision et d’une forêt aléatoire | Une prédiction constante fondée sur la moyenne constitue une référence utile, mais ne prend pas en compte les facteurs observés susceptibles d’influencer la fréquentation. |
| Évaluer la qualité des prévisions | Test chronologique portant sur les observations les plus récentes | Un découpage aléatoire pourrait conduire à évaluer le modèle sur des dates antérieures à certaines données d’entraînement et refléterait moins fidèlement une situation de prévision future. |

## 4. Données

| Jeu de données | Source et licence | Volume | Présence de données personnelles |
|---|---|---:|---|
| `data/cantine_repas.csv` | Fichier fourni avec le projet ; la source externe et la licence ne sont pas documentées | 340 observations, 11 colonnes, du 09/09/2024 au 19/06/2026 | Aucun champ directement identifiant n’est visible. La provenance et les modalités de collecte n’étant pas documentées, ce statut devra être confirmé avant toute nouvelle utilisation. |

La variable cible est `repas_servis`, dont les valeurs sont comprises entre 248 et 695 repas, pour une moyenne de 499. Les variables candidates sont `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances` et `repas_semaine_precedente`. La date est utilisée pour ordonner les observations lors de l’évaluation temporelle. La variable `repas_semaine_precedente` comporte 60 valeurs manquantes.

## 5. Métriques, référence et critères d’acceptation

Le problème relève de la régression. Le modèle de référence prédit une valeur constante correspondant à la moyenne calculée sur les données d’entraînement. 
Sur le test chronologique, il obtient une MAE de 70,271 repas, une RMSE de 88,416 repas et un R² de -0,151.

La MAE constitue la métrique principale. 
Exprimée en nombre de repas, elle rend directement interprétable l’écart moyen entre les prévisions et les valeurs observées. 
La RMSE et le R² sont également rapportés à titre complémentaire.

Les résultats de référence sont les suivants : la régression linéaire atteint une MAE de 22,239, une RMSE de 28,170 et un R² de 0,883 ; Ridge (régression linéaire régularisée) obtient respectivement 22,623, 28,545 et 0,880 ; l’arbre de décision, 46,000, 59,710 et 0,475 ; la forêt aléatoire, 31,825, 41,647 et 0,745.

Aucun seuil quantitatif d’acceptation n’a été défini. 
Avant toute utilisation opérationnelle, l’équipe de la cantine devra préciser l’erreur moyenne tolérable, les niveaux acceptables de surplus ou de manque, ainsi que la période de validation.

## 6. Architecture prévue

1. Lire le fichier CSV, conserver `repas_servis` comme variable cible et distinguer la date des variables d’entrée.
2. Trier les observations par ordre chronologique et réserver les plus récentes pour le test ; le prototype utilise 272 journées pour l’entraînement et 68 pour le test.
3. Imputer les valeurs numériques à l’aide de la médiane et mettre ces variables à l’échelle ; imputer les variables catégorielles, puis les encoder par one-hot encoding.
4. Entraîner le modèle de référence et les modèles de régression au sein de pipelines scikit-learn.
5. Comparer la MAE, la RMSE et le R² sur le test chronologique, puis sauvegarder le modèle retenu et les métriques.

Cette architecture décrit un prototype d’entraînement et d’évaluation hors ligne. La production quotidienne de prévisions et leur intégration au processus de commande ne sont pas encore implémentées.

## 7. Choix technologiques

- **Python**, **pandas** et **NumPy** sont utilisés pour la lecture et la préparation des données.
- **scikit-learn** fournit les outils de prétraitement, les modèles de régression et les métriques d’évaluation.
- **joblib** permet de sauvegarder les modèles ; **pytest** est utilisé pour les tests.
- Les dépendances sont déclarées dans `requirements.txt`.

## 8. Risques, considérations éthiques et confidentialité

- Les erreurs de prévision peuvent entraîner du gaspillage ou un nombre insuffisant de repas. Le compromis entre ces conséquences doit être discuté avec l’équipe de la cantine.
- La variable météorologique ne peut être utilisée que si une prévision météo est disponible au moment de la décision concernant les quantités. De même, `repas_semaine_precedente` doit être accessible à cet instant.
- Les 60 valeurs manquantes de `repas_semaine_precedente` sont imputées dans le pipeline ; cette stratégie devra être réévaluée à la lumière de données supplémentaires.
- Les données fournies ne comportent pas de champs directement identifiants. Leur origine, leur licence et leurs modalités de collecte restent néanmoins inconnues.
- La valeur « végétarien » de la variable `menu` semble présenter un problème d’encodage dans le fichier examiné. Cet encodage devra être corrigé afin d’éviter la création de catégories incohérentes.
- Jusqu’à l’évaluation de la fiabilité des prévisions et de leurs effets en conditions réelles, celles-ci doivent rester une aide à la décision vérifiée par le personnel.

## 9. Limites et éléments hors périmètre

- L’évaluation porte sur un seul bloc temporel de 68 observations et ne permet pas de caractériser la variabilité des performances selon la saison ou l’année scolaire.
- Aucune validation croisée temporelle, comparaison avec une méthode saisonnière ou optimisation des modèles n’a été réalisée.
- Les résultats dépendent des variables candidates ; leur disponibilité effective et leur qualité à l’horizon de prévision restent à confirmer.
- La source, la licence et la représentativité du jeu de données ne sont pas établies ; aucun critère d’acceptation métier n’a été fixé.
- L’interface de prévision, la connexion aux systèmes d’inscription et de commande, le suivi des erreurs, le réentraînement et l’estimation financière du gaspillage ne relèvent pas du périmètre de ce prototype.
