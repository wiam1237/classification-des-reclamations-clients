\# ADR 004 — Choix du modèle et du seuil de décision de MaintAI



&#x20;

\*\*Auteur :\*\* ERREYYADI Ouiam



\## 1. Contexte



Le projet MaintAI vise à détecter les pannes à partir des données collectées par les capteurs. Dans ce contexte, manquer une panne représente un coût plus important que déclencher une fausse alerte. Il est donc essentiel de privilégier le rappel (\*Recall\*), tout en maintenant une attention particulière à la précision du modèle.



Les expérimentations comparées reposent sur une régression logistique avec les mêmes paramètres (\\`C=1.0\\` et un seuil de décision de \\`0.2\\`), mais utilisent deux versions différentes du jeu de données :



\- \*\*Version 1 (v1) :\*\* 5 000 relevés, identifiée par le MD5 \\`b7fec4274774842dc1f48202c6013490\\`.

\- \*\*Version 2 (v2) :\*\* 8 000 relevés, identifiée par le MD5 \\`31ef5ebb63ef2331a31dfe009ef8796a\\`.



\## 2. Options étudiées



Quatre configurations ont d'abord été évaluées sur la version v1 :



| Modèle et paramètres | Rappel | Précision | Exactitude |

|---|---:|---:|---:|

| Régression logistique, \\`C=1.0\\`, seuil \\`0.2\\` | 0.838 | 0.543 | 0.882 |

| Régression logistique, \\`C=1.0\\`, seuil \\`0.3\\` | 0.750 | 0.622 | 0.904 |

| Régression logistique, \\`C=0.01\\`, seuil \\`0.3\\` | 0.691 | 0.653 | 0.908 |

| Forêt aléatoire, seuil \\`0.3\\` | 0.728 | 0.562 | 0.886 |



La comparaison a ensuite porté sur les deux versions du jeu de données, en conservant les mêmes paramètres du modèle :



| Version / Run | Empreinte MD5 | Nombre d'exemples d'entraînement | Rappel | Précision | Exactitude |

|---|---|---:|---:|---:|---:|

| v1 / \\`hilarious-bear-847\\` | \\`b7fec4274774842dc1f48202c6013490\\` | 4 000 | 0.838 | 0.543 | 0.882 |

| v2 / \\`fun-dove-613\\` | \\`31ef5ebb63ef2331a31dfe009ef8796a\\` | 6 400 | 0.824 | 0.567 | 0.897 |



\## 3. Décision retenue



À l'issue de ces expérimentations, le choix provisoire porte sur la \*\*régression logistique avec `C=1.0` et un seuil de décision de `0.2`\*\*.



Cette configuration présente le meilleur rappel parmi les essais réalisés, avec une valeur de \*\*0.838 sur la version v1\*\*, contre \*\*0.824 sur la version v2\*\*. Ce résultat répond à l'objectif principal du projet, qui consiste à limiter le nombre de pannes non détectées.



Toutefois, la version v2 affiche une meilleure précision (0.567 contre 0.543) ainsi qu'une meilleure exactitude (0.897 contre 0.882).



Les runs de référence retenus pour cette comparaison sont :



\- \*\*Run de référence v1 :\*\* \\`hilarious-bear-847\\`, avec l'identifiant \\`c83e9ea5946b4d258932046d6b7348e6\\`.

\- \*\*Run comparatif v2 :\*\* \\`fun-dove-613\\`, avec l'identifiant \\`6f2ba3ea99e24c2bb9c6e18ba15d6a4a\\`.



Le premier a été entraîné sur la version v1, tandis que le second utilise la version v2.



\## 4. Conséquences et limites



Le modèle retenu permet d'obtenir le meilleur niveau de détection des pannes observé au cours des essais. Néanmoins, la précision de 0.543 obtenue sur la version v1 indique qu'un certain nombre de fausses alertes peuvent être générées. La version v2 présente, sur ce point, un résultat plus favorable avec une précision de 0.567.



Il convient également de souligner que les deux versions reposent sur des volumes et des compositions de données différents, ainsi que sur des découpages distincts entre les ensembles d'entraînement et de test. Les résultats obtenus ne permettent donc pas d'affirmer, à eux seuls, la supériorité générale d'une version sur l'autre.



Avant toute mise en production, le choix devra être confirmé à l'aide de données de test représentatives. Un suivi régulier du compromis entre les pannes manquées et les fausses alertes sera également nécessaire afin de vérifier que le modèle répond toujours aux exigences opérationnelles de MaintAI.

