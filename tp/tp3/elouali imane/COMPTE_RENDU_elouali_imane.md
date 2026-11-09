# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** …  ·  **Membres :** …  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
======================== 23 passed, 1 warning in 5.55s ========================
Résultat vérifié dans l'état actuel du projet; le résultat historique juste après la mise en place n'est pas disponible.
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

Aucun actuellement : les 23 tests passent. Un avertissement de dépréciation concerne `httpx` avec `starlette.testclient`.

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?
$ python -m streamlit run ui/app.py
Usage: streamlit run [OPTIONS] [TARGET] [ARGS]...
Try 'streamlit run --help' for help.

Error: Invalid value: File does not exist: ui\app.py


Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

`python -m streamlit` lance le module Streamlit avec l'interpréteur Python actif. La commande courte `streamlit` dépend du lanceur trouvé dans le `PATH` et peut pointer vers une autre installation Python, ou ne pas être trouvée. Dans l'environnement vérifié, le lanceur court pointe vers Python 3.13 global; l'interpréteur du projet doit être utilisé pour éviter les écarts de dépendances.

## 3. Sprint 1 : l'onglet « Données »

Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

```python
   df = charger(get_settings().data_path)

   c1, c2, c3 = st.columns(3)
   c1.metric("Relevés", len(df))
   c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
   c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

   variable = st.selectbox("Variable", FEATURES)
   tranches = pd.cut(df[variable], bins=10)
   taux = df.groupby(tranches, observed=True).failure.mean()
   taux.index = [round(i.mid) for i in taux.index]
   st.bar_chart(taux)

   df_nuage = df.assign(panne=df.failure.map({0: "non", 1: "oui"}))
   st.scatter_chart(df_nuage, x="temperature_c", y="vibration_mm_s", color="panne")
```

| Indicateur | Valeur affichée |
|---|---|
| Relevés | 5 000 |
| Taux de panne | 13,6 % |
| Température moyenne | 59,8 °C |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne augmente nettement avec la vibration : environ 2 % dans la tranche la plus basse, puis il dépasse 32 % au-dessus de 4,5 mm/s et atteint 100 % dans les tranches les plus élevées (qui contiennent peu de relevés).

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

Le message `relance` apparaît dans le terminal à chaque déplacement qui modifie un curseur. Streamlit réexécute le script de haut en bas après une interaction; `@st.cache_data` permet de réutiliser les données déjà chargées.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

`@st.cache_data` met en cache le résultat de `charger` pour un même chemin et évite de relire le CSV à chaque réexécution du script.

## 4. Sprint 2 : l'onglet « Prédiction »

Votre méthode `predict` (`maintai/client.py`) :

```python
   def predict(self, reading: dict) -> dict:
      """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
      headers = {"X-API-Key": self.api_key} if self.api_key else {}
      r = self.http.post("/v1/predict", json=reading, headers=headers)
      if r.status_code != 200:
         raise APIError(r.status_code, r.json().get("detail"))
      return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
======================== 23 passed, 1 warning in 5.55s ========================
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | Probabilité de panne : 95 % (valeur API 94,75 %); alerte au-dessus du seuil 0,3. |
| valeurs par défaut, fausse clé | Avertissement `Erreur 401 : Clé API absente ou invalide`. |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | Erreur rouge `API injoignable : uvicorn est-il lancé ?`. |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

La requête est envoyée par le client Python `httpx` côté serveur Streamlit, pas directement par le navigateur. CORS est une restriction appliquée par les navigateurs aux requêtes JavaScript inter-origines; elle ne bloque pas cette communication serveur à serveur.

## 5. Questions de compréhension

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?
   Dans la page web du TP2, le JavaScript du navigateur envoie la requête avec `fetch`. Dans Streamlit, le code Python exécuté par le serveur envoie la requête avec `MaintaiClient` et `httpx`.
2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?
   Ils injectent le `TestClient` de FastAPI dans `MaintaiClient`; les requêtes sont alors traitées directement en mémoire par l'application, sans serveur réseau séparé.
3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?
   Pour une démonstration à un client, je choisirais la page HTML + JavaScript, plus facile à présenter comme une interface web dédiée. Pour un technicien, Streamlit convient bien à un outil interne d'exploration et de prédiction, avec ses curseurs et ses graphiques. Pour un déploiement durable auprès de nombreux utilisateurs, il faudrait aussi considérer les besoins d'authentification, de rôles et d'ergonomie métier.

## 6. Le rendu Git

- Lien de la pull request : : https://github.com/wiam1237/classification-des-reclamations-clients
- Le tag `tp3` existe sur GitHub : à vérifier sur le dépôt distant; le dossier fourni ne contient pas de répertoire `.git`.
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? impossible à vérifier sans l'historique Git; compléter depuis votre terminal avant le commit.

## 7. Ce qui reste flou

- Le fichier `.env` : il n'est pas dans Git, donc je ne l'avais pas dans le dossier du TP3. J'ai dû le recréer à partir de `.env.example`. Je ne sais pas encore comment l'équipe est censée se transmettre la clé de façon sûre, sans la mettre dans le dépôt.
- La différence entre `streamlit run` et `python -m streamlit run` : j'ai compris que Python ne cherche pas les modules dans les mêmes dossiers, mais je ne vois pas encore bien comment `sys.path` est construit dans chaque cas.
- CORS : je comprends que la règle s'applique au navigateur et pas au serveur Streamlit, mais je ne suis pas sûr de bien voir ce qui se passe dans le navigateur quand la requête est bloquée.
- Le travail avec les terminaux : j'ai perdu du temps entre cmd et Git Bash (les `\\` et les `/`, `activate.bat` et `source`), et à retrouver le bon dossier.
