/* ============================================
   Server Monitor v4.1 - Layout Module
   Shared layout components for all pages
   ============================================ */

// API Configuration
const currentPort = window.location.port || '80';
const apiPort = currentPort === '9081' ? 9083 : 8083;
const API_BASE = `${window.location.protocol}//${window.location.hostname}:${apiPort}`;

// Auth
const authToken = localStorage.getItem('auth_token');
const authUser = JSON.parse(localStorage.getItem('auth_user') || '{}');

// Check authentication
function requireAuth() {
    if (!authToken) {
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

// API Request helper
async function apiRequest(method, endpoint, data = null) {
    const config = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        }
    };
    if (data) config.body = JSON.stringify(data);

    const response = await fetch(`${API_BASE}${endpoint}`, config);
    if (response.status === 401) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        window.location.href = '/login.html';
        return null;
    }
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Request failed' }));
        throw new Error(error.error || error.message || 'Request failed');
    }
    if (response.status === 204) return {};
    return response.json();
}

// Language names
const langNames = { 'en': 'English', 'vi': 'Tiếng Việt', 'zh-CN': '简体中文', 'ja': '日本語', 'ko': '한국어', 'es': 'Español', 'fr': 'Français', 'de': 'Deutsch' };
const currentLang = localStorage.getItem('language') || 'en';

// Get current page name
function getCurrentPage() {
    const path = window.location.pathname;
    const page = path.split('/').pop().replace('.html', '') || 'dashboard';
    return page;
}

// Generate sidebar HTML
function generateSidebar(activePage) {
    const isAdmin = authUser?.role === 'admin';

    const menuItems = [
        {
            section: 'Overview', items: [
                { href: '/dashboard.html', icon: 'fa-th-large', label: 'Dashboard', page: 'dashboard' }
            ]
        },
        {
            section: 'Operations', items: [
                { href: '/terminal.html', icon: 'fa-terminal', label: 'Terminal', page: 'terminal' },
                { href: '/server-notes.html', icon: 'fa-sticky-note', label: 'Server Notes', page: 'server-notes' }
            ]
        },
        {
            section: 'Configuration', items: [
                { href: '/ssh-keys.html', icon: 'fa-key', label: 'SSH Keys', page: 'ssh-keys' },
                { href: '/email-settings.html', icon: 'fa-envelope', label: 'Email Alerts', page: 'email-settings' }
            ]
        },
        {
            section: 'Administration', items: [
                { href: '/users.html', icon: 'fa-users', label: 'User Management', page: 'users', adminOnly: true },
                { href: '/settings.html', icon: 'fa-cog', label: 'System Settings', page: 'settings', adminOnly: true },
                { href: '/domain-settings.html', icon: 'fa-globe', label: 'Domain & SSL', page: 'domain-settings', adminOnly: true }
            ], adminOnly: true
        }
    ];

    let html = `
        <aside class="w-64 bg-dark-900 border-r border-dark-700 fixed h-full z-30">
            <div class="h-16 flex items-center px-6 border-b border-dark-700">
                <a href="/dashboard.html" class="flex items-center gap-3">
                    <div class="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                        <i class="fas fa-server text-white text-sm"></i>
                    </div>
                    <span class="font-bold text-lg text-white">Server Monitor</span>
                </a>
            </div>
            <nav class="p-4 space-y-1 overflow-y-auto" style="height: calc(100% - 120px);">
    `;

    menuItems.forEach(section => {
        if (section.adminOnly && !isAdmin) return;

        html += `<div class="text-xs font-semibold text-dark-400 uppercase tracking-wider px-3 py-2 mt-4">${section.section}</div>`;

        section.items.forEach(item => {
            if (item.adminOnly && !isAdmin) return;

            const isActive = activePage === item.page;
            const activeClass = isActive ? 'bg-primary-500/10 border-l-2 border-primary-500 text-primary-400' : 'text-gray-300 hover:bg-dark-800 hover:text-white';

            html += `
                <a href="${item.href}" class="flex items-center gap-3 px-3 py-2.5 rounded-r-lg ${activeClass}">
                    <i class="fas ${item.icon} w-5 text-center"></i>
                    <span>${item.label}</span>
                </a>
            `;
        });
    });

    html += `
            </nav>
            <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-dark-700">
                <div class="text-xs text-dark-400 text-center">Server Monitor v4.1</div>
            </div>
        </aside>
    `;

    return html;
}

