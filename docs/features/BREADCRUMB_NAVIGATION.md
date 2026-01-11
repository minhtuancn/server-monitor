# Breadcrumb Navigation

**Version:** 2.4.0
**Last Updated:** 2026-01-11
**Status:** ✅ Implemented

---

## Overview

Breadcrumb navigation provides users with a visual hierarchy of their current location within the application. It improves navigation and user experience by showing the path from the dashboard to the current page.

## Features

- **Automatic Path Detection**: Dynamically generates breadcrumbs based on current URL
- **Clickable Navigation**: All breadcrumb items (except current page) are clickable
- **Home Icon**: Dashboard home includes a home icon for visual clarity
- **Smart Labels**: Route segments are automatically labeled with human-readable names
- **ID Detection**: Numeric IDs (e.g., server IDs) are displayed as "Server #123"
- **Responsive Design**: Breadcrumbs adapt to mobile, tablet, and desktop screens
- **Text Truncation**: Long labels are truncated with ellipsis on small screens
- **Accessibility**: Full ARIA labels and semantic HTML
- **Conditional Display**: Hidden on login/setup pages and when only one level deep

---

## Implementation

### Component Location

**File**: `frontend-next/src/components/layout/Breadcrumbs.tsx`

### Integration

Breadcrumbs are integrated into the main app layout:

**File**: `frontend-next/src/components/layout/AppShell.tsx`

```tsx
<Box>
  <Breadcrumbs />
  <Box component="main">
    {children}
  </Box>
</Box>
```

---

## Route Label Mappings

The component includes predefined labels for common routes:

| Route Segment | Display Label |
|---------------|---------------|
| `dashboard` | Dashboard |
| `servers` | Servers |
| `terminal` | Terminal |
| `notifications` | Notifications |
| `users` | Users |
| `settings` | Settings |
| `audit-logs` | Audit Logs |
| `system-check` | System Check |
| `database` | Database |
| `health` | System Health |
| `domain` | Domain & SSL |
| `email` | Email |
| `ssh-keys` | SSH Keys |
| `webhooks` | Webhooks |
| `groups` | Server Groups |
| `sessions` | Terminal Sessions |

For unlisted routes, the component automatically capitalizes and formats the segment (e.g., `my-page` → `My Page`).

---

## Usage Examples

### Example 1: Server Detail Page

**URL**: `/en/servers/42`

**Breadcrumbs Display**:
```
🏠 Dashboard > Servers > Server #42
```

### Example 2: Settings Nested Page

**URL**: `/en/settings/ssh-keys`

**Breadcrumbs Display**:
```
🏠 Dashboard > Settings > SSH Keys
```

### Example 3: System Health

**URL**: `/en/settings/health`

**Breadcrumbs Display**:
```
🏠 Dashboard > Settings > System Health
```

---

## Responsive Behavior

### Desktop (> 960px)
- All breadcrumb labels visible
- Maximum label width: 300px
- Full separator icons

### Tablet (600px - 960px)
- Truncated labels at 200px max width
- Full functionality maintained

### Mobile (< 600px)
- Truncated labels at 150px max width (100px for non-last items)
- Home icon still visible
- Scrollable if needed (flexWrap: nowrap)

---

## Accessibility Features

### ARIA Labels

```html
<nav role="navigation" aria-label="breadcrumb">
  <ol aria-label="breadcrumb navigation">
    <li>
      <a href="/dashboard">Dashboard</a>
    </li>
    <li aria-current="page">
      Current Page
    </li>
  </ol>
</nav>
```

### Keyboard Navigation

- All breadcrumb links are keyboard accessible (Tab key)
- Enter/Space activates links
- Screen readers announce "breadcrumb navigation"
- Current page marked with `aria-current="page"`

---

## Styling

### Visual Design

- **Background**: Matches app paper background
- **Border**: Bottom border for visual separation
- **Padding**: Responsive padding (2-3 units)
- **Separators**: NavigateNext icon (›)
- **Colors**:
  - Clickable links: Inherit theme color with hover underline
  - Current page: Primary text color, bold (500 weight)

