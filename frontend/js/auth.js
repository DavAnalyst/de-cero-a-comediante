// Auth: login, register, logout, route guard
const Auth = (() => {
  const TOKEN_KEY = 'dca_token';
  const USER_KEY  = 'dca_user';

  function saveSession(token, user) {
    API.setToken(token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  function clearSession() {
    API.clearToken();
    localStorage.removeItem(USER_KEY);
  }

  function currentUser() {
    try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; }
  }

  function isLoggedIn() {
    return !!API.getToken();
  }

  // Redirect to login if not authenticated
  function requireAuth() {
    if (!isLoggedIn()) {
      window.location.href = '/login.html';
    }
  }

  // Redirect to login if not admin
  function requireAdmin() {
    if (!isLoggedIn()) { window.location.href = '/login.html'; return; }
    const user = currentUser();
    if (!user?.is_admin) { window.location.href = '/dashboard.html'; }
  }

  function logout() {
    clearSession();
    window.location.href = '/index.html';
  }

  // ─── Login page logic ─────────────────────────────────────────────────────
  function initLoginPage() {
    // If already logged in → go to dashboard
    if (isLoggedIn()) {
      window.location.href = '/dashboard.html';
      return;
    }

    const tabs = document.querySelectorAll('.auth-tab');
    const loginForm    = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const loginError   = document.getElementById('login-error');
    const regError     = document.getElementById('register-error');

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const which = tab.dataset.tab;
        loginForm.classList.toggle('hidden', which !== 'login');
        registerForm.classList.toggle('hidden', which !== 'register');
      });
    });

    loginForm?.addEventListener('submit', async e => {
      e.preventDefault();
      loginError.classList.add('hidden');
      const email    = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;
      try {
        const data = await API.post('/auth/login', { email, password });
        if (data) {
          saveSession(data.token, data.user);
          const redirect = new URLSearchParams(location.search).get('next') || '/dashboard.html';
          window.location.href = redirect;
        }
      } catch (err) {
        loginError.textContent = err.message;
        loginError.classList.remove('hidden');
      }
    });

    registerForm?.addEventListener('submit', async e => {
      e.preventDefault();
      regError.classList.add('hidden');
      const name     = document.getElementById('reg-name').value.trim();
      const email    = document.getElementById('reg-email').value.trim();
      const password = document.getElementById('reg-password').value;
      try {
        const data = await API.post('/auth/register', { name, email, password });
        if (data) {
          saveSession(data.token, data.user);
          window.location.href = '/dashboard.html';
        }
      } catch (err) {
        regError.textContent = err.message;
        regError.classList.remove('hidden');
      }
    });
  }

  // ─── Bind logout button wherever present ─────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('logout-btn')?.addEventListener('click', logout);
    document.getElementById('admin-logout')?.addEventListener('click', logout);

    if (document.body.classList.contains('auth-page')) {
      initLoginPage();
    }
  });

  return { requireAuth, requireAdmin, currentUser, isLoggedIn, logout, saveSession };
})();
