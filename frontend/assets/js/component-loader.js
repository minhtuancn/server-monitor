/**
 * Component Loader - Load reusable components (header, sidebar, breadcrumb)
 * Updated: 2026-01-07 - Added breadcrumb support
 */

/**
 * Load multiple components
 * @param {Array<string>} components - Array of component names to load
 * @returns {Promise<boolean>} Success status
 */
export async function loadComponents(components = ['header', 'sidebar']) {
    try {
        const componentPaths = {
            header: '/components/header.html',
            sidebar: '/components/sidebar.html',
            breadcrumb: '/components/breadcrumb.html'
        };

        const containerIds = {
            header: 'headerContainer',
            sidebar: 'sidebarContainer',
            breadcrumb: 'breadcrumbContainer'
        };

        // Load all requested components
        for (const component of components) {
            const path = componentPaths[component];
            const containerId = containerIds[component];

            if (!path || !containerId) {
                console.warn(`Unknown component: ${component}`);
                continue;
            }

            const res = await fetch(path);
            if (res.ok) {
                const html = await res.text();
                const container = document.getElementById(containerId);
                if (container) {
                    // For breadcrumb, insert the full HTML (includes styles and scripts)
                    if (component === 'breadcrumb') {
                        container.outerHTML = html;
                    } else {
                        // For header/sidebar, extract content without inline scripts
                        const content = extractContent(html);
                        container.outerHTML = content;
                    }
                }
            }
        }

        // Execute component scripts after DOM is updated
        setTimeout(() => {
            initComponentScripts();
        }, 100);

        return true;
    } catch (error) {
        console.error('Failed to load components:', error);
        return false;
    }
}

/**
 * Legacy function for backward compatibility
 */
export async function loadHeaderAndSidebar() {
    return await loadComponents(['header', 'sidebar']);
}

function extractContent(html) {
    // Extract everything except inline script tags
    return html.replace(/<script type="module">[\s\S]*?<\/script>/gi, '');
}

function initComponentScripts() {
    // Import necessary modules
    import('/assets/js/api.js').then(apiModule => {
        import('/assets/js/auth.js').then(authModule => {
            import('/assets/js/i18n.js').then(i18nModule => {
                const api = apiModule.default;
                const auth = authModule.default;
                const i18n = i18nModule.default;

                // Initialize sidebar
                initSidebar(api, auth, i18n);
                // Initialize header
                initHeader(auth, i18n);
            });
        });
    });
}

function initSidebar(api, auth, i18n) {
    // Set active page
    const currentPage = window.location.pathname.split('/').pop().replace('.html', '') || 'dashboard';
    document.querySelectorAll('.sidebar-item').forEach(link => {
        if (link.getAttribute('data-page') === currentPage) {
            link.classList.add('active');
        }
    });

    // Show/hide based on role
    const user = auth.getCurrentUser();
    const role = user?.role || 'user';
    const systemSection = document.getElementById('systemSection');
    if (systemSection) {
        systemSection.style.display = role === 'admin' ? 'block' : 'none';
    }

    // Load server count
    api.getServers().then(servers => {
        const badge = document.getElementById('serverCount');
        if (badge && servers) {
            badge.textContent = servers.length;
        }
    }).catch(console.error);

    // Defer translations to page-level i18n.translatePage()
}

function initHeader(auth, i18n) {
    // Set user info
    const user = auth.getCurrentUser();
    if (user && user.username) {
        const userNameEl = document.getElementById('userName');
        const userAvatarEl = document.getElementById('userAvatar');
        if (userNameEl) userNameEl.textContent = user.username;
        if (userAvatarEl) userAvatarEl.textContent = user.username.charAt(0).toUpperCase();
    }

    // Language switcher
    const currentLang = i18n.getCurrentLanguage();
    const languageNames = {
        'en': 'English',
        'vi': 'Tiếng Việt',
        'zh-CN': '简体中文',
        'ja': '日本語',
        'ko': '한국어',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch'
    };

    const currentLangEl = document.getElementById('currentLanguage');
    if (currentLangEl) {
        currentLangEl.textContent = languageNames[currentLang] || 'English';
    }

    // Language dropdown
    const languageMenuBtn = document.getElementById('languageMenuBtn');
    const languageDropdown = document.getElementById('languageDropdown');

    if (languageMenuBtn && languageDropdown) {
        languageMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            languageDropdown.classList.toggle('show');
        });

        languageDropdown.querySelectorAll('[data-lang]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lang = e.currentTarget.getAttribute('data-lang');
                i18n.setLanguage(lang);
                setTimeout(() => window.location.reload(), 300);
            });
        });
    }

    // User dropdown
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');

    if (userMenuBtn && userDropdown) {
        userMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });
    }

    // Close dropdowns on click outside
    document.addEventListener('click', () => {
        if (languageDropdown) languageDropdown.classList.remove('show');
        if (userDropdown) userDropdown.classList.remove('show');
    });

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await auth.logout();
            window.location.href = '/login.html';
        });
    }
}

export default {
    loadHeaderAndSidebar,
    loadComponents  // Export new function
};