// Generate header HTML
function generateHeader(title) {
    const userName = authUser?.username || 'User';
    const userRole = authUser?.role || 'User';
    const userInitial = userName[0].toUpperCase();

    return `
        <header class="h-16 bg-dark-900/80 backdrop-blur-md border-b border-dark-700 sticky top-0 z-20">
            <div class="h-full px-6 flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <h1 class="text-xl font-semibold text-white">${title}</h1>
                </div>
                
                <div class="flex items-center gap-4">
                    <!-- Language Selector -->
                    <div class="relative" id="langDropdown">
                        <button onclick="toggleLangDropdown()" class="flex items-center gap-2 px-3 py-2 rounded-lg bg-dark-800 hover:bg-dark-700 text-gray-300 text-sm">
                            <i class="fas fa-globe"></i>
                            <span id="currentLangName">${langNames[currentLang] || 'English'}</span>
                            <i class="fas fa-chevron-down text-xs"></i>
                        </button>
                        <div id="langMenu" class="hidden absolute right-0 mt-2 w-48 bg-dark-800 rounded-lg shadow-xl border border-dark-600 py-1 z-50">
                            <button onclick="changeLanguage('en')" class="w-full px-4 py-2 text-left text-sm text-gray-300 hover:bg-dark-700 flex items-center gap-2">🇺🇸 English</button>
                            <button onclick="changeLanguage('vi')" class="w-full px-4 py-2 text-left text-sm text-gray-300 hover:bg-dark-700 flex items-center gap-2">🇻🇳 Tiếng Việt</button>
                            <button onclick="changeLanguage('zh-CN')" class="w-full px-4 py-2 text-left text-sm text-gray-300 hover:bg-dark-700 flex items-center gap-2">🇨🇳 简体中文</button>
                            <button onclick="changeLanguage('ja')" class="w-full px-4 py-2 text-left text-sm text-gray-300 hover:bg-dark-700 flex items-center gap-2">🇯🇵 日本語</button>
                            <button onclick="changeLanguage('ko')" class="w-full px-4 py-2 text-left text-sm text-gray-300 hover:bg-dark-700 flex items-center gap-2">🇰🇷 한국어</button>
                        </div>
                    </div>
                    
                    <!-- User Menu -->
                    <div class="relative" id="userDropdown">
                        <button onclick="toggleUserDropdown()" class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-dark-800">
                            <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center text-white font-semibold text-sm">${userInitial}</div>
                            <span class="text-sm text-gray-300">${userName}</span>
                            <i class="fas fa-chevron-down text-xs text-gray-400"></i>
                        </button>
                        <div id="userMenu" class="hidden absolute right-0 mt-2 w-56 bg-dark-800 rounded-lg shadow-xl border border-dark-600 py-1 z-50">
                            <div class="px-4 py-3 border-b border-dark-600">
                                <div class="font-medium text-white">${userName}</div>
                                <div class="text-xs text-gray-400 capitalize">${userRole}</div>
                            </div>
                            <a href="/settings.html" class="flex items-center gap-2 px-4 py-2 text-sm text-gray-300 hover:bg-dark-700">
                                <i class="fas fa-cog w-4"></i> Settings
                            </a>
                            <button onclick="logout()" class="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-dark-700">
                                <i class="fas fa-sign-out-alt w-4"></i> Logout
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    `;
}

// Initialize layout
function initLayout(title) {
    if (!requireAuth()) return;

    const currentPage = getCurrentPage();

    // Insert sidebar
    const sidebarContainer = document.getElementById('sidebarContainer');
    if (sidebarContainer) {
        sidebarContainer.innerHTML = generateSidebar(currentPage);
    }

    // Insert header
    const headerContainer = document.getElementById('headerContainer');
    if (headerContainer) {
        headerContainer.innerHTML = generateHeader(title);
    }

    // Setup event listeners
    setupDropdowns();
}

// Setup dropdown event listeners
function setupDropdowns() {
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#langDropdown')) {
            const langMenu = document.getElementById('langMenu');
            if (langMenu) langMenu.classList.add('hidden');
        }
        if (!e.target.closest('#userDropdown')) {
            const userMenu = document.getElementById('userMenu');
            if (userMenu) userMenu.classList.add('hidden');
        }
    });
}

// Global functions
window.toggleLangDropdown = function () {
    document.getElementById('langMenu')?.classList.toggle('hidden');
    document.getElementById('userMenu')?.classList.add('hidden');
};

window.toggleUserDropdown = function () {
    document.getElementById('userMenu')?.classList.toggle('hidden');
    document.getElementById('langMenu')?.classList.add('hidden');
};

window.changeLanguage = function (lang) {
    localStorage.setItem('language', lang);
    window.location.reload();
};

window.logout = function () {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    window.location.href = '/login.html';
};

// Toast notification
window.showToast = function (message, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'fixed bottom-4 right-4 z-50 space-y-2';
        document.body.appendChild(container);
    }

    const colors = {
        success: 'bg-emerald-600',
        error: 'bg-red-600',
        warning: 'bg-amber-600',
        info: 'bg-primary-600'
    };
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    const toast = document.createElement('div');
    toast.className = `${colors[type]} text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3`;
    toast.innerHTML = `<i class="fas ${icons[type]}"></i><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => toast.remove(), 4000);
};

// Export for ES modules
export { API_BASE, authToken, authUser, apiRequest, initLayout, requireAuth, showToast };
