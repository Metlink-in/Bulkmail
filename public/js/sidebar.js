(function () {

  /* ── PWA: manifest + theme-color + service worker ─────────────── */
  if (!document.querySelector('link[rel="manifest"]')) {
    const l = document.createElement('link');
    l.rel = 'manifest'; l.href = '/manifest.json';
    document.head.appendChild(l);
  }
  if (!document.querySelector('meta[name="theme-color"]')) {
    const m = document.createElement('meta');
    m.name = 'theme-color'; m.content = '#2563EB';
    document.head.appendChild(m);
  }
  if (!document.querySelector('meta[name="apple-mobile-web-app-capable"]')) {
    const m = document.createElement('meta');
    m.name = 'apple-mobile-web-app-capable'; m.content = 'yes';
    document.head.appendChild(m);
  }
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () =>
      navigator.serviceWorker.register('/sw.js').catch(() => {})
    );
  }

  /* ── Mobile sidebar toggle ─────────────────────────────────────── */
  function initMobileMenu() {
    const sidebar  = document.querySelector('.sidebar');
    if (!sidebar) return;

    // Overlay
    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'sidebar-overlay';
      document.body.appendChild(overlay);
    }
    overlay.addEventListener('click', closeSidebar);

    // Hamburger button — inject into page-header if not already there
    let btn = document.querySelector('.mobile-menu-btn');
    if (!btn) {
      btn = document.createElement('button');
      btn.className = 'mobile-menu-btn';
      btn.setAttribute('aria-label', 'Open menu');
      btn.innerHTML = '&#9776;';
      // Prepend to page-header, or body
      const header = document.querySelector('.page-header');
      if (header) {
        header.insertBefore(btn, header.firstChild);
      } else {
        // fallback: fixed top-left button
        btn.style.cssText = 'position:fixed;top:12px;left:12px;z-index:60;';
        document.body.appendChild(btn);
      }
    }
    btn.addEventListener('click', () => {
      const open = sidebar.classList.toggle('show');
      overlay.classList.toggle('show', open);
      btn.innerHTML = open ? '&#10005;' : '&#9776;';
    });

    function closeSidebar() {
      sidebar.classList.remove('show');
      overlay.classList.remove('show');
      if (btn) btn.innerHTML = '&#9776;';
    }

    // Close on nav item click (mobile navigation)
    sidebar.querySelectorAll('.sidebar-nav-item').forEach(a => {
      a.addEventListener('click', closeSidebar);
    });

    // Close on Escape
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeSidebar();
    });
  }

  /* ── Sidebar user info + logout ────────────────────────────────── */
  async function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;

    const payload = api.getTokenPayload();
    if (!payload) return;

    // User section
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
        <div id="impersonationBadge" style="display:none;background:var(--admin-accent);color:#000;font-size:10px;font-weight:800;padding:2px 4px;border-radius:4px;margin-left:8px;">IMP</div>
        <a href="#" id="logoutBtn" style="color:var(--danger);margin-left:auto;cursor:pointer;" title="Logout">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </a>`;
      sidebar.appendChild(userSection);
    }

    try {
      const me = await api.get('/auth/me');
      const name = me.name || me.email || 'User';
      const nameEl  = document.getElementById('userName');
      const avatarEl = document.getElementById('userAvatar');
      if (nameEl)   nameEl.textContent   = name;
      if (avatarEl) avatarEl.textContent = name.charAt(0).toUpperCase();
    } catch (_) {
      const nameEl = document.getElementById('userName');
      if (nameEl) nameEl.textContent = 'User';
    }

    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
      logoutBtn.onclick = e => {
        e.preventDefault();
        api.clearTokens();
        window.location.href = '/login.html';
      };
    }

    // Custom Outreach nav link — inject after Bulk Mail if not already present
    const nav = document.querySelector('.sidebar-nav');
    if (nav && !nav.querySelector('[data-outreach-link]')) {
      const bulkMailLink = [...nav.querySelectorAll('a')].find(a => a.href.includes('bulk-mail'));
      if (bulkMailLink) {
        const outreachLink = document.createElement('a');
        outreachLink.href = '/pages/custom-outreach.html';
        outreachLink.className = 'sidebar-nav-item' + (window.location.pathname.includes('custom-outreach') ? ' active' : '');
        outreachLink.setAttribute('data-outreach-link', '1');
        outreachLink.textContent = 'Custom Outreach';
        bulkMailLink.parentNode.insertBefore(outreachLink, bulkMailLink.nextSibling);
      }
    }

    // Guide link — inject before Settings if not already present
    if (nav && !nav.querySelector('[data-guide-link]')) {
      const settingsLink = [...nav.querySelectorAll('a')].find(a => a.href.includes('settings'));
      if (settingsLink) {
        const guideLink = document.createElement('a');
        guideLink.href = '/pages/guide.html';
        guideLink.className = 'sidebar-nav-item' + (window.location.pathname.includes('guide') ? ' active' : '');
        guideLink.setAttribute('data-guide-link', '1');
        guideLink.textContent = '? User Guide';
        settingsLink.parentNode.insertBefore(guideLink, settingsLink);
      }
    }

    // Admin link
    if (nav && payload.role === 'admin' && !nav.querySelector('[data-admin-link]')) {
      const div = document.createElement('div');
      div.setAttribute('data-admin-link', '1');
      div.innerHTML = `
        <hr style="margin:16px 12px;border:0;border-top:1px solid rgba(255,255,255,0.12);">
        <a href="/admin.html" class="sidebar-nav-item" style="color:var(--admin-accent);font-weight:700;">
          ⚙ Admin Panel
        </a>`;
      nav.appendChild(div);
    }

    // Impersonation
    if (payload.admin_impersonating) {
      const badge = document.getElementById('impersonationBadge');
      if (badge) badge.style.display = 'block';
      if (!document.getElementById('impersonationBanner')) {
        const banner = document.createElement('div');
        banner.id = 'impersonationBanner';
        banner.style = 'padding:12px;background:var(--admin-accent);color:#000;font-size:12px;font-weight:700;text-align:center;cursor:pointer;';
        banner.textContent = 'Switch back to Admin';
        banner.onclick = () => { api.clearTokens(); window.location.href = '/admin.html'; };
        sidebar.appendChild(banner);
      }
    }

    // Mobile menu must init AFTER sidebar is fully built
    initMobileMenu();
  }

  /* ── Back button injection ─────────────────────────────────────── */
  function injectBackButton() {
    // Don't add on top-level pages
    const topLevel = ['dashboard.html', 'login.html', 'register.html', '/'];
    const path = window.location.pathname;
    if (topLevel.some(p => path.endsWith(p)) || path === '/') return;

    const header = document.querySelector('.page-header');
    if (!header) return;

    // Only inject if there's no existing back/← link
    if (header.querySelector('.back-btn, .btn-ghost')) return;

    const btn = document.createElement('a');
    btn.className = 'btn btn-ghost btn-sm back-btn';
    btn.style.cssText = 'flex-shrink:0;';
    btn.textContent = '← Back';
    btn.href = '#';
    btn.onclick = e => { e.preventDefault(); history.back(); };
    header.insertBefore(btn, header.firstChild);
  }

  /* ── Draft state persistence for bulk-mail ─────────────────────── */
  function initDraftPersistence() {
    const path = window.location.pathname;
    if (!path.endsWith('bulk-mail.html')) return;

    const DRAFT_KEY = 'bulkreach_draft';

    function saveDraft() {
      try {
        const subject  = document.getElementById('subject');
        const htmlBody = document.getElementById('htmlBody');
        if (!subject || !htmlBody) return;
        sessionStorage.setItem(DRAFT_KEY, JSON.stringify({
          subject:  subject.value,
          htmlBody: htmlBody.innerHTML,
          ts:       Date.now()
        }));
      } catch (_) {}
    }

    function restoreDraft() {
      try {
        const raw = sessionStorage.getItem(DRAFT_KEY);
        if (!raw) return;
        const draft = JSON.parse(raw);
        // Only restore if saved within last 2 hours
        if (Date.now() - draft.ts > 7200000) { sessionStorage.removeItem(DRAFT_KEY); return; }

        const subject  = document.getElementById('subject');
        const htmlBody = document.getElementById('htmlBody');
        if (subject  && draft.subject)  subject.value     = draft.subject;
        if (htmlBody && draft.htmlBody) htmlBody.innerHTML = draft.htmlBody;

        // Trigger events so word count etc update
        if (subject)  subject.dispatchEvent(new Event('input'));
        if (htmlBody) htmlBody.dispatchEvent(new Event('input'));
      } catch (_) {}
    }

    // Restore on load (wait for page JS to finish)
    window.addEventListener('load', () => setTimeout(restoreDraft, 400));

    // Save on input and before unload
    document.addEventListener('input', saveDraft, { passive: true });
    window.addEventListener('beforeunload', saveDraft);
  }

  /* ── Boot ──────────────────────────────────────────────────────── */
  function boot() {
    injectBackButton();
    initDraftPersistence();
    if (typeof api !== 'undefined') {
      initSidebar();
    } else {
      // api.js not loaded yet — retry
      window.addEventListener('load', () => {
        if (typeof api !== 'undefined') initSidebar();
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

})();
