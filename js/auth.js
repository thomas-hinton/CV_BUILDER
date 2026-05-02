/*
 * Auth page logic — register and login forms.
 *
 * DISCLAIMER: This file was written with assistance from GitHub Copilot
 * (Claude Sonnet 4.6) and reviewed by the project author.
 *
 * Token storage: localStorage is used here for simplicity (learning project).
 * For a production deployment, prefer HttpOnly cookies.
 */

const API = ""; // chemins relatifs — fonctionne quel que soit l'hôte

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function showError(elementId, message) {
    const el = document.getElementById(elementId);
    el.textContent = message;
    el.style.display = "block";
}

function hideError(elementId) {
    const el = document.getElementById(elementId);
    el.textContent = "";
    el.style.display = "none";
}

function setLoading(buttonId, loading) {
    const btn = document.getElementById(buttonId);
    btn.disabled = loading;
    btn.textContent = loading ? "Chargement..." : btn.dataset.label;
}

// ---------------------------------------------------------------------------
// Register
// ---------------------------------------------------------------------------

async function register(email, password) {
    try {
        const res = await fetch(`${API}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });
        return { ok: res.ok, status: res.status, data: await res.json() };
    } catch {
        return { ok: false, status: 0, data: {} };
    }
}

// ---------------------------------------------------------------------------
// Login
// ---------------------------------------------------------------------------

async function login(email, password) {
    try {
        const res = await fetch(`${API}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });
        return { ok: res.ok, status: res.status, data: await res.json() };
    } catch {
        return { ok: false, status: 0, data: {} };
    }
}

// ---------------------------------------------------------------------------
// Tab switching (login ↔ register)
// ---------------------------------------------------------------------------

function showTab(tab) {
    document.getElementById("login-form").style.display = tab === "login" ? "block" : "none";
    document.getElementById("register-form").style.display = tab === "register" ? "block" : "none";
    document.getElementById("tab-login").classList.toggle("active", tab === "login");
    document.getElementById("tab-register").classList.toggle("active", tab === "register");
    hideError("login-error");
    hideError("register-error");
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    // Redirect if already logged in
    if (localStorage.getItem("token")) {
        window.location.href = "/admin";
        return;
    }

    // Tab buttons
    document.getElementById("tab-login").addEventListener("click", () => showTab("login"));
    document.getElementById("tab-register").addEventListener("click", () => showTab("register"));

    // Login form
    document.getElementById("login-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        hideError("login-error");
        setLoading("btn-login", true);

        const email = document.getElementById("login-email").value.trim();
        const password = document.getElementById("login-password").value;

        const { ok, status, data } = await login(email, password);
        setLoading("btn-login", false);

        if (ok) {
            localStorage.setItem("token", data.access_token);
            window.location.href = "/admin";
        } else {
            showError("login-error",
                status === 0   ? "Impossible de joindre le serveur." :
                status === 401 ? "Email ou mot de passe incorrect." :
                                 "Erreur serveur, réessaie."
            );
        }
    });

    // Register form
    document.getElementById("register-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        hideError("register-error");

        const email = document.getElementById("register-email").value.trim();
        const password = document.getElementById("register-password").value;
        const confirm = document.getElementById("register-confirm").value;

        if (password !== confirm) {
            showError("register-error", "Les mots de passe ne correspondent pas.");
            return;
        }
        if (password.length < 6) {
            showError("register-error", "Le mot de passe doit faire au moins 6 caractères.");
            return;
        }

        setLoading("btn-register", true);
        const { ok, status, data } = await register(email, password);
        setLoading("btn-register", false);

        if (ok) {
            // Auto-login after register
            const loginResult = await login(email, password);
            if (loginResult.ok) {
                localStorage.setItem("token", loginResult.data.access_token);
                window.location.href = "/admin";
            }
        } else {
            showError("register-error",
                status === 0   ? "Impossible de joindre le serveur." :
                status === 409 ? "Cet email est déjà utilisé." :
                                 "Erreur serveur, réessaie."
            );
        }
    });

    // Show login tab by default
    showTab("login");
});
