/* ============================================
   Server Monitor v4.0 - Utility Functions
   Common helper functions used across pages
   ============================================ */

/**
 * Show toast notification
 */
export function showToast(message, type = 'info', duration = 3000) {
  // Create toast container if it doesn't exist
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  // Create toast element
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  // Icon based on type
  const icons = {
    success: '✓',
    warning: '⚠',
    danger: '✕',
    info: 'ℹ'
  };
  
  toast.innerHTML = `
    <span style="font-size: 1.2rem; font-weight: bold;">${icons[type] || 'ℹ'}</span>
    <span style="flex: 1;">${message}</span>
  `;

  container.appendChild(toast);

  // Auto remove after duration
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(400px)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/**
 * Format date/time
 */
export function formatDate(dateString, includeTime = true) {
  if (!dateString) return 'N/A';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  // Relative time for recent dates
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

  // Formatted date for older dates
  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...(includeTime && { hour: '2-digit', minute: '2-digit' })
  };

  return date.toLocaleDateString('en-US', options);
}

/**
 * Format bytes to human readable size
 */
export function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  if (!bytes) return 'N/A';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Format percentage
 */
export function formatPercent(value, decimals = 1) {
  if (value === null || value === undefined) return 'N/A';
  return `${parseFloat(value).toFixed(decimals)}%`;
}

/**
 * Format uptime
 */
export function formatUptime(seconds) {
  if (!seconds) return 'N/A';

  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);

  return parts.join(' ') || '< 1m';
}

/**
 * Get status color class
 */
export function getStatusColor(status) {
  const colors = {
    online: 'success',
    offline: 'danger',
    warning: 'warning',
    pending: 'info',
    unknown: 'secondary'
  };
  return colors[status?.toLowerCase()] || 'secondary';
}

/**
 * Get status badge HTML
 */
export function getStatusBadge(status) {
  const color = getStatusColor(status);
  return `<span class="badge badge-${color}">${status || 'Unknown'}</span>`;
}

/**
 * Debounce function
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Confirm dialog
 */
export function confirm(message, title = 'Confirm') {
  return new Promise((resolve) => {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
      <div class="modal-dialog">
        <div class="modal-header">
          <h3 class="modal-title">${title}</h3>
        </div>
        <div class="modal-body">
          <p>${message}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-action="cancel">Cancel</button>
          <button class="btn btn-primary" data-action="confirm">Confirm</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Handle button clicks
    modal.addEventListener('click', (e) => {
      const action = e.target.getAttribute('data-action');
      if (action === 'confirm') {
        resolve(true);
        modal.remove();
      } else if (action === 'cancel' || e.target === modal) {
        resolve(false);
        modal.remove();
      }
    });

    // Focus confirm button
    modal.querySelector('[data-action="confirm"]').focus();
  });
}

/**
 * Show loading overlay
 */
export function showLoading(message = 'Loading...') {
  let overlay = document.getElementById('loading-overlay');
  
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      flex-direction: column;
      gap: 1rem;
    `;
    document.body.appendChild(overlay);
  }

  overlay.innerHTML = `
    <div class="spinner spinner-lg"></div>
    <div style="color: white; font-size: 1.1rem;">${message}</div>
  `;
  overlay.style.display = 'flex';
}

/**
 * Hide loading overlay
 */
export function hideLoading() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.style.display = 'none';
  }
}

/**
 * Copy to clipboard
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('Copied to clipboard', 'success', 2000);
    return true;
  } catch (error) {
    console.error('Copy failed:', error);
    showToast('Failed to copy', 'danger', 2000);
    return false;
  }
}

/**
 * Escape HTML to prevent XSS
 */
export function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Parse query string
 */
export function parseQuery(queryString = window.location.search) {
  const params = new URLSearchParams(queryString);
  const result = {};
  for (const [key, value] of params) {
    result[key] = value;
  }
  return result;
}

/**
 * Build query string
 */
export function buildQuery(params) {
  const query = new URLSearchParams(params);
  return query.toString();
}

/**
 * Validate email
 */
export function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

/**
 * Validate IP address
 */
export function isValidIP(ip) {
  const re = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  return re.test(ip);
}

/**
 * Validate port number
 */
export function isValidPort(port) {
  const num = parseInt(port);
  return !isNaN(num) && num >= 1 && num <= 65535;
}

/**
 * Generate random ID
 */
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * Sleep/delay function
 */
export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Load component HTML
 */
export async function loadComponent(elementId, componentPath) {
  try {
    const response = await fetch(componentPath);
    if (!response.ok) {
      throw new Error(`Failed to load component: ${componentPath}`);
    }
    const html = await response.text();
    const element = document.getElementById(elementId);
    if (element) {
      element.innerHTML = html;
    }
  } catch (error) {
    console.error('Load component error:', error);
  }
}

/**
 * Format command for terminal
 */
export function formatCommand(command, variables = {}) {
  let formatted = command;
  for (const [key, value] of Object.entries(variables)) {
    formatted = formatted.replace(new RegExp(`{{${key}}}`, 'g'), value);
  }
  return formatted;
}

/**
 * Get WebSocket URL
 */
export function getWebSocketURL(path) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const hostname = window.location.hostname;
  const port = window.location.port === '9081' ? 9084 : 8084;
  return `${protocol}//${hostname}:${port}${path}`;
}

/**
 * Truncate text
 */
export function truncate(text, length = 50) {
  if (!text) return '';
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
}

/**
 * Pluralize word
 */
export function pluralize(count, singular, plural = null) {
  if (count === 1) return singular;
  return plural || `${singular}s`;
}

/**
 * Sort array of objects by key
 */
export function sortBy(array, key, order = 'asc') {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (aVal < bVal) return order === 'asc' ? -1 : 1;
    if (aVal > bVal) return order === 'asc' ? 1 : -1;
    return 0;
  });
}

/**
 * Group array of objects by key
 */
export function groupBy(array, key) {
  return array.reduce((result, item) => {
    const group = item[key];
    if (!result[group]) {
      result[group] = [];
    }
    result[group].push(item);
    return result;
  }, {});
}

// Export all functions as default object
export default {
  showToast,
  formatDate,
  formatBytes,
  formatPercent,
  formatUptime,
  getStatusColor,
  getStatusBadge,
  debounce,
  confirm,
  showLoading,
  hideLoading,
  copyToClipboard,
  escapeHtml,
  parseQuery,
  buildQuery,
  isValidEmail,
  isValidIP,
  isValidPort,
  generateId,
  sleep,
  loadComponent,
  formatCommand,
  getWebSocketURL,
  truncate,
  pluralize,
  sortBy,
  groupBy
};
