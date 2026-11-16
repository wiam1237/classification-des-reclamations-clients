# ADR 000 : hoix du modèle et du seuil de décision pour MaintAI

Date : [16/11/2026] · Auteurs : [RMAILI AMIRA]

## Contexte
MaintAI doit prédire les pannes de machines à partir de relevés de capteurs. Une panne manquée coûte plus cher qu'une fausse alerte : il faut donc privilégier le recall, sans que la precision ne s'effondre.

## Options étudiées
Quatre entraînements ont été comparés dans MLflow, sur la v1 des données (5000 relevés, data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15) :

| Option | recall | precision | accuracy |
|---|---|---|---|
| 1. Régression logistique, C=1, seuil 0.3 | 0.750 | 0.622 | 0.904 |
| 2. Régression logistique, C=0.01, seuil 0.3 | 0.691 | 0.653 | 0.908 |
| 3. Régression logistique, C=1, seuil 0.2 | 0.838 | 0.543 | 0.882 |
| 4. Forêt aléatoire, seuil 0.3 | 0.728 | 0.562 | 0.886 |

1. Option 1 : bon équilibre, mais 25 % des pannes restent manquées.
2. Option 2 : la régularisation forte améliore la precision, mais dégrade le recall.
3. Option 3 : le meilleur recall, au prix d'une precision plus basse.
4. Option 4 : modèle plus complexe, pourtant moins bon que l'option 1 sur les trois métriques.

## Décision
Nous retenons la régression logistique (C=1) avec un seuil de 0.2 (option 3). Elle donne le meilleur recall (0.838), ce qui répond à la contrainte principale : manquer une panne coûte plus cher qu'une fausse alerte.

Run MLflow : f1b4792b253b4ded9c759d34a2a9dbea
Données : data/sensors.csv, version v1, data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15 (commit DVC « Données v1 », 1491c38).

## Conséquences
- Facilité : moins de pannes non détectées (recall 0.838 contre 0.750 avec le seuil 0.3).
- Accepté en échange : plus de fausses alertes (precision 0.543 contre 0.622) et une accuracy un peu plus basse (0.882).
- La forêt aléatoire n'apporte rien ici : le seuil a plus d'effet que le choix du modèle.
- À surveiller : le coût réel des fausses alertes pour la maintenance, et la dérive des données. Un run sur la v2 (8000 relevés) donne des scores proches (recall 0.741 au seuil 0.3), mais son jeu de test est différent, donc non strictement comparable.
- Pour auditer ou ré-entraîner : git checkout <commit> -- data/sensors.csv.dvc puis dvc checkout ramène les données, et le requirements.txt du run donne les versions exactes (scikit-learn 1.8.0).