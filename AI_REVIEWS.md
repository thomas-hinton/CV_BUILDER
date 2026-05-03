← [Retour au README](README.md)

# 🤖 Reviews externes par IA

Ce projet est réalisé dans le cadre du cours **Web Programming**, dont les compétences visées sont :

1. Mettre en place un service web sur une architecture 3-tiers
2. Mettre en place un site graphique permettant la manipulation de données avec gestion de rôles utilisateurs
3. Livrer une application web à un client (documentation, versioning et démonstration de déploiement)

Dans cette optique — et avant de présenter notre travail — nous avons soumis le projet, dans son état actuel, à deux intelligences artificielles auxquelles nous avons demandé de se comporter comme des développeurs seniors effectuant une code review sur un travail étudiant :

- 🟣 **Claude Sonnet 4.6** (Anthropic)
- 🟢 **GPT-4.5** (OpenAI / Codex)

L'objectif était d'obtenir un regard extérieur critique sur nos choix techniques, les problèmes de sécurité, la qualité du code et les pratiques à corriger — afin de nous préparer à défendre et livrer notre travail dans les meilleures conditions.

---

## ⚠️ Ce qui a été soulevé

### Sécurité

- ⚠️ **Clé JWT codée en dur** — tant que `SECRET_KEY` est dans le code source, n'importe qui qui voit le dépôt peut théoriquement signer des tokens valides. Elle doit être externalisée dans une variable d'environnement (fichier `.env`, non versionné).

- **JWT en localStorage** — choix simple et adapté à l'apprentissage, mais des cookies `HttpOnly` seraient préférables pour une application en production : ils ne sont pas accessibles depuis JavaScript, ce qui résiste mieux aux attaques XSS.

- ⚠️ **XSS dans le dashboard** — des données utilisateur sont injectées dans `innerHTML` sans échappement dans les listes de formations, expériences et compétences. Un attaquant qui contrôle ces données pourrait injecter du code JavaScript arbitraire. À corriger en échappant tous les champs avant injection dans le DOM.

### Architecture et protection des routes

- **Page `/admin` protégée côté client uniquement** — la page HTML peut être chargée sans authentification ; c'est le JavaScript qui redirige si aucun token n'est présent. Les routes API restent bien protégées côté serveur, mais la page elle-même est accessible sans contrôle. Ce comportement est acceptable pour un projet pédagogique, à condition d'en être conscient.

### Base de données

- **SQLite** — adapté au développement local, mais PostgreSQL est préférable pour un déploiement public avec plusieurs utilisateurs simultanés (gestion des accès concurrents, performances, fiabilité).

- **Pas de migration de base de données** — toute modification du schéma SQL nécessite actuellement un `--reset` qui supprime toutes les données existantes. Un outil de migration (Alembic par exemple) permettrait d'évoluer le schéma sans perte de données.

---

## 🛠️ Mesures adoptées suite aux reviews

### ✅ Déjà corrigé

| Problème identifié | Ce qui a été fait | Commit |
|---|---|---|
| **Fuite de champs internes dans le CV public** — `GET /cv/{slug}/data` renvoyait toute la ligne SQL, exposant `user_id`, `id_user_page`, `is_public`, etc. Ces identifiants internes n'ont aucune utilité pour le visiteur mais révèlent la structure de la base. | Construction explicite d'un dictionnaire de réponse ne contenant que les champs publics autorisés. Test automatisé ajouté : si quelqu'un réintroduit la fuite par erreur, le test échoue immédiatement. | [`3a11091`](https://github.com/thomas-hinton/CV_BUILDER/commit/3a11091) |
| **Validation du mot de passe inexistante côté serveur** — la limite de 8 caractères n'était indiquée que dans le placeholder HTML. Un appel direct à l'API (sans passer par le formulaire) permettait de créer un compte avec un mot de passe d'un seul caractère. | Validateur Pydantic ajouté dans `RegisterRequest` : rejette avec une erreur 422 tout mot de passe de moins de 8 caractères, avec message d'erreur en français. Test automatisé ajouté. | [`77f89a1`](https://github.com/thomas-hinton/CV_BUILDER/commit/77f89a1) |
| **Injection XSS via le lien du CV public** — le slug était injecté dans le DOM via `innerHTML`. Si le slug contenait du HTML malveillant (ex. `<img src=x onerror=alert(1)>`), le navigateur l'aurait exécuté. | Remplacement de `innerHTML` par `document.createElement()` + `textContent`, qui traite toujours la valeur comme du texte brut — toute injection est rendue inoffensive. | [`11c373f`](https://github.com/thomas-hinton/CV_BUILDER/commit/11c373f) |

### 🚧 Mesures adoptées à réaliser

Les deux points suivants, directement soulevés par les reviews, sont jugés critiques et seront corrigés avant la première release :

- **Sortir `SECRET_KEY` du code** — lire depuis `.env` via `python-dotenv`. Une clé secrète dans le dépôt Git est accessible à n'importe qui ; c'est la correction de sécurité la plus urgente.
- **Corriger le XSS dans le dashboard** — ajouter `esc()` dans `admin.js` pour tous les champs injectés dans le DOM. Sans ça, un utilisateur peut injecter du code malveillant qui s'exécute dans le navigateur.
