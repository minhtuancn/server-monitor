/* ============================================
   Server Monitor v2.0 Enterprise - Authentication Module
   JWT-based session management with role-based access control
   ============================================ */

class AuthManager {
  constructor() {
    this.TOKEN_KEY = 'auth_token';
    this.USER_KEY = 'auth_user';
    this.token = this.getToken();
    this.user = this.getUser();
  }

  /**
   * Get token from localStorage
   */
  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Set token to localStorage
   */
  setToken(token) {
    localStorage.setItem(this.TOKEN_KEY, token);
    this.token = token;
  }

  /**
   * Get user info from localStorage
   */
  getUser() {
    const userStr = localStorage.getItem(this.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Get current user
   */
  getCurrentUser() {
    return this.user;
  }

  /**
   * Set user info to localStorage
   */
  setUser(user) {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    this.user = user;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    if (!this.token || !this.user) return false;
    return !this.isTokenExpired();
  }

  /**
   * Check if user has specific role
   */
  hasRole(role) {
    return this.user && this.user.role === role;
  }

  /**
   * Check if user has any of the specified roles
   */
  hasAnyRole(roles) {
    return this.user && roles.includes(this.user.role);
  }

  /**
   * Check if user has permission
   */
  hasPermission(permission) {
    if (!this.user || !this.user.permissions) return false;

    const permissions = this.user.permissions;

    // Admin has all permissions
    if (permissions.includes('*')) return true;

    // Check exact permission or wildcard
    return permissions.includes(permission) ||
      permissions.some(p => p.endsWith('.*') && permission.startsWith(p.slice(0, -2)));
  }

  /**
   * Decode JWT token payload
   */
  decodeToken(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      return JSON.parse(jsonPayload);
    } catch (e) {
      return null;
    }
  }

  /**
   * Check if token is expired
   */
  isTokenExpired() {
    if (!this.token) return true;

    const payload = this.decodeToken(this.token);
    if (!payload || !payload.exp) return true;

    return Date.now() >= payload.exp * 1000;
  }

  /**
   * Login with username and password (JWT-based)
   */
  async login(username, password) {
    try {
      const API_BASE = window.API_BASE_URL || `http://${window.location.hostname}:9083`;

      const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Login failed');
      }

      const data = await response.json();

      if (data.success && data.token) {
        // Decode token to get user info
        const payload = this.decodeToken(data.token);

        const user = {
          id: payload.user_id,
          username: payload.username,
          role: payload.role,
          permissions: payload.permissions || []
        };

        // Store token and user info
        this.setToken(data.token);
        this.setUser(user);

        return { success: true, data: { token: data.token, user } };
      }

      throw new Error('Invalid response from server');
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Logout and clear session
   */
  async logout(redirect = true) {
    try {
      const API_BASE = window.API_BASE_URL || `http://${window.location.hostname}:9083`;

      // Call logout API if token exists
      if (this.token) {
        await fetch(`${API_BASE}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        }).catch(() => { }); // Ignore errors
      }
    } finally {
      // Clear local storage
      localStorage.removeItem(this.TOKEN_KEY);
      localStorage.removeItem(this.USER_KEY);
      this.token = null;
      this.user = null;

      // Redirect to login page
      if (redirect) {
        window.location.href = '/login.html';
      }
    }
  }

  /**
   * Require authentication - redirect to login if not authenticated
   */
  requireAuth() {
    // Check if token expired
    if (this.isTokenExpired()) {
      this.logout(true);
      return false;
    }

    if (!this.isAuthenticated()) {
      sessionStorage.setItem('redirect_after_login', window.location.pathname);
      window.location.href = '/login.html';
      return false;
    }
    return true;
  }

  /**
   * Require specific role
   */
  requireRole(role) {
    if (!this.requireAuth()) return false;

    if (!this.hasRole(role)) {
      alert(`Access denied. This page requires ${role} role.`);
      window.location.href = '/dashboard.html';
      return false;
    }
    return true;
  }

  /**
   * Require any of specified roles
   */
  requireAnyRole(roles) {
    if (!this.requireAuth()) return false;

    if (!this.hasAnyRole(roles)) {
      alert(`Access denied. This page requires one of: ${roles.join(', ')}`);
      window.location.href = '/dashboard.html';
      return false;
    }
    return true;
  }

  /**
   * Redirect if already authenticated
   */
  redirectIfAuthenticated() {
    if (this.isAuthenticated() && !this.isTokenExpired()) {
      const redirectUrl = sessionStorage.getItem('redirect_after_login');
      sessionStorage.removeItem('redirect_after_login');

      window.location.href = redirectUrl || '/dashboard.html';
      return true;
    }
    return false;
  }

  /**
   * Update user settings
   */
  async updateUserSettings(settings) {
    try {
      const API_BASE = window.API_BASE_URL || `http://${window.location.hostname}:9083`;

      const response = await fetch(`${API_BASE}/api/v1/user/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        },
        body: JSON.stringify(settings)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update settings');
      }

      const data = await response.json();

      // Update local user info
      this.setUser({ ...this.user, ...settings });

      // Apply theme if changed
      if (settings.theme) {
        document.documentElement.setAttribute('data-theme', settings.theme);
      }

      return { success: true, data };
    } catch (error) {
      console.error('Update settings error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Validate token by making a test API call
   */
  async validateToken() {
    if (!this.token) {
      return false;
    }

    try {
      const API_BASE = window.API_BASE_URL || `http://${window.location.hostname}:9083`;

      const response = await fetch(`${API_BASE}/api/v1/user/validate`, {
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      });

      if (!response.ok) {
        // Token is invalid, clear it
        this.logout(false);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  }

  /**
   * Get authorization header
   */
  getAuthHeader() {
    return {
      'Authorization': `Bearer ${this.token}`
    };
  }
}

// Export singleton instance
const auth = new AuthManager();

// Also export class for custom instances if needed
export { AuthManager, auth };
export default auth;
