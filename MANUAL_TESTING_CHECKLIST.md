# Manual Testing Checklist - Mobile Responsive & Accessibility

## 📋 Pre-Test Setup

### Requirements:
- ✅ Server Monitor running on http://172.22.0.103:9081
- ✅ Login credentials: admin / admin123
- ✅ Test devices or browser DevTools

### Test Browsers:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

---

## 📱 Mobile Responsive Testing

### Test Viewport Sizes:

#### 1. iPhone SE (320px × 568px) - MINIMUM SIZE ⚠️
- [ ] Dashboard loads without horizontal scroll
- [ ] Servers list shows mobile cards (not table)
- [ ] Server detail page tabs scroll horizontally
- [ ] Terminal page loads correctly
- [ ] Users page form is full-width
- [ ] Audit logs show mobile cards
- [ ] SSH Keys settings show mobile cards
- [ ] Groups settings show mobile cards with scrollable tabs
- [ ] Email settings form is full-width
- [ ] Domain settings form is full-width
- [ ] Database settings show mobile cards for backups
- [ ] Health dashboard cards stack vertically

**Critical**: No horizontal scroll on ANY page at 320px!

#### 2. iPhone 12 (414px × 896px)
- [ ] All pages load correctly
- [ ] Navigation menu works
- [ ] Forms are usable
- [ ] Buttons are clickable

#### 3. iPad (768px × 1024px)
- [ ] Pages use appropriate layout (cards or table)
- [ ] Tabs are visible and usable
- [ ] Touch targets are adequate

#### 4. Desktop (1920px × 1080px)
- [ ] Desktop tables show (not mobile cards)
- [ ] All features accessible
- [ ] Layout looks professional

---

## ♿ Accessibility Testing

### ARIA Labels Verification:

#### All Pages - Interactive Elements
- [ ] All buttons have `aria-label` attributes
- [ ] All icon buttons have descriptive labels
- [ ] All form inputs have `aria-label` in `inputProps`
- [ ] All switches have `aria-label` in `inputProps`
- [ ] Dynamic labels include item names (e.g., "Delete server-name")

#### Specific Pages:

**Dashboard:**
- [ ] Action buttons have labels

**Servers:**
- [ ] "Add Server" button has label
- [ ] Edit/Delete buttons have dynamic labels with server names
- [ ] Filter/search inputs have labels

**Users:**
- [ ] Username input has label
- [ ] Email input has label
- [ ] Password input has label
- [ ] Role selector has label
- [ ] "Create User" button has label

**Audit Logs:**
- [ ] Filter buttons have labels
- [ ] Export button has label
- [ ] Action buttons on cards have labels

**SSH Keys:**
- [ ] "Add SSH Key" button has label
- [ ] Edit buttons have dynamic labels with key names
- [ ] Delete buttons have dynamic labels with key names

**Groups:**
- [ ] "Add Group" button has label
- [ ] Color picker buttons have labels (e.g., "Select red color")
- [ ] Color picker has `aria-pressed` attribute
- [ ] Edit/Delete buttons have dynamic labels

**Email Settings:**
- [ ] "Enable email alerts" switch has label
- [ ] SMTP host input has label
- [ ] SMTP port input has label
- [ ] Username input has label
- [ ] Password input has label
- [ ] Recipients input has label
- [ ] "Save Settings" button has label

**Domain Settings:**
- [ ] Domain name input has label
- [ ] "Enable SSL/TLS" switch has label
- [ ] SSL type selector has label
- [ ] "Auto Renew" switch has label
- [ ] Certificate path input has label
- [ ] Private key path input has label
- [ ] "Save Settings" button has label

**Database Settings:**
- [ ] "Create Backup" button has label
- [ ] Restore buttons have labels
- [ ] Delete buttons have labels

**Health Dashboard:**
- [ ] Auto-refresh toggle has label
- [ ] "Refresh" button has label

---

## ⌨️ Keyboard Navigation Testing

### Tab Navigation:
- [ ] **Login Page**: Tab through username → password → login button
- [ ] **Dashboard**: Tab through navigation and action buttons
- [ ] **All Pages**: Can reach all interactive elements with Tab key
- [ ] **Forms**: Tab order is logical (top to bottom, left to right)

### Keyboard Actions:
- [ ] **Enter Key**: Activates focused buttons
- [ ] **Space Key**: Toggles switches and checkboxes
- [ ] **Escape Key**: Closes dialogs/modals
- [ ] **Arrow Keys**: Navigate through select dropdowns

### Color Picker (Groups Page):
- [ ] Color picker can be focused with Tab
- [ ] Enter key selects color
- [ ] Space key selects color
- [ ] Focus outline is visible

### Dialogs:
- [ ] Escape key closes "Add" dialogs
- [ ] Escape key closes "Edit" dialogs
- [ ] Escape key closes ConfirmDialog
- [ ] Tab cycles through dialog buttons

---

## 👆 Touch Target Testing

Use browser DevTools or ruler to verify sizes:

### Minimum Sizes:
- **Buttons**: ≥44px × 44px
- **Icon Buttons**: ≥44px × 44px
- **Form Inputs**: ≥40px height
- **Switches**: ≥38px × 38px
- **Color Pickers**: ≥40px × 40px

### Pages to Check:

#### Dashboard:
- [ ] All icon buttons are ≥44px

#### Servers:
- [ ] "Add Server" button is ≥44px
- [ ] Edit/Delete buttons on mobile cards are ≥44px

#### SSH Keys:
- [ ] "Add SSH Key" button is ≥44px
- [ ] Action buttons on mobile cards are ≥44px

#### Groups:
- [ ] "Add Group" button is ≥44px
- [ ] Color picker swatches are ≥40px
- [ ] Edit/Delete buttons are ≥44px

