/* Frontend Config (runtime)
 * Toggle features without rebuild. Safe defaults.
 */

const baseConfig = {
    // Allow login over HTTP (dev environments). Set false to require HTTPS.
    allowInsecureLogin: true,
    // Reserved for future use (not enforced automatically here)
    enforceHttps: false
};

// LocalStorage overrides: set key 'config.allowInsecureLogin' to 'true' or 'false'
try {
    const lsAllow = localStorage.getItem('config.allowInsecureLogin');
    if (lsAllow !== null) baseConfig.allowInsecureLogin = lsAllow === 'true';
} catch (e) {
    // ignore
}

// Merge with any preloaded window.APP_CONFIG (if server injects)
const APP_CONFIG = Object.assign({}, baseConfig, window.APP_CONFIG || {});

// Expose globally and as module export
window.APP_CONFIG = APP_CONFIG;
export default APP_CONFIG;
