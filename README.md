# CV Builder

Application web multi-utilisateurs pour créer et publier un CV en ligne, avec un backend FastAPI et une base SQLite.

---

## Ce qui fonctionne actuellement

### Backend
- **Authentification** — register, login, logout via JWT signé (bcrypt + python-jose)
- **Profil CV** — création, lecture, modification, suppression (1 profil par compte)
- **Formations** — ajout, lecture, suppression (`/profiles/me/educations`)
- **Expériences** — ajout, lecture, suppression (`/profiles/me/experiences`)
- **Compétences** — ajout, lecture, suppression (`/profiles/me/skills`)
- **Slug auto-généré** — URL publique `/cv/prenom-nom`, déduplication automatique si collision
- **Visibilité contrôlée** — champ `is_public` pour activer/désactiver la publication
- **Masquage email/téléphone** — l'utilisateur choisit ce qui apparaît sur son CV public
- **Endpoint public** — `GET /cv/{slug}/data` retourne uniquement les champs publics (aucun identifiant interne exposé)
- **Validation des données** — schemas Pydantic avec validation email, format téléphone, longueurs, mot de passe minimum 8 caractères
- **34 tests** — schéma SQL, authentification, CRUD, et intégration end-to-end (register → login → création profil → ajout formations/expériences/compétences → publication → lecture du CV public)
- **Linter** — `ruff` configuré, zéro erreur

### Frontend
- **Page login/register** — connexion et création de compte, JWT stocké en localStorage
- **Dashboard admin** — saisie et mise à jour du profil, ajout/suppression de formations, expériences, compétences
- **Page CV publique** — rendu dynamique du CV via `/cv/{slug}`, compétences groupées par catégorie
- **Lien vers le CV public** — affiché dans l'admin après enregistrement du profil

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
├── main.py                  # initialisation FastAPI + inclusion des routers
├── requirements.txt
├── pyproject.toml           # configuration ruff
├── SQL/
│   └── create_db.sql        # schéma de la base (5 tables)
├── scripts/
│   └── init_db.py           # script de création/reset de la DB
├── python/
│   ├── routers/             # auth.py, profiles.py, cv.py — gestion HTTP
│   ├── schemas/             # modèles Pydantic — validation des données
│   ├── services/            # logique métier — auth.py, profiles.py
│   └── database/            # connexion SQLite partagée (connection.py)
├── tests/
│   ├── test_database.py     # intégrité schéma + contraintes FK
│   ├── test_auth.py         # register, login, JWT
│   ├── test_crud.py         # profils, formations, expériences, compétences
│   └── test_integration.py  # flux end-to-end complets
├── css/
│   └── index.css            # styles partagés (CV public, auth, admin)
├── js/
│   ├── auth.js              # logique page login/register
│   ├── admin.js             # logique dashboard admin
│   └── cv.js                # rendu du CV public
└── assets/
    └── logo.png
```

---

## 🤖 Reviews externes par IA

De notre propre initiative, et dans un souci d'autocorrection et de progression, nous avons soumis le code à deux IAs (Claude Sonnet 4.6 et GPT-4.5) en leur demandant de se comporter comme des développeurs seniors effectuant une code review. L'objectif n'était pas de nous laisser guider, mais d'obtenir un regard extérieur critique pour identifier des problèmes que nous n'aurions pas nécessairement repérés seuls.

Le fichier [AI_REVIEWS.md](AI_REVIEWS.md) documente la phase actuelle du projet : les points soulevés lors de ces reviews, ce qui a déjà été corrigé en réponse, et ce qui reste à traiter avant la première release.

---

## Corrections à venir avant la release

- [ ] Sortir la clé JWT du code source — lire `SECRET_KEY` depuis `.env` 🤖
- [ ] Corriger les risques XSS dans le dashboard — échapper les champs injectés dans `innerHTML` 🤖
- [ ] Ajouter l'édition des formations, expériences et compétences
- [ ] Tests manquants — email invalide → 422, date de fin avant date de début → 422

---

## Améliorations futures

- Déployer l'application en ligne (Render ou équivalent)
- Exporter le CV en PDF
- Proposer plusieurs templates visuels pour le CV
- Permettre l'upload d'une photo de profil
- Ajouter une version bilingue du CV (FR/EN)
- Améliorer la compatibilité mobile et responsive
- Permettre plusieurs CVs par compte (différents profils)

