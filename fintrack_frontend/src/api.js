// Single axios instance with JWT auth baked in. Every component that
// talks to the backend imports `api` from here so the bearer token
// attaches automatically and a 401 kicks the user to /login in one place
// instead of N.

import axios from 'axios';

const ACCESS_TOKEN_KEY = 'fintrack_access_token';
const REFRESH_TOKEN_KEY = 'fintrack_refresh_token';

const api = axios.create({
  baseURL: '/',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Token expired or otherwise bad. Clear and bounce to login.
    // Skip the redirect on the /api/token/ endpoint itself. Bad creds
    // there should surface as a form error, not a redirect loop.
    const url = error.config?.url || '';
    if (error.response?.status === 401 && !url.includes('/api/token/')) {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      if (window.location.pathname !== '/login') {
        window.location.assign('/login');
      }
    }
    return Promise.reject(error);
  },
);

export async function login(username, password) {
  const { data } = await api.post('/api/token/', { username, password });
  localStorage.setItem(ACCESS_TOKEN_KEY, data.access);
  localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh);
  return data;
}

export function logout() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem(ACCESS_TOKEN_KEY));
}

export default api;
