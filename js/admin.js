/*
 * Admin dashboard — CV editor connected to the real API.
 *
 * DISCLAIMER: This file was written with assistance from GitHub Copilot
 * (Claude Sonnet 4.6) and reviewed by the project author.
 */

const API = "http://127.0.0.1:8000";

// Track whether a profile already exists so we know which HTTP method to use.
let profileExists = false;

// ---------------------------------------------------------------------------
// Auth helpers
// ---------------------------------------------------------------------------

function getToken() {
    return localStorage.getItem("token");
}

function authHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${getToken()}`,
    };
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/";
}

// ---------------------------------------------------------------------------
// Generic API wrapper — returns { ok, status, data }
// ---------------------------------------------------------------------------

async function api(method, path, body) {
    const opts = { method, headers: authHeaders() };
    if (body !== undefined) opts.body = JSON.stringify(body);
    const res = await fetch(`${API}${path}`, opts);
    if (res.status === 401) {
        logout();
        return { ok: false, status: 401, data: null };
    }
    const data = res.status !== 204 ? await res.json() : null;
    return { ok: res.ok, status: res.status, data };
}

// ---------------------------------------------------------------------------
// UI helpers
// ---------------------------------------------------------------------------

function showMsg(id, text, isError = false) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = "msg " + (isError ? "msg-error" : "msg-ok");
    el.style.display = "block";
    setTimeout(() => { el.style.display = "none"; }, 4000);
}

function val(id) {
    const el = document.getElementById(id);
    if (!el) return null;
    if (el.type === "checkbox") return el.checked;
    const v = el.value.trim();
    return v === "" ? null : v;
}

function set(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    if (el.type === "checkbox") el.checked = !!value;
    else el.value = value ?? "";
}

// ---------------------------------------------------------------------------
// Profile — load and save
// ---------------------------------------------------------------------------

async function loadProfile() {
    const { ok, status, data } = await api("GET", "/profiles/me");

    if (status === 404) {
        profileExists = false;
        document.getElementById("profile-status").textContent =
            "Aucun profil trouvé. Remplis le formulaire ci-dessous pour en créer un.";
        return;
    }
    if (!ok) {
        showMsg("profile-msg", "Erreur lors du chargement du profil.", true);
        return;
    }

    profileExists = true;
    document.getElementById("profile-status").textContent = "";
    document.getElementById("profile-slug-info").textContent =
        `URL publique : /cv/${data.slug}`;

    set("f-nom",        data.nom);
    set("f-prenom",     data.prenom);
    set("f-email",      data.email);
    set("f-tel",        data.tel);
    set("f-adresse",    data.adresse);
    set("f-is-public",  data.is_public);
    set("f-show-email", data.show_email);
    set("f-show-phone", data.show_phone);

    await loadFormations();
    await loadExperiences();
    await loadSkills();
}

async function saveProfile(e) {
    e.preventDefault();

    const body = {
        nom:        val("f-nom"),
        prenom:     val("f-prenom"),
        email:      val("f-email"),
        tel:        val("f-tel"),
        adresse:    val("f-adresse"),
        is_public:  val("f-is-public"),
        show_email: val("f-show-email"),
        show_phone: val("f-show-phone"),
    };

    const method = profileExists ? "PATCH" : "POST";
    const { ok, data } = await api(method, "/profiles/me", body);

    if (ok) {
        profileExists = true;
        showMsg("profile-msg", "Profil sauvegardé ✓");
        document.getElementById("profile-slug-info").textContent =
            `URL publique : /cv/${data.slug}`;
        // Refresh list sections on first creation
        if (method === "POST") {
            await loadFormations();
            await loadExperiences();
            await loadSkills();
        }
    } else {
        const detail = data?.detail ?? "Erreur inconnue";
        showMsg("profile-msg", typeof detail === "string" ? detail : JSON.stringify(detail), true);
    }
}

// ---------------------------------------------------------------------------
// Formations
// ---------------------------------------------------------------------------

async function loadFormations() {
    const { ok, data } = await api("GET", "/profiles/me/educations");
    if (!ok) return;
    renderList("formations-list", data, renderFormationItem);
}

function renderFormationItem(f) {
    return `
        <div class="list-item">
            <span><strong>${f.nom_formation}</strong> — ${f.organisme_formation}
            (${f.date_debut}${f.date_fin ? " → " + f.date_fin : ""})</span>
            <button class="btn-delete" data-id="${f.id_formation}" data-type="formation">Supprimer</button>
        </div>`;
}

async function addFormation(e) {
    e.preventDefault();
    const body = {
        nom_formation:          val("fo-nom"),
        organisme_formation:    val("fo-organisme"),
        date_debut:             val("fo-date-debut"),
        date_fin:               val("fo-date-fin"),
        description_formation:  val("fo-description"),
    };
    const { ok, data } = await api("POST", "/profiles/me/educations", body);
    if (ok) {
        showMsg("formation-msg", "Formation ajoutée ✓");
        e.target.reset();
        await loadFormations();
    } else {
        showMsg("formation-msg", data?.detail ?? "Erreur", true);
    }
}

// ---------------------------------------------------------------------------
// Experiences
// ---------------------------------------------------------------------------

async function loadExperiences() {
    const { ok, data } = await api("GET", "/profiles/me/experiences");
    if (!ok) return;
    renderList("experiences-list", data, renderExperienceItem);
}

function renderExperienceItem(exp) {
    return `
        <div class="list-item">
            <span><strong>${exp.nom_experience}</strong>${exp.organisme_experience ? " — " + exp.organisme_experience : ""}
            (${exp.date_debut}${exp.date_fin ? " → " + exp.date_fin : ""})</span>
            <button class="btn-delete" data-id="${exp.id_experience}" data-type="experience">Supprimer</button>
        </div>`;
}

async function addExperience(e) {
    e.preventDefault();
    const body = {
        nom_experience:         val("ex-nom"),
        organisme_experience:   val("ex-organisme"),
        date_debut:             val("ex-date-debut"),
        date_fin:               val("ex-date-fin"),
        description_experience: val("ex-description"),
        lieu_experience:        val("ex-lieu"),
    };
    const { ok, data } = await api("POST", "/profiles/me/experiences", body);
    if (ok) {
        showMsg("experience-msg", "Expérience ajoutée ✓");
        e.target.reset();
        await loadExperiences();
    } else {
        showMsg("experience-msg", data?.detail ?? "Erreur", true);
    }
}

// ---------------------------------------------------------------------------
// Skills
// ---------------------------------------------------------------------------

async function loadSkills() {
    const { ok, data } = await api("GET", "/profiles/me/skills");
    if (!ok) return;
    renderList("skills-list", data, renderSkillItem);
}

function renderSkillItem(s) {
    return `
        <div class="list-item">
            <span><strong>${s.nom_skill}</strong>${s.niveau ? " — " + s.niveau : ""}${s.categorie ? " (" + s.categorie + ")" : ""}</span>
            <button class="btn-delete" data-id="${s.id_skill}" data-type="skill">Supprimer</button>
        </div>`;
}

async function addSkill(e) {
    e.preventDefault();
    const body = {
        nom_skill:  val("sk-nom"),
        niveau:     val("sk-niveau"),
        categorie:  val("sk-categorie"),
    };
    const { ok, data } = await api("POST", "/profiles/me/skills", body);
    if (ok) {
        showMsg("skill-msg", "Compétence ajoutée ✓");
        e.target.reset();
        await loadSkills();
    } else {
        showMsg("skill-msg", data?.detail ?? "Erreur", true);
    }
}

// ---------------------------------------------------------------------------
// Generic list renderer + delete handler
// ---------------------------------------------------------------------------

function renderList(containerId, items, renderFn) {
    const container = document.getElementById(containerId);
    if (!items || items.length === 0) {
        container.innerHTML = "<p class='empty'>Aucun élément.</p>";
        return;
    }
    container.innerHTML = items.map(renderFn).join("");

    container.querySelectorAll(".btn-delete").forEach((btn) => {
        btn.addEventListener("click", handleDelete);
    });
}

async function handleDelete(e) {
    const { id, type } = e.currentTarget.dataset;
    const paths = {
        formation:  `/profiles/me/educations/${id}`,
        experience: `/profiles/me/experiences/${id}`,
        skill:      `/profiles/me/skills/${id}`,
    };
    const { ok } = await api("DELETE", paths[type]);
    if (ok) {
        if (type === "formation")  await loadFormations();
        if (type === "experience") await loadExperiences();
        if (type === "skill")      await loadSkills();
    }
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", async () => {
    if (!getToken()) {
        window.location.href = "/";
        return;
    }

    document.getElementById("btn-logout").addEventListener("click", logout);
    document.getElementById("profile-form").addEventListener("submit", saveProfile);
    document.getElementById("formation-form").addEventListener("submit", addFormation);
    document.getElementById("experience-form").addEventListener("submit", addExperience);
    document.getElementById("skill-form").addEventListener("submit", addSkill);

    await loadProfile();
});


