/* ============================================
   Server Monitor v4.0 - Form Helper Utilities
   Enhanced form handling with loading states and validation
   ============================================ */

import { showToast } from './utils.js';

/**
 * Add loading state to a button during async operation
 * @param {HTMLElement} button - Button element to add loading state
 * @param {Function} asyncFn - Async function to execute
 * @param {string} loadingText - Optional text to show during loading
 */
export async function withLoading(button, asyncFn, loadingText = 'Processing...') {
  const originalText = button.innerHTML;
  const originalDisabled = button.disabled;
  
  try {
    // Set loading state
    button.disabled = true;
    button.innerHTML = `
      <span class="spinner" style="margin-right: 8px;"></span>
      ${loadingText}
    `;
    
    // Execute async function
    const result = await asyncFn();
    
    return result;
  } finally {
    // Restore original state
    button.disabled = originalDisabled;
    button.innerHTML = originalText;
  }
}

/**
 * Wrap form submission with loading state and error handling
 * @param {HTMLFormElement} form - Form element
 * @param {Function} submitHandler - Async function to handle form submission
 * @param {Object} options - Optional configuration
 */
export function setupFormWithLoading(form, submitHandler, options = {}) {
  const {
    submitButton = form.querySelector('button[type="submit"]'),
    loadingText = 'Submitting...',
    successMessage = 'Success!',
    onSuccess = null,
    onError = null
  } = options;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!submitButton) {
      console.error('Submit button not found');
      return;
    }

    try {
      const result = await withLoading(submitButton, async () => {
        return await submitHandler(new FormData(form));
      }, loadingText);

      // Show success toast
      if (successMessage) {
        showToast(successMessage, 'success');
      }

      // Call success callback
      if (onSuccess) {
        onSuccess(result);
      }

      return result;
    } catch (error) {
      console.error('Form submission error:', error);
      
      // Show error toast
      showToast(error.message || 'An error occurred', 'danger');

      // Call error callback
      if (onError) {
        onError(error);
      }

      throw error;
    }
  });
}

/**
 * Add real-time validation to form fields
 * @param {HTMLElement} field - Input field element
 * @param {Function} validator - Validation function that returns {valid: boolean, message: string}
 */
export function addFieldValidation(field, validator) {
  const errorElement = document.createElement('div');
  errorElement.className = 'field-error';
  errorElement.style.cssText = 'color: var(--danger); font-size: 0.875rem; margin-top: 4px; display: none;';
  
  // Insert error element after field
  field.parentNode.insertBefore(errorElement, field.nextSibling);

  const validate = () => {
    const result = validator(field.value);
    
    if (!result.valid) {
      field.classList.add('error');
      errorElement.textContent = result.message;
      errorElement.style.display = 'block';
    } else {
      field.classList.remove('error');
      errorElement.style.display = 'none';
    }

    return result.valid;
  };

  // Validate on blur
  field.addEventListener('blur', validate);
  
  // Clear error on focus
  field.addEventListener('focus', () => {
    field.classList.remove('error');
    errorElement.style.display = 'none';
  });

  // Return validate function for manual validation
  return validate;
}

/**
 * Common validators
 */
export const validators = {
  required: (value) => ({
    valid: value.trim().length > 0,
    message: 'This field is required'
  }),

  email: (value) => ({
    valid: /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    message: 'Please enter a valid email address'
  }),

  ip: (value) => {
    const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!ipPattern.test(value)) {
      return { valid: false, message: 'Invalid IP format (e.g., 192.168.1.1)' };
    }
    const octets = value.split('.');
    const valid = octets.every(octet => {
      const num = parseInt(octet);
      return num >= 0 && num <= 255;
    });
    return {
      valid,
      message: valid ? '' : 'IP octets must be between 0 and 255'
    };
  },

  port: (value) => {
    const port = parseInt(value);
    return {
      valid: !isNaN(port) && port >= 1 && port <= 65535,
      message: 'Port must be between 1 and 65535'
    };
  },

  hostname: (value) => {
    const hostnamePattern = /^[a-zA-Z0-9.-]+$/;
    return {
      valid: hostnamePattern.test(value) && value.length <= 255,
      message: 'Invalid hostname format'
    };
  },

  minLength: (min) => (value) => ({
    valid: value.length >= min,
    message: `Must be at least ${min} characters`
  }),

  maxLength: (max) => (value) => ({
    valid: value.length <= max,
    message: `Must be no more than ${max} characters`
  })
};

/**
 * Show loading overlay on entire page
 */
export function showPageLoading(message = 'Loading...') {
  let overlay = document.querySelector('.page-loading-overlay');
  
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'page-loading-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      color: white;
      font-size: 1.2rem;
    `;
    overlay.innerHTML = `
      <div class="spinner-lg"></div>
      <div style="margin-top: 1rem;">${message}</div>
    `;
    document.body.appendChild(overlay);
  }

  overlay.style.display = 'flex';
  return overlay;
}

/**
 * Hide loading overlay
 */
export function hidePageLoading() {
  const overlay = document.querySelector('.page-loading-overlay');
  if (overlay) {
    overlay.style.display = 'none';
  }
}

/**
 * Confirm action with dialog
 * @param {string} message - Confirmation message
 * @param {string} confirmText - Confirm button text
 * @param {string} cancelText - Cancel button text
 * @returns {Promise<boolean>} - True if confirmed
 */
export async function confirm(message, confirmText = 'Confirm', cancelText = 'Cancel') {
  return new Promise((resolve) => {
    const dialog = document.createElement('div');
    dialog.className = 'confirm-dialog-overlay';
    dialog.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
    `;

    dialog.innerHTML = `
      <div style="
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        padding: 2rem;
        max-width: 400px;
        width: 90%;
        box-shadow: var(--shadow-xl);
      ">
        <div style="margin-bottom: 1.5rem; font-size: 1.1rem; color: var(--text-primary);">
          ${message}
        </div>
        <div style="display: flex; gap: 1rem; justify-content: flex-end;">
          <button class="btn btn-secondary cancel-btn" style="min-width: 80px;">
            ${cancelText}
          </button>
          <button class="btn btn-primary confirm-btn" style="min-width: 80px;">
            ${confirmText}
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(dialog);

    dialog.querySelector('.confirm-btn').addEventListener('click', () => {
      dialog.remove();
      resolve(true);
    });

    dialog.querySelector('.cancel-btn').addEventListener('click', () => {
      dialog.remove();
      resolve(false);
    });

    // Close on overlay click
    dialog.addEventListener('click', (e) => {
      if (e.target === dialog) {
        dialog.remove();
        resolve(false);
      }
    });
  });
}

export default {
  withLoading,
  setupFormWithLoading,
  addFieldValidation,
  validators,
  showPageLoading,
  hidePageLoading,
  confirm
};
