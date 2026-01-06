# i18n Integration Guide

## Quick Start

### 1. Import i18n module in your page
```javascript
import i18n from '/assets/js/i18n.js';
```

### 2. Add data-i18n attributes to HTML elements

```html
<!-- Basic text translation -->
<h1 data-i18n="dashboard.title">Dashboard</h1>
<button data-i18n="common.save">Save</button>
<label data-i18n="users.username">Username</label>

<!-- Placeholder translation -->
<input data-i18n-placeholder="common.search" placeholder="Search...">

<!-- Title/tooltip translation -->
<button data-i18n-title="common.help" title="Help">?</button>

<!-- Aria-label translation -->
<button data-i18n-aria="common.close" aria-label="Close">×</button>
```

### 3. Initialize i18n in your script

```javascript
// Simple initialization
async function initI18n() {
    const currentLang = i18n.getLanguage();
    await i18n.loadLanguage(currentLang);
    translatePage();
    document.documentElement.lang = currentLang;
}

function translatePage() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        element.textContent = i18n.t(key);
    });
}

initI18n();
```

### 4. Use i18n.t() for dynamic content

```javascript
// Translate messages dynamically
const message = i18n.t('auth.loginSuccess');
showToast(message, 'success');

// With parameters
const greeting = i18n.t('common.hello', { name: 'John' });
// If translation is: "Hello {name}!" → Output: "Hello John!"

// Format numbers
const formatted = i18n.formatNumber(1234567.89); // 1,234,567.89

// Format dates
const date = i18n.formatDate(new Date(), 'long'); // January 6, 2026

// Relative time
const relative = i18n.relativeTime(new Date(Date.now() - 3600000)); // 1 hour ago
```

## Translation Keys Structure

All translation keys are organized in JSON files under `frontend/assets/locales/`:

```
common.*        - Common UI elements (save, cancel, delete, etc.)
dashboard.*     - Dashboard page
users.*         - User management
settings.*      - System settings
servers.*       - Server management
terminal.*      - Terminal page
network.*       - Network tools
auth.*          - Authentication
errors.*        - Error messages
```

## Supported Languages

1. 🇺🇸 English (en)
2. 🇻🇳 Vietnamese (vi)
3. 🇨🇳 Chinese Simplified (zh-CN)
4. 🇯🇵 Japanese (ja)
5. 🇰🇷 Korean (ko)
6. 🇪🇸 Spanish (es)
7. 🇫🇷 French (fr)
8. 🇩🇪 German (de)

## Pages with i18n Integrated

- ✅ login.html - Full integration
- ✅ components/header.html - Language switcher + user menu
- ✅ components/sidebar.html - Navigation menu
- ⏳ dashboard.html - In progress
- ⏳ users.html - In progress
- ⏳ settings.html - In progress

## Adding New Translation Keys

1. Add key to all 8 language files in `frontend/assets/locales/`:
   - en.json
   - vi.json
   - zh-CN.json
   - ja.json
   - ko.json
   - es.json
   - fr.json
   - de.json

2. Use the key in your HTML or JavaScript:
   ```html
   <button data-i18n="yourSection.yourKey">Default Text</button>
   ```

3. The default text will be replaced when i18n loads.

## Best Practices

1. **Use nested keys**: `dashboard.title` instead of `dashboardTitle`
2. **Keep it organized**: Group related keys under same section
3. **Be descriptive**: Use clear key names like `users.deleteConfirmation`
4. **Test all languages**: Check that translations fit in UI elements
5. **Use parameters**: `"Welcome {name}!"` for dynamic content
6. **Fallback gracefully**: Always provide default English text in HTML

## Helper Module

Use `i18n-helper.js` for automatic translation:

```javascript
import { initI18n, t } from '/assets/js/i18n-helper.js';

// Auto-translate all data-i18n elements
await initI18n();

// Use shorthand for translations
const msg = t('common.save');
```

This helper automatically:
- Loads current language
- Translates all data-i18n elements
- Sets document language
- Observes DOM for dynamic elements

## Language Switching

Users can switch languages using the dropdown in the header. The selection is:
1. Saved to localStorage
2. Page reloads to apply translations
3. All subsequent pages use the selected language

## Troubleshooting

**Translations not showing:**
- Check that i18n module is imported
- Verify translation keys exist in language files
- Ensure initI18n() is called
- Check browser console for errors

**Missing translations:**
- Add missing keys to all language files
- Use English as fallback
- i18n will automatically use English if key not found

**Language not persisting:**
- Check localStorage for 'language' key
- Ensure i18n.setLanguage() is called
- Verify browser allows localStorage

