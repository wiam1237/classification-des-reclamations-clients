# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** à compléter  ·  **Membres :** à compléter  ·  **Date :** 09/11/2026

> Les valeurs et résultats ci-dessous correspondent au projet et aux essais réalisés dans cet environnement. Les informations personnelles et les éléments Git à publier restent à compléter par le groupe.

---

## 1. Mise en place (dans `TP/TP3`)

Lors du premier lancement de `python -m pytest`, les dépendances du projet n’étaient pas encore installées. La dernière ligne indiquait :

```text
3 errors in 2.48s
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

Les trois tests de `tests/test_client.py` n’ont pas pu démarrer : leur fixture importe `fastapi.testclient`, mais FastAPI n’était pas installé dans l’environnement Python. L’erreur était `ModuleNotFoundError: No module named 'fastapi'`. Après installation des dépendances de `requirements.txt`, les tests ont pu s’exécuter.

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

L’interface MaintAI s’affiche avec le titre « MaintAI · prédiction de panne », une barre latérale contenant l’URL de l’API et le champ de clé API, ainsi que les onglets « Données » et « Prédiction ». L’onglet « Prédiction » présente les quatre champs de relevé et le bouton « Prédire ».

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

`python -m streamlit` lance Streamlit avec le module associé à l’interpréteur Python courant. `streamlit run` appelle plutôt l’exécutable trouvé dans le `PATH` du terminal ; si cet exécutable appartient à un autre environnement, la commande peut utiliser une installation différente ou ne pas être trouvée. Dans l’environnement utilisé ici, le lancement avec `python -m streamlit` a fonctionné. Les deux commandes peuvent fonctionner si elles utilisent le même environnement.

Pour cet essai, l’application a été lancée sur le port Streamlit par défaut :

```text
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

## 3. Sprint 1 : l'onglet « Données »

Code de l’onglet « Données » :

```python
with onglet_donnees:
    df = charger(get_settings().data_path)

    n_rows = len(df)
    failure_rate = df["failure"].mean()
    avg_temp = df["temperature_c"].mean()

    cols = st.columns(3)
    cols[0].metric("Relevés", n_rows)
    cols[1].metric("Taux de panne", f"{failure_rate * 100:.1f} %")
    cols[2].metric("Température moyenne", f"{avg_temp:.1f} °C")

    feature = st.selectbox("Variable à analyser", FEATURES)
    bins = pd.qcut(df[feature], q=5, duplicates="drop")
    taux_par_tranche = (
        df.assign(_tranche=bins)
        .groupby("_tranche")["failure"]
        .mean()
        .mul(100)
        .rename("taux_panne")
        .to_frame()
    )
    taux_par_tranche.index = taux_par_tranche.index.map(str)
    st.bar_chart(taux_par_tranche)

    st.scatter_chart(df, x="temperature_c", y="vibration_mm_s", color="failure")
```

Avec le fichier `data/sensors.csv` lu par défaut par l’application :

| Indicateur | Valeur affichée |
|---|---:|
| Relevés | 5000 |
| Taux de panne | 13,6 % |
| Température moyenne | 59,8 °C |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne augmente nettement avec la vibration. En divisant les relevés en cinq tranches de valeurs, il va d’environ 1,3 % dans la tranche la plus basse à environ 45,8 % dans la plus élevée. Ces valeurs décrivent le jeu de données synthétique actuel du projet.

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

À chaque interaction qui déclenche une mise à jour, Streamlit réexécute le script ; le message `relance` apparaît donc de nouveau dans le terminal. Cela illustre son modèle de réexécution réactive. Le test précis avec ce `print` n’a pas été conservé dans le fichier.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

Le décorateur met en cache le résultat de la lecture du CSV. Quand le script est réexécuté sans changement des arguments de la fonction ni du fichier concerné, Streamlit peut réutiliser les données déjà chargées au lieu de relire le fichier.

## 4. Sprint 2 : l'onglet « Prédiction »

Méthode `predict` de `maintai/client.py` :

```python
    def predict(self, reading: dict) -> dict:
        """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
        headers = None
        if self.api_key is not None:
            headers = {"X-API-Key": self.api_key}

        r = self.http.post("/v1/predict", json=reading, headers=headers)

        if r.status_code != 200:
            try:
                payload = r.json()
            except ValueError:
                payload = {"detail": r.text}
            detail = payload.get("detail") if isinstance(payload, dict) else payload
            raise APIError(r.status_code, detail)

        return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```text
23 passed, 1 warning in 3.25s
```

Le warning était un avertissement de dépréciation lié à `httpx` et `starlette.testclient`; les tests ont tous réussi.

L’API est configurée pour ce projet sur le port **8001**. Pour la démarrer avec la clé utilisée lors de l’essai :

```bash
MAINTAI_API_KEY=test-key python -m uvicorn maintai.api.main:app --reload --host 127.0.0.1 --port 8001
```

| Essai | Ce qu’affiche Streamlit |
|---|---|
| Valeurs par défaut, bonne clé (`test-key`) | La capture d’écran montre une probabilité de panne de **95 %** et le message `ALERTE : probabilité de panne 95% (seuil 30%)`. |
| Valeurs par défaut, fausse clé | L’API répond 401 ; Streamlit affiche un avertissement, par exemple `Erreur 401 : Clé API absente ou invalide`. |
| API arrêtée (Ctrl+C dans le terminal d’uvicorn) | Streamlit affiche `API injoignable : ...`, car la connexion au serveur est refusée. |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

Le navigateur communique avec Streamlit, puis c’est le code Python exécuté par Streamlit qui envoie la requête à l’API avec `MaintaiClient`. Cette requête serveur-à-serveur n’est pas soumise aux restrictions CORS du navigateur. CORS est pertinent pour l’appel direct depuis le JavaScript de la page web du TP2.

## 5. Questions de compréhension

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?

   Dans la page du TP2, le JavaScript du navigateur envoie la requête avec `fetch`. Dans Streamlit, le code Python du serveur Streamlit l’envoie via `MaintaiClient`.

2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?

   La fixture de test crée un `fastapi.testclient.TestClient` et l’injecte dans `MaintaiClient`. Ce client appelle l’application ASGI en processus, sans démarrer Uvicorn ni faire de requête à un serveur réseau séparé.

3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?

   Pour une démonstration rapide avec des graphiques et des contrôles interactifs, Streamlit est pratique et rapide à développer. Pour une interface publique destinée à des clients ou intégrée à un produit, une page HTML/JavaScript personnalisée peut offrir davantage de contrôle sur le design et l’expérience utilisateur. Le choix dépend donc du public, des contraintes et du niveau de personnalisation attendu.

## 6. Le rendu Git

- Dépôt GitHub : https://github.com/wiam1237/classification-des-reclamations-clients
- Lien de la pull request TP3 : aucune pull request TP3 n’apparaît dans le dépôt au moment de la vérification ; à ajouter après sa création.
- Le tag `tp3` existe sur GitHub : non. La recherche des références de tag `tp3` dans le dépôt ne retourne aucun résultat.
- `git status` avant le commit : non vérifiable dans cet environnement, car le dossier de travail disponible n’est pas un dépôt Git.
- Avant de rendre le travail, vérifier que les secrets (`.env`) et les artefacts générés (`data/`, `models/`) ne sont pas ajoutés par erreur au commit.

## 7. Ce qui reste flou

À compléter par les membres du groupe si une notion ou une étape du TP reste à éclaircir.
