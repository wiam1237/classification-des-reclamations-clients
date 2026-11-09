# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :*2* …  ·  **Membres :*SANAA KASTASS* …  ·  **Date :**9\11\2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
5 failed, 18 passed
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

Cinq tests échouent, dans deux fichiers :
- `tests/test_client.py` (3 tests) : `NotImplementedError: TP3 sprint 2 : MaintaiClient.predict`. La méthode `predict` du client n'est pas encore écrite.
- `tests/test_ui.py` (2 tests) : `IndexError: list index out of range`. La page n'affiche pas encore d'indicateur (`at.metric[0]`) ni de résultat de prédiction, donc le test ne trouve rien à lire.

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

```
ModuleNotFoundError: No module named 'maintai'
```

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

Python cherche les modules dans une liste de dossiers (`sys.path`), et cette liste dépend de la façon de lancer. Avec `streamlit run ui/app.py`, Python cherche d'abord dans le dossier du script (`ui/`), où il n'y a pas de dossier `maintai/` : l'import échoue. Avec `python -m streamlit run ui/app.py`, l'option `-m` ajoute le dossier courant (la racine du projet, `TP/TP3`) à la liste. Le dossier `maintai/` y est, donc l'import `from maintai.client import ...` fonctionne.

## 3. Sprint 1 : l'onglet « Données »

Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

```python
c1, c2, c3 = st.columns(3)
c1.metric("Relevés", len(df))
c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

variable = st.selectbox("Variable", FEATURES)

tranches = pd.cut(df[variable], bins=10)
taux = df.groupby(tranches, observed=True).failure.mean()  # observed=True : ignore les tranches vides
taux.index = [round(i.mid, 1) for i in taux.index]          # des nombres, pas du texte
st.subheader(f"Taux de panne selon {variable}")
st.bar_chart(taux)

nuage = df.assign(panne=df.failure.map({0: "non", 1: "oui"}))
st.scatter_chart(nuage, x="temperature_c", y="vibration_mm_s", color="panne")
```

| Indicateur | Valeur affichée |
|---|---|
| Relevés | 5000 |
| Taux de panne | 13.6 % |
| Température moyenne | 59.8 °C |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne augmente très fortement avec la vibration. Il part d'environ 2 % pour les vibrations les plus faibles (autour de 1 mm/s), monte à environ 33 % vers 5-6 mm/s et à environ 66 % vers 8 mm/s. Il atteint 100 % à partir de 12 mm/s. Pour la température, la hausse est plus douce : de 0 % vers 27 °C à environ 37 % vers 84-91 °C. La vibration est donc la variable qui compte le plus : ses barres montent beaucoup plus vite et plus haut que celles de la température.

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

Le mot « relance » s'affiche dans le terminal à chaque ouverture de la page et à chaque changement de widget hors formulaire (par exemple la liste déroulante « Variable » de l'onglet Données). Cela montre que Streamlit exécute à nouveau tout le script, de la première à la dernière ligne, à chaque interaction. En revanche, déplacer un curseur du formulaire de l'onglet « Prédiction » n'affiche rien : les widgets d'un `st.form` ne relancent pas le script. Seul le clic sur « Prédire » provoque une relance.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

Comme tout le script est relancé à chaque interaction, sans cache le fichier CSV serait relu à chaque clic. Avec `@st.cache_data`, la fonction n'est exécutée qu'une seule fois pour un même chemin : les appels suivants renvoient le même tableau gardé en mémoire. La page reste donc rapide.

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
================================================== 23 passed, 1 warning in 5.15s ===================================================
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | Probabilité de panne : 95 %, avec le message rouge « ALERTE : au-dessus du seuil 0.3 » |
| valeurs par défaut, fausse clé | Avertissement jaune « Erreur 401 : » suivi du message de l'API (clé absente ou invalide) |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | Message rouge « API injoignable : uvicorn est-il lancé ? » |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

CORS est une règle appliquée par le navigateur : il bloque une page qui appelle une API d'une autre origine, sauf si l'API l'autorise. Dans Streamlit, le navigateur n'appelle jamais l'API : il affiche seulement la page et envoie les clics au serveur Streamlit. C'est le serveur Streamlit, un programme Python, qui envoie la requête à l'API avec `httpx`. Cette requête ne vient pas d'un navigateur, il n'y a ni demande de permission (OPTIONS) ni en-tête Origin, comme avec curl ou le programme Java. Le port 8501 n'a donc pas besoin d'être dans la liste. La clé API reste vérifiée par l'API.

## 5. Questions de compréhension

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?
   Dans la page web du TP2, c'est le navigateur de l'utilisateur : le `fetch` JavaScript s'exécute dans le navigateur, donc il est soumis à CORS. Dans Streamlit, c'est le serveur Streamlit (Python, via `MaintaiClient` et `httpx`) qui envoie la requête ; le navigateur n'appelle jamais l'API.
2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?
   Parce que `MaintaiClient` reçoit le client de test de FastAPI (`MaintaiClient(api_key="test-key", http=client)`). La requête est envoyée directement à l'application en mémoire, sans réseau ni serveur. C'est aussi pour cela que `predict` doit utiliser `self.http.post` et non `httpx.post`.
3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?
   Pour une démonstration à un client, je choisirais la page HTML + JavaScript : on contrôle entièrement l'apparence, on peut soigner l'identité visuelle, et la page peut être hébergée simplement. Pour l'application d'un technicien, je choisirais Streamlit : elle est très rapide à écrire en Python, l'équipe n'a pas besoin de JavaScript, et elle donne directement l'exploration des données et la prédiction. Le coût est une interface moins personnalisable, ce qui compte peu pour un outil interne.

## 6. Le rendu Git

- Lien de la pull request : (à compléter après la création de la pull request)
- Le tag `tp3` existe sur GitHub : oui / non (à compléter après `git push --tags`)
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? non (le `.gitignore` du starter les exclut)

## 7. Ce qui reste flou

Je dois encore m'entraîner à réécrire seule le code de l'onglet « Données » (surtout `pd.cut` et `groupby` avec `observed=True`) et à retenir l'ordre des `except` (`APIError` avant `httpx.HTTPError`). La partie Git (pull request, relecture, tag) reste à faire.