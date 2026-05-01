(function() {
    async function initSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;

        const payload = api.getTokenPayload();
        if (!payload) return;

        // 1. Build user section skeleton immediately
        let userSection = document.querySelector('.sidebar-user');
        if (!userSection) {
            userSection = document.createElement('div');
            userSection.className = 'sidebar-user';
            userSection.innerHTML = `
                <div class="sidebar-user-avatar" id="userAvatar">U</div>
                <div class="sidebar-user-info">
                    <span class="sidebar-user-name" id="userName">Loading…</span>
                    <span class="sidebar-user-role" id="userRole">${payload.role}</span>
                </div>
                <div id="impersonationBadge" style="display:none; background:var(--admin-accent); color:#000; font-size:10px; font-weight:800; padding:2px 4px; border-radius:4px; margin-left:8px;">IMP</div>
                <a href="#" id="logoutBtn" style="color:var(--danger); margin-left:auto; cursor:pointer;" title="Logout">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                </a>
            `;
            sidebar.appendChild(userSection);
        }

        // 2. Fetch real user profile for name/email
        try {
            const me = await api.get('/auth/me');
            const name = me.name || me.email || 'User';
            const nameEl = document.getElementById('userName');
            const avatarEl = document.getElementById('userAvatar');
            if (nameEl) nameEl.textContent = name;
            if (avatarEl) avatarEl.textContent = name.charAt(0).toUpperCase();
        } catch (_) {
            const nameEl = document.getElementById('userName');
            if (nameEl) nameEl.textContent = 'User';
        }

        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.onclick = (e) => {
                e.preventDefault();
                api.clearTokens();
                window.location.href = '/login.html';
            };
        }

        // 3. Add Admin Link if admin
        const nav = document.querySelector('.sidebar-nav');
        if (nav && payload.role === 'admin') {
            if (!nav.querySelector('[data-admin-link]')) {
                const adminLink = document.createElement('div');
                adminLink.setAttribute('data-admin-link', '1');
                adminLink.innerHTML = `
                    <hr style="margin: 16px 12px; border: 0; border-top: 1px solid var(--border); opacity: 0.3;">
                    <a href="/admin.html" class="sidebar-nav-item" style="color:var(--admin-accent); font-weight:700;">
                        Go to Admin Panel
                    </a>
                `;
                nav.appendChild(adminLink);
            }
        }

        // 4. Handle Impersonation
        if (payload.admin_impersonating) {
            const badge = document.getElementById('impersonationBadge');
            if (badge) badge.style.display = 'block';

            if (!document.getElementById('impersonationBanner')) {
                const banner = document.createElement('div');
                banner.id = 'impersonationBanner';
                banner.style = 'padding:12px; background:var(--admin-accent); color:#000; font-size:12px; font-weight:700; text-align:center; cursor:pointer;';
                banner.textContent = 'Switch back to Admin';
                banner.onclick = () => {
                    api.clearTokens();
                    window.location.href = '/admin.html';
                };
                sidebar.appendChild(banner);
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSidebar);
    } else {
        initSidebar();
    }
})();
