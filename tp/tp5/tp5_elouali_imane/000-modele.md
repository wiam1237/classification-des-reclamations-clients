# ADR 000 : [régression logistique (C = 1.0).]

Date : [16/11/2026] · Auteurs : [Elouali Imane]
# ADR 004 : choix du modèle et du seuil d'alerte

## Contexte
MaintAI doit prévenir les pannes à partir de relevés de capteurs. Une panne manquée coûte plus cher qu'une fausse alerte, donc le recall prime, sans que la précision ne s'effondre au point de noyer les techniciens sous les fausses alertes. Les pannes sont rares (13.6 % des relevés de la v1), si bien que l'accuracy est trompeuse : le baseline « jamais de panne » atteint 0.864 d'accuracy avec un recall de 0.

## Options étudiées
Cinq runs MLflow sur les données v1 (4000 relevés d'entraînement, 1000 de test) :

1. **Régression logistique, seuil 0.3 (réglage par défaut)** : recall 0.750, precision 0.622, accuracy 0.904. Bonne précision, mais une panne sur quatre est manquée.
2. **Régression logistique, C = 0.01, seuil 0.3** : recall 0.691, precision 0.653, accuracy 0.908. Plus de régularisation, mais le recall baisse encore.
3. **Forêt aléatoire, seuil 0.3** : recall 0.728, precision 0.562, accuracy 0.886. Plus complexe, sans gain : recall et précision inférieurs à ceux de la régression logistique par défaut.
4. **Régression logistique, seuil 0.2** : recall 0.838, precision 0.543, accuracy 0.882. On attrape environ 84 % des pannes, et plus d'une alerte sur deux est une vraie panne.
5. **Régression logistique, seuil 0.1** : recall 0.919, precision 0.434, accuracy 0.826. Meilleur recall, mais moins d'une alerte sur deux est justifiée, et l'accuracy passe sous celle du baseline.

## Décision
Nous retenons la **régression logistique (C = 1.0) avec un seuil d'alerte de 0.2**.

- Run MLflow : `5c6a34a80e1646948cd8d674f07af837`
- Données : version v1, `data_md5` = `73e0b7cb3c6f795c70c3ddf970b99c15` (commit Git `c8b43ee`)

La raison principale est la contrainte du projet : une panne manquée coûte plus cher qu'une fausse alerte. Le seuil 0.2 relève nettement le recall (0.838 contre 0.750 à 0.3) tout en gardant une précision supérieure à 0.5. Le seuil 0.1 est écarté : le gain de recall (+8 points) se paie par une précision de 0.434. La forêt aléatoire est écartée car elle n'apporte rien de plus que la régression logistique, plus simple.

## Conséquences
- **Ce que cela facilite :** on détecte davantage de pannes, avec un modèle simple, rapide à entraîner et facile à expliquer. Le choix est reproductible : le run donne les paramètres et le modèle, le `data_md5` permet de retrouver les données exactes avec `git checkout c8b43ee -- data/sensors.csv.dvc` puis `dvc checkout` (ou `dvc pull`).
- **Ce que cela rend plus difficile :** plus de fausses alertes (precision 0.543) et une accuracy plus basse (0.882 contre 0.904 au seuil 0.3). Il faudra que les équipes de maintenance acceptent ce coût.
- **Ce qu'il faudra surveiller :** le jeu de test ne contient qu'environ 136 pannes ; un écart de quelques points de recall correspond à quelques pannes, donc le choix entre les seuils 0.2 et 0.1 reste fragile. Les données v2 (8000 relevés) existent déjà, mais un run entraîné dessus n'est pas directement comparable (jeu de test différent) : pour trancher, il faudra comparer sur un même jeu de test. Il faudra aussi surveiller la dérive des données : si les relevés changent, le recall peut baisser sans qu'on modifie le code, et il faudra ré-entraîner sur des données versionnées.