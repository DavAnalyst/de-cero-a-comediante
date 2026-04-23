// Central fetch wrapper. Attaches JWT automatically and handles 401 redirects.
const API = (() => {
  // En producción Nginx hace el proxy, aquí apunta directo al Flask de dev
  const BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : '/api';
  const TOKEN_KEY = 'dca_token';

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
  }

  function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  }

  function _headers(extra = {}) {
    const headers = { 'Content-Type': 'application/json', ...extra };
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
  }

  async function _handleResponse(res) {
    if (res.status === 401) {
      clearToken();
      if (!window.location.pathname.includes('login.html')) {
        window.location.href = '/login.html';
      }
      return null;
    }
    const json = await res.json().catch(() => null);
    if (!res.ok) {
      const msg = json?.error || `HTTP ${res.status}`;
      throw new Error(msg);
    }
    return json;
  }

  async function get(path) {
    const res = await fetch(BASE_URL + path, { headers: _headers() });
    return _handleResponse(res);
  }

  async function post(path, body) {
    const res = await fetch(BASE_URL + path, {
      method: 'POST',
      headers: _headers(),
      body: JSON.stringify(body),
    });
    return _handleResponse(res);
  }

  async function put(path, body) {
    const res = await fetch(BASE_URL + path, {
      method: 'PUT',
      headers: _headers(),
      body: JSON.stringify(body),
    });
    return _handleResponse(res);
  }

  return { get, post, put, getToken, setToken, clearToken };
})();
