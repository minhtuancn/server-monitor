/* ============================================
   Server Monitor v2.0 Enterprise - i18n Module
   Multi-language support with 8 languages
   ============================================ */

class I18n {
    constructor() {
        this.translations = {};
        this.fallbackLanguage = 'en';
        this.supportedLanguages = {
            'en': 'English',
            'vi': 'Tiếng Việt',
            'zh-CN': '简体中文',
            'ja': '日本語',
            'ko': '한국어',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch'
        };
        this.currentLanguage = this.getStoredLanguage() || this.detectBrowserLanguage();
    }

    /**
     * Get stored language from localStorage
     */
    getStoredLanguage() {
        return localStorage.getItem('language');
    }

    /**
     * Set and store language
     */
    setLanguage(lang) {
        if (!this.supportedLanguages[lang]) {
            console.warn(`Language ${lang} not supported, falling back to ${this.fallbackLanguage}`);
            lang = this.fallbackLanguage;
        }

        this.currentLanguage = lang;
        localStorage.setItem('language', lang);
        document.documentElement.lang = lang;

        // Dispatch event for other components to react
        window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
    }

    /**
     * Detect browser language
     */
    detectBrowserLanguage() {
        const browserLang = navigator.language || navigator.userLanguage;
        const langCode = browserLang.split('-')[0];

        // Check if browser language is supported
        if (this.supportedLanguages[browserLang]) {
            return browserLang;
        } else if (this.supportedLanguages[langCode]) {
            return langCode;
        }

        return this.fallbackLanguage;
    }

    /**
     * Load translation file for language
     */
    async loadTranslations(lang) {
        if (this.translations[lang]) {
            return this.translations[lang];
        }

        try {
            const response = await fetch(`/assets/locales/${lang}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load translations for ${lang}`);
            }

            this.translations[lang] = await response.json();
            return this.translations[lang];
        } catch (error) {
            console.error(`Error loading translations for ${lang}:`, error);

            // Load fallback if current language fails
            if (lang !== this.fallbackLanguage && !this.translations[this.fallbackLanguage]) {
                return this.loadTranslations(this.fallbackLanguage);
            }

            return {};
        }
    }

    /**
     * Get translation for key
     * Supports nested keys using dot notation: 'menu.dashboard'
     */
    t(key, params = {}) {
        const translations = this.translations[this.currentLanguage] || {};
        const fallbackTranslations = this.translations[this.fallbackLanguage] || {};

        // Get nested value
        const getValue = (obj, path) => {
            return path.split('.').reduce((curr, prop) => curr?.[prop], obj);
        };

        let translation = getValue(translations, key) || getValue(fallbackTranslations, key) || key;

        // Replace parameters
        Object.keys(params).forEach(param => {
            translation = translation.replace(new RegExp(`\\{${param}\\}`, 'g'), params[param]);
        });

        return translation;
    }

    /**
     * Translate element content
     */
    translateElement(element) {
        const key = element.getAttribute('data-i18n');
        if (key) {
            element.textContent = this.t(key);
        }

        // Translate attributes
        const attrs = ['placeholder', 'title', 'alt'];
        attrs.forEach(attr => {
            const attrKey = element.getAttribute(`data-i18n-${attr}`);
            if (attrKey) {
                element.setAttribute(attr, this.t(attrKey));
            }
        });
    }

    /**
     * Translate all elements with data-i18n attribute
     */
    translatePage() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            this.translateElement(element);
        });

        // Translate attributes
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.setAttribute('placeholder', this.t(key));
        });

        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.setAttribute('title', this.t(key));
        });
    }

    /**
     * Initialize i18n
     */
    async init() {
        await this.loadTranslations(this.currentLanguage);

        // Load fallback if different
        if (this.currentLanguage !== this.fallbackLanguage) {
            await this.loadTranslations(this.fallbackLanguage);
        }

        this.translatePage();

        // Watch for dynamic content
        this.observeDOMChanges();
    }

    /**
     * Observe DOM changes and translate new elements
     */
    observeDOMChanges() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        if (node.hasAttribute('data-i18n')) {
                            this.translateElement(node);
                        }
                        node.querySelectorAll('[data-i18n]').forEach(element => {
                            this.translateElement(element);
                        });
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    /**
     * Format number according to current language
     */
    formatNumber(number, options = {}) {
        return new Intl.NumberFormat(this.currentLanguage, options).format(number);
    }

    /**
     * Format date according to current language
     */
    formatDate(date, options = {}) {
        return new Intl.DateTimeFormat(this.currentLanguage, options).format(new Date(date));
    }

    /**
     * Format relative time (e.g., "2 hours ago")
     */
    formatRelativeTime(date) {
        const now = new Date();
        const past = new Date(date);
        const diffMs = now - past;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffSecs < 60) {
            return this.t('time.just_now');
        } else if (diffMins < 60) {
            return this.t('time.minutes_ago', { count: diffMins });
        } else if (diffHours < 24) {
            return this.t('time.hours_ago', { count: diffHours });
        } else if (diffDays < 30) {
            return this.t('time.days_ago', { count: diffDays });
        } else {
            return this.formatDate(date, { year: 'numeric', month: 'short', day: 'numeric' });
        }
    }

    /**
     * Get all supported languages
     */
    getSupportedLanguages() {
        return this.supportedLanguages;
    }

    /**
     * Get current language
     */
    getCurrentLanguage() {
        return this.currentLanguage;
    }
}

// Export singleton instance
const i18n = new I18n();

export default i18n;
