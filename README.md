# CV Builder

Application web d'apprentissage pour construire un CV depuis une interface simple, avec un backend FastAPI et une base SQLite.

Le projet sert aussi de support pour comprendre les relations entre :

- une page HTML/CSS/JavaScript;
- une API backend FastAPI;
- une base de donnees SQLite;
- une future authentification utilisateur.

## Etat actuel

Le projet contient actuellement :

- une application FastAPI dans `main.py`;
- une page d'accueil servie sur `/`;
- une page d'edition servie sur `/admin`;
- des fichiers statiques dans `css/`, `js/` et `assets/`;
- deux endpoints de test autour du champ `nom`;
- un schema SQL dans `SQL/create_db.sql`;
- un script de creation de base dans `scripts/init_db.py`.

L'authentification, les formulaires complets de CV, la sauvegarde des formations/experiences et l'export du CV restent a construire.

## Installation

Depuis la racine du projet :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Sous Windows PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Initialiser la base de donnees

Pour creer la base SQLite si elle n'existe pas :

```bash
python scripts/init_db.py
```

Pour repartir d'une base vide :

```bash
python scripts/init_db.py --reset
```

La base est creee dans `data/db.db`. Ce fichier est volontairement ignore par Git.

## Lancer l'application

```bash
uvicorn main:app --reload
```

Puis ouvrir :

- `http://127.0.0.1:8000/` pour la page d'accueil;
- `http://127.0.0.1:8000/admin` pour la page d'edition en cours de construction;
- `http://127.0.0.1:8000/docs` pour la documentation interactive FastAPI.

## Lancer les tests

```bash
python -m pytest
```

Ou avec le detail de chaque test :

```bash
python -m pytest -v
```

Les tests couvrent l'integrite du schema SQL et l'application des cles etrangeres.
Ils tournent sur une base SQLite en memoire — aucun fichier n'est cree sur le disque.

## Structure

```text
.
+-- main.py
+-- requirements.txt
+-- README.md
+-- SQL/
|   +-- create_db.sql
+-- scripts/
|   +-- init_db.py
+-- python/
|   +-- database/
+-- css/
+-- js/
+-- assets/
+-- data/
```
