# Frontend Structure - Server Monitor

## Overview
Clean, organized frontend with 14 functional pages (reduced from 25+ after removing duplicates).

## Main Pages

### Authentication
- **login.html** - User login page
- **index.html** - Landing page (redirects to dashboard)

### Core Dashboard
- **dashboard.html** - Main multi-server monitoring dashboard (PRIMARY)
  - Real-time server stats
  - Server grid view
  - Quick actions
  - Navigation to all features

### Server Management
- **server-detail.html** - Individual server details and monitoring
- **server-notes.html** - Markdown notes for servers

### Configuration Pages
- **settings.html** - System settings
- **domain-settings.html** - Domain & SSL configuration
- **email-settings.html** - Email alert configuration
- **ssh-keys.html** - SSH key management

### Tools
- **terminal.html** - Web-based SSH terminal (xterm.js)
- **notifications.html** - Alert notifications management

### Admin
- **users.html** - User management (admin only)
- **system-check.html** - System health check

### Testing
- **test_cors.html** - CORS configuration testing

## Assets Structure

```
frontend/
├── assets/
│   ├── css/
│   │   ├── app.css          - Main application styles
│   │   ├── components.css   - Reusable component styles
│   │   └── themes.css       - Light/dark theme definitions
│   ├── js/
│   │   ├── api.js           - API client wrapper
│   │   ├── auth.js          - Authentication helpers
│   │   ├── i18n.js          - Internationalization
│   │   ├── utils.js         - Utility functions
│   │   └── component-loader.js - Dynamic component loading
│   └── locales/
│       ├── en.json          - English translations
│       ├── vi.json          - Vietnamese translations
│       └── [6 other languages]
└── components/
    ├── header.html          - Shared header component
    └── sidebar.html         - Shared sidebar navigation

```

## Cleanup History

**Date:** 2026-01-07

### Removed Files (Duplicates/Backups)
- `backup/` directory (3 files)
  - `dashboard-v1.html`
  - `dashboard-v2.html`
  - `dashboard.html`
- `dashboard-old.html` - Outdated version
- `dashboard-old2.html` - Outdated version
- `dashboard-final.html` - Duplicate of main dashboard
- `dashboard-iframe.html` - Unused iframe version
- `dashboard-dynamic.html` - Duplicate functionality
- `dashboard-sidebar.html` - Merged into main dashboard

**Result:** Reduced from 25+ files to 14 clean, functional pages

### Why Cleaned Up
1. **Maintenance burden** - Multiple similar dashboards confusing
2. **Code duplication** - Same features in multiple files
3. **Version confusion** - Unclear which version is active
4. **Size reduction** - Smaller codebase easier to maintain

## Navigation Flow

```
index.html (landing)
    ↓
login.html (if not authenticated)
    ↓
dashboard.html (main hub)
    ├─→ server-detail.html (view server)
    ├─→ server-notes.html (notes)
    ├─→ terminal.html (SSH access)
    ├─→ settings.html (config)
    ├─→ domain-settings.html (SSL)
    ├─→ email-settings.html (alerts)
    ├─→ ssh-keys.html (keys)
    ├─→ users.html (admin)
    └─→ notifications.html (alerts)
```

## Development Guidelines

### Adding New Pages
1. Follow naming convention: `feature-name.html`
2. Use shared components (header, sidebar)
3. Include i18n support
4. Add to this README

### Before Creating "Backup" Files
**DON'T** create files like:
- `page-old.html`
- `page-backup.html`
- `page-v2.html`

**DO** use Git for version control:
```bash
git checkout <commit> -- path/to/file.html  # Restore old version
git diff <commit>                            # Compare versions
```

### Testing Changes
Always test navigation flow after changes:
1. Login flow
2. Dashboard loading
3. Navigation between pages
4. Logout/session handling

## Internationalization

Supported languages (8):
- English (en)
- Vietnamese (vi)
- Chinese Simplified (zh-CN)
- Japanese (ja)
- Korean (ko)
- Spanish (es)
- French (fr)
- German (de)

Translation files: `assets/locales/{lang}.json`

## Components

### Shared Components
Located in `components/` directory:
- **header.html** - Top navigation bar
- **sidebar.html** - Left sidebar menu

### Loading Components
Use `component-loader.js` to dynamically load shared components:
```javascript
// Load header and sidebar
loadComponents(['header', 'sidebar']);
```

## Best Practices

1. **Single Source of Truth** - One file per feature
2. **Component Reuse** - Use shared components
3. **Clean URLs** - Descriptive filenames
4. **Git for Versions** - No `-old` or `-backup` files
5. **Documentation** - Update this README when adding pages

## Testing

### Manual Testing Checklist
- [ ] All pages load without errors
- [ ] Navigation works between pages
- [ ] Authentication redirects work
- [ ] Components load correctly
- [ ] i18n language switching works
- [ ] Mobile responsive design
- [ ] Dark/light theme switching

### CORS Testing
Use `test_cors.html` to verify:
- API endpoint accessibility
- CORS headers configured
- Authentication flow

---

**Last Updated:** 2026-01-07  
**Pages:** 14 functional pages  
**Components:** 2 shared components  
**Languages:** 8 supported
