/**
 * i18n Helper - Auto-translate DOM elements
 * Usage: Add data-i18n="key" to any HTML element
 * Example: <button data-i18n="common.save">Save</button>
 */

import i18n from './i18n.js';

/**
 * Translate all elements with data-i18n attribute
 */
export function translatePage() {
    // Translate text content
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = i18n.t(key);

        if (element.tagName === 'INPUT' && element.placeholder !== undefined) {
            element.placeholder = translation;
        } else {
            element.textContent = translation;
        }
    });

    // Translate placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        element.placeholder = i18n.t(key);
    });

    // Translate titles
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        element.title = i18n.t(key);
    });

    // Translate aria-labels
    document.querySelectorAll('[data-i18n-aria]').forEach(element => {
        const key = element.getAttribute('data-i18n-aria');
        element.setAttribute('aria-label', i18n.t(key));
    });
}

/**
 * Initialize i18n for the page
 */
export async function initI18n() {
    const currentLang = i18n.getLanguage();
    await i18n.loadLanguage(currentLang);
    translatePage();

    // Set document language
    document.documentElement.lang = currentLang;
}

/**
 * Get translation shorthand
 */
export function t(key, params = {}) {
    return i18n.t(key, params);
}

/**
 * Format number
 */
export function formatNumber(number, options = {}) {
    return i18n.formatNumber(number, options);
}

/**
 * Format date
 */
export function formatDate(date, format = 'short') {
    return i18n.formatDate(date, format);
}

/**
 * Format relative time
 */
export function relativeTime(date) {
    return i18n.relativeTime(date);
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initI18n);
} else {
    initI18n();
}

export default {
    translatePage,
    initI18n,
    t,
    formatNumber,
    formatDate,
    relativeTime
};
