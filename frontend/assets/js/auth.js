/* ============================================
   Server Monitor v4.0 - Authentication Module
   Unified session management across all pages
   ============================================ */

class AuthManager {
  constructor() {
    this.TOKEN_KEY = 'auth_token'; // Unified token storage key
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
    return !!this.token;
  }

  /**
   * Login with username and password
   */
  async login(username, password) {
    try {
      const API_BASE = window.API_BASE_URL || `http://${window.location.hostname}:9083`;
      
      const response = await fetch(`${API_BASE}/api/v1/admin/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      
      // Store token and user info
      this.setToken(data.token);
      this.setUser(data.user || { username });

      return { success: true, data };
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
        await fetch(`${API_BASE}/api/v1/admin/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        }).catch(() => {}); // Ignore errors
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
   * Call this at the top of protected pages
   */
  requireAuth() {
    if (!this.isAuthenticated()) {
      // Store current URL for redirect after login
      sessionStorage.setItem('redirect_after_login', window.location.pathname);
      window.location.href = '/login.html';
      return false;
    }
    return true;
  }

  /**
   * Redirect if already authenticated
   * Call this on login page
   */
  redirectIfAuthenticated() {
    if (this.isAuthenticated()) {
      // Check if there's a redirect URL
      const redirectUrl = sessionStorage.getItem('redirect_after_login');
      sessionStorage.removeItem('redirect_after_login');
      
      window.location.href = redirectUrl || '/dashboard.html';
      return true;
    }
    return false;
  }

  /**
   * Change password
   */
  async changePassword(currentPassword, newPassword) {
    try {
      const API_BASE = window.API_BASE_URL || `http://${window.location.hostname}:9083`;
      
      const response = await fetch(`${API_BASE}/api/v1/user/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to change password');
      }

      return { success: true };
    } catch (error) {
      console.error('Change password error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get user settings
   */
  async getUserSettings() {
    try {
      const API_BASE = window.API_BASE_URL || `http://${window.location.hostname}:9083`;
      
      const response = await fetch(`${API_BASE}/api/v1/user/settings`, {
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get user settings');
      }

      return await response.json();
    } catch (error) {
      console.error('Get settings error:', error);
      return null;
    }
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
