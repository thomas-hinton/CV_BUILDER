# CV Builder

Application web multi-utilisateurs pour créer et publier un CV en ligne, avec un backend FastAPI et une base SQLite.

## Fonctionnalités implémentées

- **Authentification** — register, login, logout via JWT (bcrypt + python-jose)
- **Profil CV** — création, lecture, modification, suppression (1 profil par compte)
- **Formations** — CRUD complet `/profiles/me/educations`
- **Expériences** — CRUD complet `/profiles/me/experiences`
- **Compétences** — CRUD complet `/profiles/me/skills`
- **Slug auto-généré** — URL propre `/cv/prenom-nom` (déduplication automatique)
- **23 tests** — schéma SQL, authentification, CRUD complet

## À venir

- Page login/register connectée à l'API
- Dashboard admin pour saisir son CV
- Page CV publique (`/cv/{slug}`)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .\.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

## Initialiser la base de données

```bash
python scripts/init_db.py        # crée data/db.db
python scripts/init_db.py --reset  # repart d'une base vide
```

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
python -m pytest -v
```

Les tests tournent sur une base SQLite en mémoire isolée — aucun fichier créé sur le disque.

## Structure

```text
.
├── main.py                  # initialisation FastAPI + routers
├── requirements.txt
├── SQL/
│   └── create_db.sql        # schéma de la base (5 tables)
├── scripts/
│   └── init_db.py           # script de création/reset de la DB
├── python/
│   ├── routers/             # auth.py, profiles.py
│   ├── schemas/             # modèles Pydantic (auth, profiles)
│   ├── services/            # logique métier (auth, profiles)
│   └── database/            # connexion SQLite partagée
├── tests/
│   ├── test_database.py     # intégrité schéma + FK
│   ├── test_auth.py         # register, login, JWT
│   └── test_crud.py         # profils, formations, expériences, compétences
├── css/
├── js/
└── assets/
```

