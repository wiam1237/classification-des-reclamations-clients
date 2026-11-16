# ADR 004 : Choix du modèle et du seuil d'alerte pour MaintAI

Date : 16/11/2026 · Auteurs : SANAA KASTASS

## Contexte
MaintAI doit prédire les pannes de machines à partir de relevés de capteurs. Une panne manquée coûte beaucoup plus cher qu'une fausse alerte : il faut donc privilégier le recall. Nous avons comparé plusieurs entraînements dans MLflow, tous sur les mêmes données (v1, 5000 relevés), pour justifier le choix.

## Options étudiées
1. Régression logistique, seuil 0.3 (réglage par défaut) : recall 0.750, precision 0.622, accuracy 0.904. Simple et rapide, mais 1 panne sur 4 reste manquée.
2. Régression logistique, `C = 0.01`, seuil 0.3 : recall 0.691, precision 0.653, accuracy 0.908. Plus de régularisation, mais le recall baisse : c'est le contraire de ce qu'il nous faut.
3. Forêt aléatoire (`--model forest`), seuil 0.3 : recall 0.728, precision 0.562, accuracy 0.886. Plus complexe et plus lourde, sans meilleur recall que la régression logistique : la forêt n'est pas meilleure ici.
4. Régression logistique, seuil 0.2 : recall 0.838, precision 0.543, accuracy 0.882. Le recall le plus élevé de tous les runs.

## Décision
Nous retenons la **régression logistique avec un seuil de 0.2** (`python -m maintai.train --threshold 0.2`). La raison principale est la contrainte du projet : manquer une panne coûte plus cher qu'une fausse alerte, et c'est ce réglage qui détecte le plus de pannes (recall 0.838).

- Identifiant du run MLflow : Run MLflow : 15352308d0b64146a618716db9e37fd9
- `data_md5` des données utilisées (v1) : `COLLER_ICI_LE_MD5_COMPLET`

## Conséquences
- Facilite : on détecte environ 84 % des pannes au lieu de 75 % avec le seuil 0.3.
- Rend plus difficile : la precision baisse (0.543), donc davantage de fausses alertes (environ une alerte sur deux est fausse) et plus d'inspections inutiles. C'est ce que nous acceptons en échange.
- À surveiller : ce choix est valable pour les données v1. Si les données changent (dérive, nouvelle version sous DVC), il faudra ré-entraîner, comparer à nouveau dans MLflow et revoir le seuil. Le run et son `data_md5` permettent de retrouver exactement le modèle et les données de cette décision.