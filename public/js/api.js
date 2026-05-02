const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8080' : '';

const api = {
    getTokens() {
        return {
            access: localStorage.getItem('access_token'),
            refresh: localStorage.getItem('refresh_token')
        };
    },
    setTokens(access, refresh) {
        if(access) localStorage.setItem('access_token', access);
        if(refresh) localStorage.setItem('refresh_token', refresh);
    },
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },
    getTokenPayload() {
        const { access } = this.getTokens();
        if (!access) return null;
        try {
            const base64Url = access.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            return JSON.parse(window.atob(base64));
        } catch (e) {
            return null;
        }
    },
    isLoggedIn() {
        const payload = this.getTokenPayload();
        if (!payload) return false;
        return payload.exp * 1000 > Date.now();
    },
    getUserRole() {
        const payload = this.getTokenPayload();
        return payload ? payload.role : null;
    },
    async refreshAccessToken({ redirectOnFail = true } = {}) {
        const { refresh } = this.getTokens();
        if (!refresh) {
            this.clearTokens();
            if (redirectOnFail) window.location.href = '/login.html';
            return null;
        }
        try {
            const res = await fetch(`${API_BASE}/api/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refresh })
            });
            if (!res.ok) throw new Error("Refresh failed");
            const data = await res.json();
            this.setTokens(data.access_token, null);
            return data.access_token;
        } catch (e) {
            if (redirectOnFail) {
                this.clearTokens();
                window.location.href = '/login.html';
            }
            return null;
        }
    },
    async request(method, path, body = null, options = {}) {
        let { access } = this.getTokens();

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (access) {
            headers['Authorization'] = `Bearer ${access}`;
        }

        const config = { method, headers };
        if (body) {
            config.body = body instanceof FormData ? body : JSON.stringify(body);
            if (body instanceof FormData) {
                delete headers['Content-Type'];
            }
        }

        const safePath = path.startsWith('/') ? path : '/' + path;
        let res = await fetch(`${API_BASE}/api${safePath}`, config);

        if (res.status === 401 && access) {
            // silent refresh — never redirect during background requests
            const newToken = await this.refreshAccessToken({ redirectOnFail: false });
            if (newToken) {
                headers['Authorization'] = `Bearer ${newToken}`;
                res = await fetch(`${API_BASE}/api${safePath}`, config);
            } else {
                // refresh failed: only redirect if this is a user-initiated request (not polling)
                if (!options.silent) {
                    this.clearTokens();
                    window.location.href = '/login.html';
                }
                throw { status: 401, message: 'Session expired. Please log in again.' };
            }
        }

        let data;
        try {
            data = await res.json();
        } catch(e) {
            data = null;
        }

        if (!res.ok) {
            throw { status: res.status, message: data?.detail || res.statusText, detail: data };
        }
        return data;
    },
    // silent variant — 401 errors don't redirect to login (safe for polling)
    poll(path) { return this.request('GET', path, null, { silent: true }); },
    get(path) { return this.request('GET', path); },
    post(path, body) { return this.request('POST', path, body); },
    put(path, body) { return this.request('PUT', path, body); },
    delete(path) { return this.request('DELETE', path); },
    upload(path, formData) { return this.request('POST', path, formData); }
};

window.api = api;

function requireAuth() {
    if (!api.isLoggedIn()) {
        window.location.href = '/login.html';
    }
}

function requireAdmin() {
    requireAuth();
    if (api.getUserRole() !== 'admin') {
        window.location.href = '/dashboard.html';
    }
}
