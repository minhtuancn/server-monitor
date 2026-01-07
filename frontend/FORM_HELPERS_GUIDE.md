# Form Helper Usage Guide

## Overview

The `form-helpers.js` module provides enhanced form handling with:
- Loading states during async operations
- Real-time field validation
- Toast notifications for success/error
- Confirmation dialogs
- Page-level loading overlay

## Quick Start

### 1. Basic Form with Loading State

```javascript
import { setupFormWithLoading } from '/assets/js/form-helpers.js';
import api from '/assets/js/api.js';

const form = document.querySelector('#myForm');

setupFormWithLoading(form, async (formData) => {
  // Your async submission logic
  const data = {
    name: formData.get('name'),
    email: formData.get('email')
  };
  
  const response = await api.post('/api/endpoint', data);
  return response;
}, {
  loadingText: 'Saving...',
  successMessage: 'Settings saved successfully!',
  onSuccess: (result) => {
    console.log('Success:', result);
    // Additional actions after success
  },
  onError: (error) => {
    console.error('Error:', error);
    // Additional error handling
  }
});
```

### 2. Button with Loading State

```javascript
import { withLoading } from '/assets/js/form-helpers.js';

const button = document.querySelector('#saveButton');

button.addEventListener('click', async () => {
  await withLoading(button, async () => {
    // Your async operation
    await api.post('/api/save', data);
  }, 'Saving...');
});
```

### 3. Real-time Field Validation

```javascript
import { addFieldValidation, validators } from '/assets/js/form-helpers.js';

const emailField = document.querySelector('#email');
const ipField = document.querySelector('#ip');
const portField = document.querySelector('#port');

// Email validation
addFieldValidation(emailField, validators.email);

// IP validation
addFieldValidation(ipField, validators.ip);

// Port validation
addFieldValidation(portField, validators.port);

// Custom validation
addFieldValidation(document.querySelector('#username'), (value) => {
  if (value.length < 3) {
    return { valid: false, message: 'Username must be at least 3 characters' };
  }
  return { valid: true, message: '' };
});
```

### 4. Confirmation Dialog

```javascript
import { confirm } from '/assets/js/form-helpers.js';

async function deleteServer(serverId) {
  const confirmed = await confirm(
    'Are you sure you want to delete this server?',
    'Delete',
    'Cancel'
  );
  
  if (confirmed) {
    await api.delete(`/api/servers/${serverId}`);
    showToast('Server deleted', 'success');
  }
}
```

### 5. Page Loading Overlay

```javascript
import { showPageLoading, hidePageLoading } from '/assets/js/form-helpers.js';

async function loadData() {
  showPageLoading('Loading servers...');
  
  try {
    const servers = await api.get('/api/servers');
    renderServers(servers);
  } finally {
    hidePageLoading();
  }
}
```

## Complete Example: Email Settings Form

```html
<form id="emailConfigForm">
  <div class="form-group">
    <label for="smtp_host">SMTP Host</label>
    <input type="text" id="smtp_host" name="smtp_host" required>
  </div>

  <div class="form-group">
    <label for="smtp_port">SMTP Port</label>
    <input type="number" id="smtp_port" name="smtp_port" required>
  </div>

  <div class="form-group">
    <label for="smtp_user">SMTP Username</label>
    <input type="email" id="smtp_user" name="smtp_user" required>
  </div>

  <button type="submit" class="btn btn-primary">Save Settings</button>
</form>

<script type="module">
  import { setupFormWithLoading, addFieldValidation, validators } from '/assets/js/form-helpers.js';
  import api from '/assets/js/api.js';

  const form = document.querySelector('#emailConfigForm');

  // Add validation
  addFieldValidation(
    document.querySelector('#smtp_user'),
    validators.email
  );
  
  addFieldValidation(
    document.querySelector('#smtp_port'),
    validators.port
  );

  // Setup form with loading
  setupFormWithLoading(form, async (formData) => {
    const config = {
      smtp_host: formData.get('smtp_host'),
      smtp_port: parseInt(formData.get('smtp_port')),
      smtp_user: formData.get('smtp_user')
    };
    
    return await api.post('/api/email/config', config);
  }, {
    loadingText: 'Saving configuration...',
    successMessage: 'Email settings saved!',
    onSuccess: () => {
      // Redirect or update UI
      console.log('Settings saved');
    }
  });
</script>
```

