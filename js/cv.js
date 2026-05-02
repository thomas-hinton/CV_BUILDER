/*
 * Public CV page — fetches /cv/{slug}/data and renders the CV.
 *
 * DISCLAIMER: This file was written with assistance from GitHub Copilot
 * (Claude Sonnet 4.6) and reviewed by the project author.
 */

function slug() {
    // Extract slug from URL path: /cv/{slug}
    return window.location.pathname.split("/cv/")[1]?.replace(/\/$/, "");
}

function esc(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function formatDate(d) {
    if (!d) return "En cours";
    const [y, m] = d.split("-");
    return `${m}/${y}`;
}

// ---------------------------------------------------------------------------
// Render helpers
// ---------------------------------------------------------------------------

function renderProfile(p) {
    const name = `${esc(p.prenom)} ${esc(p.nom)}`;
    const email  = p.email  ? `<div class="info-item"><span>Email</span>${esc(p.email)}</div>` : "";
    const tel    = p.tel    ? `<div class="info-item"><span>Téléphone</span>${esc(p.tel)}</div>` : "";
    const adresse = p.adresse ? `<div class="info-item"><span>Adresse</span>${esc(p.adresse)}</div>` : "";

    return `
        <div class="header">
            <div class="photo-wrapper">
                <div class="photo">Photo<br>de profil</div>
            </div>
            <div class="identity">
                <h1>${name}</h1>
                <div class="info-grid">
                    ${email}${tel}${adresse}
                </div>
            </div>
        </div>`;
}

function renderFormations(formations) {
    if (!formations.length) return "";
    const items = formations.map(f => `
        <div class="entry">
            <div class="entry-header">
                <span class="entry-name">${esc(f.nom_formation)}</span>
                <span class="entry-dates">${formatDate(f.date_debut)} → ${formatDate(f.date_fin)}</span>
            </div>
            <p class="entry-meta">${esc(f.organisme_formation)}</p>
            ${f.description_formation ? `<p class="entry-description">${esc(f.description_formation)}</p>` : ""}
            ${f.diplome_url ? `<a class="diploma-link" href="${esc(f.diplome_url)}" target="_blank" rel="noopener">Voir le diplôme</a>` : ""}
        </div>`).join("");
    return `
        <div class="section">
            <h2 class="section-title">Formations</h2>
            <div class="timeline">${items}</div>
        </div>`;
}

function renderExperiences(experiences) {
    if (!experiences.length) return "";
    const items = experiences.map(e => `
        <div class="entry">
            <div class="entry-header">
                <span class="entry-name">${esc(e.nom_experience)}</span>
                <span class="entry-dates">${formatDate(e.date_debut)} → ${formatDate(e.date_fin)}</span>
            </div>
            ${e.organisme_experience ? `<p class="entry-meta">${esc(e.organisme_experience)}${e.lieu_experience ? " — " + esc(e.lieu_experience) : ""}</p>` : ""}
            ${e.description_experience ? `<p class="entry-description">${esc(e.description_experience)}</p>` : ""}
        </div>`).join("");
    return `
        <div class="section">
            <h2 class="section-title">Expériences professionnelles</h2>
            <div class="timeline">${items}</div>
        </div>`;
}

function renderSkills(skills) {
    if (!skills.length) return "";
    // Group by category
    const groups = {};
    for (const s of skills) {
        const cat = s.categorie || "Autres";
        if (!groups[cat]) groups[cat] = [];
        groups[cat].push(s);
    }
    const tags = Object.entries(groups).map(([cat, items]) => `
        <div style="margin-bottom:14px">
            <p style="margin:0 0 8px;font-weight:600;color:var(--muted);font-size:0.85rem;text-transform:uppercase">${esc(cat)}</p>
            <div style="display:flex;flex-wrap:wrap;gap:8px">
                ${items.map(s => `
                    <span style="padding:5px 14px;background:var(--primary-soft);color:#1d4ed8;border-radius:999px;font-size:0.9rem;font-weight:600">
                        ${esc(s.nom_skill)}${s.niveau ? " · " + esc(s.niveau) : ""}
                    </span>`).join("")}
            </div>
        </div>`).join("");
    return `
        <div class="section">
            <h2 class="section-title">Compétences</h2>
            ${tags}
        </div>`;
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", async () => {
    const s = slug();
    if (!s) {
        document.getElementById("cv-root").innerHTML = "<p>Slug manquant dans l'URL.</p>";
        return;
    }

    let data;
    try {
        const res = await fetch(`/cv/${encodeURIComponent(s)}/data`);
        if (res.status === 404) {
            document.getElementById("cv-root").innerHTML =
                "<p>Ce CV n'existe pas ou n'est pas public.</p>";
            document.title = "CV introuvable";
            return;
        }
        data = await res.json();
    } catch {
        document.getElementById("cv-root").innerHTML =
            "<p>Impossible de charger le CV. Vérifie ta connexion.</p>";
        return;
    }

    const { profile, formations, experiences, skills } = data;
    document.title = `CV — ${profile.prenom} ${profile.nom}`;

    document.getElementById("cv-root").innerHTML = `
        <div class="cv-container">
            ${renderProfile(profile)}
            ${renderFormations(formations)}
            ${renderExperiences(experiences)}
            ${renderSkills(skills)}
        </div>`;
});
