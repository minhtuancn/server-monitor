/* ============================================
   Server Monitor v4.0 - API Client Module
   Unified API client with authentication
   ============================================ */

import auth from './auth.js';

class APIClient {
  constructor() {
    // Auto-detect API base URL
    this.baseURL = this.detectAPIBaseURL();
  }

  /**
   * Auto-detect API base URL based on environment
   */
  detectAPIBaseURL() {
    // Check if API_BASE_URL is defined in window
    if (window.API_BASE_URL) {
      return window.API_BASE_URL;
    }

    const hostname = window.location.hostname;
    const port = window.location.port;

    // Development: port 9083
    // Production: port 8083
    const apiPort = port === '9081' ? 9083 : 8083;

    return `http://${hostname}:${apiPort}`;
  }

  /**
   * Make API request with automatic auth header
   */
  async request(method, endpoint, data = null, options = {}) {
    try {
      const url = `${this.baseURL}${endpoint}`;

      const headers = {
        'Content-Type': 'application/json',
        ...options.headers
      };

      // Add auth header if token exists
      if (auth.token) {
        headers['Authorization'] = `Bearer ${auth.token}`;
      }

      const config = {
        method,
        headers,
        ...options
      };

      // Add body for POST/PUT/PATCH requests
      if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
        config.body = JSON.stringify(data);
      }

      const response = await fetch(url, config);

      // Handle 401 Unauthorized - token expired or invalid
      if (response.status === 401) {
        auth.logout(true);
        throw new Error('Session expired. Please login again.');
      }

      // Handle other error responses
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || error.message || 'Request failed');
      }

      // Return empty object for 204 No Content
      if (response.status === 204) {
        return {};
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${method} ${endpoint}]:`, error);
      throw error;
    }
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    return this.request('GET', endpoint, null, options);
  }

  /**
   * POST request
   */
  async post(endpoint, data, options = {}) {
    return this.request('POST', endpoint, data, options);
  }

  /**
   * PUT request
   */
  async put(endpoint, data, options = {}) {
    return this.request('PUT', endpoint, data, options);
  }

  /**
   * PATCH request
   */
  async patch(endpoint, data, options = {}) {
    return this.request('PATCH', endpoint, data, options);
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    return this.request('DELETE', endpoint, null, options);
  }

  /**
   * Upload file
   */
  async upload(endpoint, formData, options = {}) {
    try {
      const url = `${this.baseURL}${endpoint}`;

      const headers = {
        ...options.headers
      };

      // Add auth header if token exists
      if (auth.token) {
        headers['Authorization'] = `Bearer ${auth.token}`;
      }

      // Don't set Content-Type for FormData - browser will set it automatically with boundary

      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
        ...options
      });

      if (response.status === 401) {
        auth.logout(true);
        throw new Error('Session expired. Please login again.');
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(error.detail || 'Upload failed');
      }

      return await response.json();
    } catch (error) {
      console.error(`Upload Error [${endpoint}]:`, error);
      throw error;
    }
  }

  /**
   * Download file
   */
  async download(endpoint, filename) {
    try {
      const url = `${this.baseURL}${endpoint}`;

      const headers = {};
      if (auth.token) {
        headers['Authorization'] = `Bearer ${auth.token}`;
      }

      const response = await fetch(url, { headers });

      if (response.status === 401) {
        auth.logout(true);
        throw new Error('Session expired. Please login again.');
      }

      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(downloadUrl);
      document.body.removeChild(a);
    } catch (error) {
      console.error(`Download Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // ========================================
  // Server APIs
  // ========================================

  async getServers() {
    return this.get('/api/v1/servers');
  }

  async getServer(id) {
    return this.get(`/api/v1/servers/${id}`);
  }

  async addServer(data) {
    return this.post('/api/v1/servers', data);
  }

  async updateServer(id, data) {
    return this.put(`/api/v1/servers/${id}`, data);
  }

  async deleteServer(id) {
    return this.delete(`/api/v1/servers/${id}`);
  }

  async installAgent(id) {
    return this.post(`/api/v1/servers/${id}/install-agent`);
  }

  async testConnection(id) {
    return this.post(`/api/v1/servers/${id}/test`);
  }

  // ========================================
  // SSH Key APIs
  // ========================================

  async getSSHKeys() {
    return this.get('/api/v1/ssh-keys');
  }

  async getSSHKey(id) {
    return this.get(`/api/v1/ssh-keys/${id}`);
  }

  async addSSHKey(data) {
    return this.post('/api/v1/ssh-keys', data);
  }

  async updateSSHKey(id, data) {
    return this.put(`/api/v1/ssh-keys/${id}`, data);
  }

  async deleteSSHKey(id) {
    return this.delete(`/api/v1/ssh-keys/${id}`);
  }

  async generateSSHKey(data) {
    return this.post('/api/v1/ssh-keys/generate', data);
  }

  async deploySSHKey(keyId, serverIds) {
    return this.post(`/api/v1/ssh-keys/${keyId}/deploy`, { server_ids: serverIds });
  }

  // ========================================
  // Email Settings APIs
  // ========================================

  async getEmailSettings() {
    return this.get('/api/v1/email-settings');
  }

  async updateEmailSettings(data) {
    return this.put('/api/v1/email-settings', data);
  }

  async testEmail(data) {
    return this.post('/api/v1/email-settings/test', data);
  }

  // ========================================
  // Server Groups APIs
  // ========================================

  async getGroups() {
    return this.get('/api/v1/groups');
  }

  async getGroup(id) {
    return this.get(`/api/v1/groups/${id}`);
  }

  async addGroup(data) {
    return this.post('/api/v1/groups', data);
  }

  async updateGroup(id, data) {
    return this.put(`/api/v1/groups/${id}`, data);
  }

  async deleteGroup(id) {
    return this.delete(`/api/v1/groups/${id}`);
  }

  // ========================================
  // Terminal Snippets APIs
  // ========================================

  async getSnippets() {
    return this.get('/api/v1/snippets');
  }

  async getSnippet(id) {
    return this.get(`/api/v1/snippets/${id}`);
  }

  async addSnippet(data) {
    return this.post('/api/v1/snippets', data);
  }

  async updateSnippet(id, data) {
    return this.put(`/api/v1/snippets/${id}`, data);
  }

  async deleteSnippet(id) {
    return this.delete(`/api/v1/snippets/${id}`);
  }

  async executeSnippet(id, serverId) {
    return this.post(`/api/v1/snippets/${id}/execute`, { server_id: serverId });
  }

  // ========================================
  // Network Tools APIs
  // ========================================

  async scanPorts(serverId, data) {
    return this.post(`/api/v1/servers/${serverId}/scan-ports`, data);
  }

  async checkPort(serverId, port) {
    return this.post(`/api/v1/servers/${serverId}/check-port`, { port });
  }

  async getFirewallStatus(serverId) {
    return this.get(`/api/v1/servers/${serverId}/firewall-status`);
  }

  async pingServer(serverId) {
    return this.post(`/api/v1/servers/${serverId}/ping`);
  }

  // ========================================
  // User Management APIs (Phase 1)
  // ========================================

  async getUsers() {
    return this.get('/api/users');
  }

  async getUser(id) {
    return this.get(`/api/users/${id}`);
  }

  async createUser(data) {
    return this.post('/api/users', data);
  }

  async updateUser(id, data) {
    return this.put(`/api/users/${id}`, data);
  }

  async deleteUser(id) {
    return this.delete(`/api/users/${id}`);
  }

  async changePassword(id, oldPassword, newPassword) {
    return this.post(`/api/users/${id}/change-password`, {
      old_password: oldPassword,
      new_password: newPassword
    });
  }

  async getRoles() {
    return this.get('/api/roles');
  }

  // ========================================
  // System Settings APIs (Phase 1)
  // ========================================

  async getSettings() {
    return this.get('/api/settings');
  }

  async getSetting(key) {
    return this.get(`/api/settings/${key}`);
  }

  async updateSetting(key, value) {
    return this.post(`/api/settings/${key}`, { value });
  }

  async updateSettings(settings) {
    return this.post('/api/settings', settings);
  }

  async getSettingsOptions() {
    return this.get('/api/settings/options');
  }
}

// Export singleton instance
const api = new APIClient();

export { APIClient, api };
export default api;