## Available Validators

### Built-in Validators

```javascript
import { validators } from '/assets/js/form-helpers.js';

// Required field
validators.required(value)

// Email format
validators.email(value)

// IP address (0-255 per octet)
validators.ip(value)

// Port number (1-65535)
validators.port(value)

// Hostname format
validators.hostname(value)

// Minimum length
validators.minLength(8)(value)  // At least 8 chars

// Maximum length
validators.maxLength(100)(value)  // Max 100 chars
```

### Custom Validators

```javascript
// Custom validator function
const customValidator = (value) => {
  const valid = /* your validation logic */;
  return {
    valid: valid,
    message: valid ? '' : 'Error message'
  };
};

addFieldValidation(field, customValidator);
```

## CSS Classes

### Form States

```css
/* Error state - added automatically */
input.error {
  border-color: var(--danger);
  background-color: rgba(239, 68, 68, 0.05);
}

/* Success state */
input.success {
  border-color: var(--success);
  background-color: rgba(16, 185, 129, 0.05);
}

/* Error message - shown automatically */
.field-error {
  color: var(--danger);
  font-size: 0.875rem;
  margin-top: 4px;
}
```

### Loading States

```html
<!-- Button with spinner -->
<button class="btn btn-primary">
  <span class="spinner"></span>
  Loading...
</button>

<!-- Large spinner -->
<div class="spinner-lg"></div>
```

## Best Practices

### 1. Always Use Loading States

```javascript
// ❌ Bad - No feedback during async operation
button.addEventListener('click', async () => {
  await api.post('/api/save', data);
});

// ✅ Good - User sees loading indicator
button.addEventListener('click', async () => {
  await withLoading(button, async () => {
    await api.post('/api/save', data);
  }, 'Saving...');
});
```

### 2. Validate Before Submission

```javascript
// ✅ Good - Validate before submitting
const validators = [
  addFieldValidation(emailField, validators.email),
  addFieldValidation(portField, validators.port)
];

form.addEventListener('submit', (e) => {
  const allValid = validators.every(validate => validate());
  if (!allValid) {
    e.preventDefault();
    showToast('Please fix errors before submitting', 'danger');
  }
});
```

### 3. Show Meaningful Messages

```javascript
// ❌ Bad - Generic message
successMessage: 'Success!'

// ✅ Good - Specific message
successMessage: 'Email settings saved successfully!'
```

### 4. Handle Errors Gracefully

```javascript
setupFormWithLoading(form, handler, {
  onError: (error) => {
    // Log for debugging
    console.error('Submission error:', error);
    
    // Show user-friendly message
    if (error.message.includes('network')) {
      showToast('Network error. Please check your connection.', 'danger');
    }
  }
});
```

## Migration Guide

### Updating Existing Forms

1. **Add module import:**
   ```javascript
   import { setupFormWithLoading, validators } from '/assets/js/form-helpers.js';
   ```

2. **Replace inline submit handler:**
   ```javascript
   // Old
   form.onsubmit = async (e) => {
     e.preventDefault();
     await submitData();
   };
   
   // New
   setupFormWithLoading(form, async (formData) => {
     return await submitData(formData);
   });
   ```

3. **Add validation:**
   ```javascript
   // Add to form initialization
   addFieldValidation(emailField, validators.email);
   addFieldValidation(portField, validators.port);
   ```

## Troubleshooting

### Validation Not Showing

- Ensure validator returns `{valid: boolean, message: string}`
- Check that field has proper parent element for error insertion
- Verify CSS classes are loaded

### Loading State Not Working

- Ensure button element is passed correctly
- Check that async function is returned from handler
- Verify spinner CSS is loaded

### Toast Not Appearing

- Import `showToast` from utils.js
- Check that toast-container styles are loaded
- Verify z-index is high enough

---

**Created:** 2026-01-07  
**Version:** 1.0.0  
**Module:** form-helpers.js
