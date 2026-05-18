# CV Builder

Application web multi-utilisateurs pour créer et publier un CV en ligne, avec un backend FastAPI et une base SQLite.

---

## Fonctionnalités livrées — version V1.0.0

Périmètre de la release **V1.0.0** : création de compte, édition d’un CV structuré et publication d’une page publique consultable par lien.

### API (FastAPI)
- **Authentification** — inscription, connexion et déconnexion ; jetons JWT signés (`bcrypt`, `python-jose`) ; clés secrètes externalisées via `.env`
- **Profil CV** — CRUD complet, un profil par compte (`/profiles`, `/profiles/me`)
- **Parcours** — formations, expériences et compétences : ajout, consultation et suppression (`/profiles/me/educations`, `/experiences`, `/skills`)
- **Publication** — slug automatique (`/cv/prenom-nom`), gestion des collisions, activation via `is_public`
- **Confidentialité** — choix d’affichage de l’email et du téléphone sur le CV public (`show_email`, `show_phone`)
- **Accès visiteur** — `GET /cv/{slug}/data` : données publiques uniquement, sans identifiants internes
- **Validation** — schémas Pydantic (email, téléphone, longueurs, mot de passe ≥ 8 caractères, cohérence des dates)
- **Qualité** — 38 tests automatisés (schéma SQL, auth, CRUD, intégration bout en bout) ; linter `ruff` sans erreur

### Interface web
- **Authentification** — pages login / register ; session via JWT en `localStorage`
- **Espace admin** — formulaire de profil et gestion des formations, expériences et compétences (ajout / suppression)
- **CV public** — rendu dynamique sur `/cv/{slug}` ; compétences regroupées par catégorie
- **Partage** — lien vers le CV public affiché dans l’admin après enregistrement du profil

---

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .\.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

## Initialiser la base de données

```bash
python scripts/init_db.py          # crée data/db.db
python scripts/init_db.py --reset  # repart d'une base vide
```

## Lancer l'application

```bash
uvicorn main:app --reload
```

Puis ouvrir :

- `http://127.0.0.1:8000/` — page login/register
- `http://127.0.0.1:8000/admin` — dashboard de saisie du CV
- `http://127.0.0.1:8000/cv/{slug}` — CV public
- `http://127.0.0.1:8000/docs` — documentation interactive FastAPI

## Lancer les tests

```bash
python -m pytest -v
```

Les tests tournent sur une base SQLite isolée en mémoire — aucun fichier créé sur le disque.

## Lancer le linter

```bash
ruff check .
```

## Architecture

```text
.
├── main.py                  # point d'entrée FastAPI + routes statiques HTML
├── requirements.txt
├── pyproject.toml           # configuration ruff
├── .env                     # modèle de config (APP_ENV, clés JWT)
├── index.html               # page login / register  →  /
├── admin.html               # dashboard édition CV  →  /admin
├── cv.html                  # CV public             →  /cv/{slug}
├── AI_REVIEWS.md            # retours des code reviews IA
├── SQL/
│   └── create_db.sql        # schéma de la base (5 tables)
├── data/
│   ├── .gitkeep
│   └── db.db                # généré localement par init_db.py (ignoré par Git)
├── scripts/
│   └── init_db.py           # création / reset de la base
├── python/
│   ├── routers/
│   │   ├── auth.py          # /auth/register, /login, /logout
│   │   ├── profiles.py      # CRUD profil, formations, expériences, compétences
│   │   └── cv.py            # GET /cv/{slug}/data (lecture publique)
│   ├── schemas/
│   │   ├── auth.py          # RegisterRequest, LoginRequest, TokenResponse
│   │   └── profiles.py      # profil, formation, expérience, compétence
│   ├── services/
│   │   ├── auth.py          # hash mot de passe, JWT, utilisateurs
│   │   └── profiles.py      # logique métier profils et parcours
│   └── database/
│       └── connection.py    # connexion SQLite partagée
├── tests/                   # 38 tests (pytest + httpx)
│   ├── test_database.py
│   ├── test_auth.py
│   ├── test_crud.py
│   └── test_integration.py
├── css/
│   └── index.css
├── js/
│   ├── auth.js
│   ├── admin.js
│   └── cv.js
└── assets/
    └── logo.png
```

---

## 🤖 Reviews externes par IA

De notre propre initiative, et dans un souci d'autocorrection et de progression, nous avons soumis le code à des IAs (Claude Sonnet 4.6, GPT-4.5) en leur demandant d'effectuer une code review de niveau senior. L'objectif n'était pas de nous laisser guider, mais d'obtenir un regard extérieur critique sur des points que nous n'aurions pas nécessairement repérés seuls.

Une **première analyse** a été réalisée avant la release **V1.0.0** : les points soulevés (sécurité JWT, XSS, fuite de données sur le CV public, validation API, tests manquants, etc.) ont **tous été corrigés** avant cette version.

Une **nouvelle analyse** sera menée dans la suite du développement, lorsque de nouvelles fonctionnalités seront ajoutées.


## Améliorations futures

- Ajouter l'édition des formations, expériences et compétences
- Déployer l'application en ligne (Render ou équivalent)
- Exporter le CV en PDF
- Proposer plusieurs templates visuels pour le CV
- Permettre l'upload d'une photo de profil
- Ajouter une version bilingue du CV (FR/EN)
- Améliorer la compatibilité mobile et responsive
- Permettre plusieurs CVs par compte (différents profils)