#### All Forms:
- [ ] Text inputs are ≥40px tall
- [ ] Buttons are ≥44px tall

---

## 🚫 No Browser confirm() Testing

**Critical**: App should NEVER use browser `confirm()` dialog

### Test Delete Actions:
- [ ] **SSH Keys**: Delete key shows ConfirmDialog (not browser confirm)
- [ ] **Groups**: Delete group shows ConfirmDialog
- [ ] **Servers**: Delete server shows ConfirmDialog
- [ ] **All deletes**: Custom dialog with Cancel and Confirm buttons

### Visual Check:
- ConfirmDialog should have:
  - Title (e.g., "Delete SSH Key")
  - Message with item name
  - Cancel button (gray)
  - Confirm button (red for delete)
  - Loading state when processing

---

## 🔊 Screen Reader Testing (Optional)

If you have screen reader available:

### macOS VoiceOver:
```bash
# Enable: Cmd + F5
# Navigate: Control + Option + Arrow keys
```

### Windows Narrator:
```bash
# Enable: Windows + Ctrl + Enter
# Navigate: Caps Lock + Arrow keys
```

### Tests:
- [ ] Page headings are announced
- [ ] Button labels are read correctly
- [ ] Form input labels are read
- [ ] Landmarks (nav, main) are detected

---

## 📸 Screenshot Testing

Take screenshots at each viewport for documentation:

### Screenshots Needed:
- [ ] Dashboard at 320px
- [ ] Servers list (mobile cards) at 320px
- [ ] SSH Keys (mobile cards) at 320px
- [ ] Groups page with color picker at 320px
- [ ] Forms at 320px
- [ ] Same pages at 768px (tablet)
- [ ] Same pages at 1920px (desktop)

---

## ✅ Pass/Fail Criteria

### Must Pass:
- ✅ No horizontal scroll at 320px width on ANY page
- ✅ All interactive elements have ARIA labels
- ✅ Tab navigation works on all pages
- ✅ Touch targets meet 44px minimum (40px for inputs)
- ✅ No browser confirm() usage (only ConfirmDialog)
- ✅ All pages load without errors

### Should Pass:
- ✅ Color picker is keyboard accessible
- ✅ Forms are usable on mobile
- ✅ Mobile cards display data clearly
- ✅ Tabs scroll on mobile

---

## 🐛 Issues to Report

If you find issues, document:

1. **Page**: Which page has the issue
2. **Viewport**: Screen size where issue occurs (e.g., 320px)
3. **Element**: Which element has the issue
4. **Issue**: What's wrong (horizontal scroll, missing label, etc.)
5. **Screenshot**: Visual proof
6. **Steps**: How to reproduce

### Example Issue Report:
```
Page: Servers List
Viewport: 320px width
Element: "Add Server" button
Issue: Button has no aria-label
Screenshot: [attached]
Steps:
1. Open servers page
2. Inspect "Add Server" button
3. No aria-label attribute found
```

---

## 📊 Testing Report Template

After testing, fill out this report:

```markdown
# Manual Testing Report - v2.4.0

**Tester**: [Your Name]
**Date**: [Date]
**Duration**: [Time spent]

## Mobile Responsive (10 pages × 4 viewports = 40 tests)
- [ ] Dashboard: ✅ Pass / ❌ Fail - [Notes]
- [ ] Servers: ✅ Pass / ❌ Fail - [Notes]
- [ ] Users: ✅ Pass / ❌ Fail - [Notes]
- [ ] Audit Logs: ✅ Pass / ❌ Fail - [Notes]
- [ ] Terminal: ✅ Pass / ❌ Fail - [Notes]
- [ ] SSH Keys: ✅ Pass / ❌ Fail - [Notes]
- [ ] Groups: ✅ Pass / ❌ Fail - [Notes]
- [ ] Email: ✅ Pass / ❌ Fail - [Notes]
- [ ] Domain: ✅ Pass / ❌ Fail - [Notes]
- [ ] Database: ✅ Pass / ❌ Fail - [Notes]
- [ ] Health: ✅ Pass / ❌ Fail - [Notes]

## Accessibility (ARIA Labels)
- [ ] All buttons labeled: ✅ Pass / ❌ Fail
- [ ] All inputs labeled: ✅ Pass / ❌ Fail
- [ ] No browser confirm(): ✅ Pass / ❌ Fail

## Keyboard Navigation
- [ ] Tab navigation: ✅ Pass / ❌ Fail
- [ ] Enter/Space keys: ✅ Pass / ❌ Fail
- [ ] Escape key: ✅ Pass / ❌ Fail
- [ ] Color picker: ✅ Pass / ❌ Fail

## Touch Targets
- [ ] All targets ≥44px: ✅ Pass / ❌ Fail

## Issues Found
[List any issues with details]

## Overall Result
- ✅ PASS - Ready for production
- ⚠️ PASS with minor issues - [list issues]
- ❌ FAIL - [critical issues blocking production]

## Recommendations
[Any suggestions for improvement]
```

---

## ⏱️ Estimated Testing Time

- **Quick Test** (critical paths only): 30 minutes
- **Standard Test** (all pages, main viewports): 1-2 hours
- **Comprehensive Test** (all checks + screen reader): 3-4 hours

---

## 🎯 Priority Order

If time is limited, test in this order:

1. **Critical**: 320px width (no horizontal scroll) - 15 min
2. **High**: ARIA labels on all pages - 30 min
3. **High**: Keyboard navigation - 15 min
4. **Medium**: Touch targets - 15 min
5. **Medium**: Other viewports (768px, 1920px) - 30 min
6. **Low**: Screen reader testing - 30 min

---

**Happy Testing! 🧪**

Questions? See `SESSION_3_FINAL_REPORT.md` or `e2e-tests/README.md`
