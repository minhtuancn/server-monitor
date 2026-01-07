# Breadcrumb Navigation Guide

## Overview

The breadcrumb component provides hierarchical navigation showing the user's location within the application.

## Features

- ✅ Automatic page detection
- ✅ Dynamic server name display
- ✅ Mobile-responsive (shows icons only on small screens)
- ✅ i18n support
- ✅ Semantic HTML with ARIA labels
- ✅ Hover effects and animations

## Usage

### 1. Include the Component

Add the breadcrumb component after your header:

```html
<!DOCTYPE html>
<html>
<head>
    <!-- Your head content -->
</head>
<body>
    <!-- Header -->
    <div id="header-placeholder"></div>
    
    <!-- Breadcrumb (add this) -->
    <div id="breadcrumb-placeholder"></div>
    
    <!-- Main content -->
    <main class="main-content">
        <!-- Your content -->
    </main>

    <script type="module">
        import { loadComponents } from '/assets/js/component-loader.js';
        
        // Load header, sidebar, and breadcrumb
        await loadComponents(['header', 'sidebar', 'breadcrumb']);
    </script>
</body>
</html>
```

### 2. Update component-loader.js

Add breadcrumb to the component loader if not already present:

```javascript
const componentPaths = {
    header: '/components/header.html',
    sidebar: '/components/sidebar.html',
    breadcrumb: '/components/breadcrumb.html'  // Add this
};
```

### 3. Automatic Detection

The breadcrumb automatically detects:
- Current page from URL
- Page title from predefined mapping
- Server name from URL parameters or localStorage

No additional configuration needed!

## Page Mapping

Current page mappings (add more as needed):

```javascript
const breadcrumbData = {
    '/dashboard.html': { icon: 'home', text: 'Dashboard' },
    '/server-detail.html': { icon: 'server', text: 'Server Details' },
    '/server-notes.html': { icon: 'sticky-note', text: 'Server Notes' },
    '/terminal.html': { icon: 'terminal', text: 'Terminal' },
    '/settings.html': { icon: 'cog', text: 'Settings' },
    // Add more pages here
};
```

## Server Context

For server-specific pages, the breadcrumb will show:

```
Dashboard / Server Name / Current Page
```

Example: `Dashboard / Production Server / Server Details`

This works automatically if:
1. URL has `?id=123&name=Production Server` parameters, OR
2. Server name is stored in localStorage as `server_123_name`

## Customization

### Change Separator

Edit the CSS in `breadcrumb.html`:

```css
.breadcrumb-item:not(:last-child)::after {
    content: '>';  /* Change from '/' to '>' */
    /* ... */
}
```

### Add Custom Page

Add to the `breadcrumbData` object:

```javascript
'/my-page.html': { 
    icon: 'chart-line',  // Font Awesome icon name
    text: 'My Custom Page' 
}
```

### Style Overrides

Override in your page-specific CSS:

```css
.breadcrumb-nav {
    background: #custom-color;
}

.breadcrumb-item a {
    color: #custom-color;
}
```

## Mobile Behavior

On screens < 768px:
- Only icons are shown (text hidden)
- Maintains full functionality
- Touch-friendly spacing

## Accessibility

- Uses semantic `<nav>` with `aria-label="Breadcrumb"`
- Ordered list for proper structure
- Active item marked with `.active` class
- Keyboard navigable

## Examples

### Basic Page

```html
<!-- dashboard.html -->
<!-- Breadcrumb hidden on home page -->
```

### Settings Page

```html
<!-- settings.html -->
<!-- Shows: Dashboard / Settings -->
```

### Server Detail

```html
<!-- server-detail.html?id=5&name=Production -->
<!-- Shows: Dashboard / Production / Server Details -->
```

### Server Notes

```html
<!-- server-notes.html?id=5 -->
<!-- Shows: Dashboard / Production Server / Server Notes -->
<!-- (Name retrieved from localStorage if not in URL) -->
```

## Integration Checklist

- [ ] Add breadcrumb placeholder to HTML
- [ ] Update component-loader.js
- [ ] Test navigation on each page
- [ ] Verify mobile responsive behavior
- [ ] Check server context pages
- [ ] Test with i18n language switching

## Troubleshooting

### Breadcrumb Not Showing

1. Check if `#breadcrumb-placeholder` div exists
2. Verify component-loader is loading breadcrumb
3. Check browser console for errors
4. Ensure `/components/breadcrumb.html` is accessible

### Server Name Not Showing

1. Verify URL has `?name=` parameter OR
2. Check localStorage has `server_{id}_name` key
3. Ensure server ID matches in URL and localStorage

### Styles Not Applied

1. Verify breadcrumb.html is loaded
2. Check CSS variables are defined in themes.css
3. Look for CSS conflicts in browser DevTools

---

**Created:** 2026-01-07  
**Component:** breadcrumb.html  
**Location:** frontend/components/