### Dark Mode Support

Breadcrumbs automatically adapt to theme:
- Light mode: Dark text on light background
- Dark mode: Light text on dark background

---

## Customization

### Adding New Route Labels

Edit `Breadcrumbs.tsx` and add to the `routeLabels` object:

```tsx
const routeLabels: Record<string, string> = {
  // ... existing labels
  "my-new-route": "My Custom Label",
};
```

### Hiding Breadcrumbs on Specific Routes

Modify the hide logic in `Breadcrumbs.tsx`:

```tsx
// Don't show breadcrumbs on these pages
if (pathname?.includes("/login") ||
    pathname?.includes("/setup") ||
    pathname?.includes("/my-custom-page")) {
  return null;
}
```

---

## Technical Details

### Dependencies

- `@mui/material`: Breadcrumbs, Link, Typography components
- `@mui/icons-material`: NavigateNextIcon, HomeIcon
- `next/navigation`: usePathname, useParams hooks

### Performance

- **Render Time**: < 1ms (pure client-side calculation)
- **Re-renders**: Only when pathname changes
- **Memory**: Minimal (~5KB component size)

### Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Android Chrome)
- IE11 not supported (Next.js 16 requirement)

---

## Testing

### Manual Testing Checklist

- [ ] Navigate to dashboard → breadcrumb shows "Dashboard" only
- [ ] Navigate to /servers → breadcrumb shows "Dashboard > Servers"
- [ ] Navigate to /servers/123 → breadcrumb shows "Dashboard > Servers > Server #123"
- [ ] Click on "Dashboard" breadcrumb → navigates to dashboard
- [ ] Click on "Servers" breadcrumb → navigates to servers list
- [ ] Current page breadcrumb is not clickable
- [ ] Test on mobile (< 600px width) → labels truncate properly
- [ ] Test in dark mode → colors adapt correctly
- [ ] Test keyboard navigation → Tab through breadcrumbs
- [ ] Test screen reader → announces "breadcrumb navigation"

### Automated Testing

Currently manual testing only. Future: Add Playwright E2E tests.

---

## Troubleshooting

### Breadcrumbs Not Showing

**Issue**: Breadcrumbs don't appear on a page

**Solutions**:
1. Check if page is login/setup (intentionally hidden)
2. Verify pathname depth (hidden if only one level)
3. Check AppShell integration is correct
4. Inspect browser console for React errors

### Incorrect Labels

**Issue**: Route segment shows wrong label

**Solutions**:
1. Add custom label to `routeLabels` mapping
2. Check if segment contains special characters
3. Verify route naming convention

### Truncation Too Aggressive

**Issue**: Labels cut off too early on desktop

**Solutions**:
1. Adjust `maxWidth` in Breadcrumbs.tsx:
   ```tsx
   maxWidth: { xs: "150px", sm: "250px", md: "400px" }
   ```

---

## Future Enhancements

Potential improvements for future versions:

1. **i18n Support**: Translate breadcrumb labels based on locale
2. **Custom Icons**: Allow per-route custom icons
3. **Dynamic Labels**: Fetch server names/titles for IDs
4. **Collapsible Breadcrumbs**: Show "..." for very long paths
5. **Breadcrumb Schema**: Add structured data for SEO

---

## Related Documentation

- [Navigation](../architecture/NAVIGATION.md) - App navigation structure
- [Accessibility](../architecture/ACCESSIBILITY.md) - Accessibility standards
- [UI Components](../architecture/UI_COMPONENTS.md) - MUI component usage

---

## Changelog

### v2.4.0 (2026-01-11)
- ✅ Initial implementation
- ✅ Responsive design
- ✅ Accessibility features
- ✅ Route label mappings

---

**Questions or Issues?**

- GitHub Issues: [github.com/minhtuancn/server-monitor/issues](https://github.com/minhtuancn/server-monitor/issues)
- Documentation: [docs/README.md](../README.md)
