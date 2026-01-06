#!/usr/bin/env python3

"""
Central Multi-Server Monitoring API v3
Manages multiple remote servers via SSH
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
import ssh_manager as ssh
import email_alerts as email
import security

PORT = 9083  # Different port for central server

# ==================== HELPER FUNCTIONS ====================

def get_server_with_auth(server_id):
    """Get server details with decrypted password for SSH"""
    server = db.get_server(server_id, decrypt_password=True)
    if not server:
        return None
    return server

def verify_auth_token(handler):
    """Verify authentication token from Authorization header"""
    auth_header = handler.headers.get('Authorization', '')
    
    # Allow public endpoints without auth (read-only)
    public_endpoints = ['/api/stats/overview', '/api/servers']
    if handler.path in public_endpoints and handler.command == 'GET':
        return {'valid': True, 'role': 'public'}
    
    # Check for token
    if not auth_header.startswith('Bearer '):
        return {'valid': False, 'error': 'No authentication token provided'}
    
    token = auth_header.replace('Bearer ', '').strip()
    
    # Verify token with database
    result = db.verify_session(token)
    return result

class CentralAPIHandler(BaseHTTPRequestHandler):
    
    def _set_headers(self, status=200, extra_headers=None):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        
        # Always apply security headers (CORS + Security Headers)
        origin = self.headers.get('Origin', '')
        cors_headers = security.CORS.get_cors_headers(origin)
        sec_headers = security.SecurityHeaders.get_security_headers()
        
        for key, value in {**cors_headers, **sec_headers}.items():
            self.send_header(key, value)
        
        # Add any extra headers (will override if keys conflict)
        if extra_headers:
            for key, value in extra_headers.items():
                # Skip if already set by security headers to avoid duplicates
                if key not in cors_headers and key not in sec_headers:
                    self.send_header(key, value)
        
        self.end_headers()
    
    def do_OPTIONS(self):
        # Apply security middleware
        sec_result = security.apply_security_middleware(self, 'OPTIONS')
        if sec_result['block']:
            self._set_headers(sec_result['status'], sec_result.get('headers'))
            self.wfile.write(json.dumps(sec_result['body']).encode())
            return
        
        self._set_headers(200, sec_result.get('headers'))
    
    def _read_body(self):
        """Read and parse POST body"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            return json.loads(body)
        except:
            return {}
    
    def do_GET(self):
        # Apply security middleware
        sec_result = security.apply_security_middleware(self, 'GET')
        if sec_result['block']:
            self._set_headers(sec_result['status'], sec_result.get('headers'))
            self.wfile.write(json.dumps(sec_result['body']).encode())
            return
        
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # ==================== AUTHENTICATION ====================
        
        if path == '/api/auth/verify':
            # Verify current session
            auth_result = verify_auth_token(self)
            
            if auth_result['valid']:
                self._set_headers()
                self.wfile.write(json.dumps({
                    'valid': True,
                    'username': auth_result.get('username'),
                    'role': auth_result.get('role')
                }).encode())
            else:
                self._set_headers(401)
                self.wfile.write(json.dumps({'valid': False, 'error': auth_result.get('error')}).encode())
            return
        
        # ==================== SERVER MANAGEMENT ====================
        
        if path == '/api/servers':
            # Get all servers (public read allowed)
            self._set_headers()
            servers = db.get_servers()
            # Hide sensitive data for non-authenticated users
            auth_result = verify_auth_token(self)
            if not auth_result.get('valid') or auth_result.get('role') == 'public':
                for server in servers:
                    server.pop('ssh_key_path', None)
                    server.pop('ssh_password', None)
            self.wfile.write(json.dumps(servers).encode())
        
        elif path.startswith('/api/servers/'):
            # Get single server
            server_id = path.split('/')[-1]
            try:
                server_id = int(server_id)
                server = db.get_server(server_id)
                
                if server:
                    self._set_headers()
                    self.wfile.write(json.dumps(server).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Server not found'}).encode())
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        elif path == '/api/stats/overview':
            # Get stats overview of all servers
            self._set_headers()
            stats = db.get_server_stats()
            self.wfile.write(json.dumps(stats).encode())
        
        # ==================== EXPORT ENDPOINTS ====================
        
        elif path == '/api/export/servers/csv':
            # Export servers to CSV
            auth_result = verify_auth_token(self)
            if not auth_result['valid'] or auth_result.get('role') == 'public':
                self._set_headers(401)
                self.wfile.write(json.dumps({'error': 'Authentication required'}).encode())
                return
            
            try:
                csv_data = db.export_servers_csv()
                self.send_response(200)
                self.send_header('Content-type', 'text/csv')
                self.send_header('Content-Disposition', f'attachment; filename="servers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"')
                self.end_headers()
                self.wfile.write(csv_data.encode('utf-8'))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        elif path == '/api/export/servers/json':
            # Export servers to JSON
            auth_result = verify_auth_token(self)
            if not auth_result['valid'] or auth_result.get('role') == 'public':
                self._set_headers(401)
                self.wfile.write(json.dumps({'error': 'Authentication required'}).encode())
                return
            
            try:
                json_data = db.export_servers_json()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Disposition', f'attachment; filename="servers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"')
                self.end_headers()
                self.wfile.write(json_data.encode('utf-8'))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        elif path.startswith('/api/export/history/'):
            # Export monitoring history
            auth_result = verify_auth_token(self)
            if not auth_result['valid'] or auth_result.get('role') == 'public':
                self._set_headers(401)
                self.wfile.write(json.dumps({'error': 'Authentication required'}).encode())
                return
            
            # Parse format and parameters
            parts = path.split('/')
            export_format = parts[-1]  # csv or json
            
            # Get query parameters
            params = parse_qs(parsed.query)
            server_id = params.get('server_id', [None])[0]
            start_date = params.get('start_date', [None])[0]
            end_date = params.get('end_date', [None])[0]
            
            try:
                if export_format == 'csv':
                    csv_data = db.export_monitoring_history_csv(server_id, start_date, end_date)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/csv')
                    self.send_header('Content-Disposition', f'attachment; filename="history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"')
                    self.end_headers()
                    self.wfile.write(csv_data.encode('utf-8'))
                elif export_format == 'json':
                    json_data = db.export_monitoring_history_json(server_id, start_date, end_date)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Content-Disposition', f'attachment; filename="history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"')
                    self.end_headers()
                    self.wfile.write(json_data.encode('utf-8'))
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'error': 'Invalid format. Use csv or json'}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        elif path == '/api/export/alerts/csv':
            # Export alerts to CSV
            auth_result = verify_auth_token(self)
            if not auth_result['valid'] or auth_result.get('role') == 'public':
                self._set_headers(401)
                self.wfile.write(json.dumps({'error': 'Authentication required'}).encode())
                return
            
            # Get query parameters
            params = parse_qs(parsed.query)
            server_id = params.get('server_id', [None])[0]
            is_read = params.get('is_read', [None])[0]
            
            try:
                csv_data = db.export_alerts_csv(server_id, is_read)
                self.send_response(200)
                self.send_header('Content-type', 'text/csv')
                self.send_header('Content-Disposition', f'attachment; filename="alerts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"')
                self.end_headers()
                self.wfile.write(csv_data.encode('utf-8'))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        # ==================== REMOTE SERVER DATA ====================
        
        elif path.startswith('/api/remote/stats/'):
            # Get monitoring data from remote server
            server_id = path.split('/')[-1]
            
            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)
                
                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Server not found'}).encode())
                    return
                
                # Get data from remote agent
                result = ssh.get_remote_agent_data(
                    host=server['host'],
                    port=server['port'],
                    username=server['username'],
                    agent_port=server['agent_port'],
                    endpoint='/api/all',
                    ssh_key_path=server['ssh_key_path'],
                    password=server.get('ssh_password')
                )
                
                if result['success']:
                    # Update server status
                    db.update_server_status(server_id, 'online')
                    
                    # Add server info to response
                    data = result['data']
                    data['server_info'] = {
                        'id': server['id'],
                        'name': server['name'],
                        'host': server['host'],
                        'description': server['description']
                    }
                    
                    self._set_headers()
                    self.wfile.write(json.dumps(data).encode())
                else:
                    # Update server status to offline
                    db.update_server_status(server_id, 'offline')
                    
                    self._set_headers(503)
                    self.wfile.write(json.dumps({
                        'error': 'Failed to get data from remote server',
                        'details': result.get('error', '')
                    }).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        elif path == '/api/remote/stats/all':
            # Get stats from all servers
            self._set_headers()
            
            servers = db.get_servers()
            results = []
            
            for server in servers:
                # Get server with decrypted password
                server_full = get_server_with_auth(server['id'])
                
                if not server_full:
                    continue
                
                result = ssh.get_remote_agent_data(
                    host=server_full['host'],
                    port=server_full['port'],
                    username=server_full['username'],
                    agent_port=server_full['agent_port'],
                    endpoint='/api/all',
                    ssh_key_path=server_full['ssh_key_path'],
                    password=server_full.get('ssh_password')
                )
                
                if result['success']:
                    db.update_server_status(server['id'], 'online')
                    data = result['data']
                    data['server_info'] = {
                        'id': server['id'],
                        'name': server['name'],
                        'host': server['host'],
                        'description': server['description'],
                        'status': 'online'
                    }
                    results.append(data)
                else:
                    db.update_server_status(server['id'], 'offline')
                    results.append({
                        'server_info': {
                            'id': server['id'],
                            'name': server['name'],
                            'host': server['host'],
                            'description': server['description'],
                            'status': 'offline'
                        },
                        'error': result.get('error', 'Connection failed')
                    })
            
            self.wfile.write(json.dumps(results).encode())
        
        # ==================== SSH UTILITIES ====================
        
        elif path == '/api/ssh/pubkey':
            # Get SSH public key for display
            self._set_headers()
            result = ssh.get_ssh_public_key()
            self.wfile.write(json.dumps(result).encode())
        
        # ==================== ALERTS ====================
        
        elif path == '/api/alerts':
            self._set_headers()
            server_id = query.get('server_id', [None])[0]
            is_read = query.get('is_read', [None])[0]
            
            if is_read is not None:
                is_read = int(is_read)
            
            alerts = db.get_alerts(server_id=server_id, is_read=is_read)
            self.wfile.write(json.dumps(alerts).encode())
        
        # ==================== COMMAND SNIPPETS ====================
        
        elif path == '/api/snippets':
            # Get all snippets
            self._set_headers()
            category = query.get('category', [None])[0]
            snippets = db.get_snippets(category=category)
            self.wfile.write(json.dumps(snippets).encode())
        
        elif path.startswith('/api/snippets/'):
            # Get single snippet
            snippet_id = path.split('/')[-1]
            try:
                snippet_id = int(snippet_id)
                snippet = db.get_snippet(snippet_id)
                
                if snippet:
                    self._set_headers()
                    self.wfile.write(json.dumps(snippet).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Snippet not found'}).encode())
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid snippet ID'}).encode())
        
        # ==================== SSH KEY MANAGEMENT ====================
        
        elif path == '/api/ssh-keys':
            # Get all SSH keys
            auth_result = verify_auth_token(self)
            if not auth_result['valid'] or auth_result.get('role') == 'public':
                self._set_headers(401)
                self.wfile.write(json.dumps({'error': 'Authentication required'}).encode())
                return
            
            self._set_headers()
            keys = db.get_ssh_keys()
            # Don't expose sensitive paths in list view
            for key in keys:
                key.pop('passphrase', None)
            self.wfile.write(json.dumps(keys).encode())
        
        elif path.startswith('/api/ssh-keys/'):
            # Get single SSH key
            auth_result = verify_auth_token(self)
            if not auth_result['valid'] or auth_result.get('role') == 'public':
                self._set_headers(401)
                self.wfile.write(json.dumps({'error': 'Authentication required'}).encode())
                return
            
            key_id = path.split('/')[-1]
            try:
                key_id = int(key_id)
                key = db.get_ssh_key(key_id, decrypt_passphrase=False)
                
                if key:
                    # Don't expose passphrase
                    key.pop('passphrase', None)
                    self._set_headers()
                    self.wfile.write(json.dumps(key).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'SSH key not found'}).encode())
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid SSH key ID'}).encode())
        
        # ==================== EMAIL ALERTS ====================
        
        elif path == '/api/email/config':
            # Get email configuration
            auth_result = verify_auth_token(self)
            if not auth_result['valid'] or auth_result.get('role') == 'public':
                self._set_headers(401)
                self.wfile.write(json.dumps({'error': 'Authentication required'}).encode())
                return
            
            config = email.get_email_config()
            if config:
                # Hide password
                config['smtp_password'] = '********' if config.get('smtp_password') else ''
                self._set_headers()
                self.wfile.write(json.dumps(config).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'No email configuration found'}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())
    
    def do_POST(self):
        # Apply security middleware
        sec_result = security.apply_security_middleware(self, 'POST')
        if sec_result['block']:
            self._set_headers(sec_result['status'], sec_result.get('headers'))
            self.wfile.write(json.dumps(sec_result['body']).encode())
            return
        
        path = self.path
        data = self._read_body()
        
        # Sanitize input data
        if data:
            for key, value in data.items():
                if isinstance(value, str):
                    if key in ['name', 'description', 'username']:
                        data[key] = security.InputSanitizer.sanitize_string(value)
                    elif key == 'host':
                        # Validate hostname or IP
                        if not (security.InputSanitizer.validate_hostname(value) or 
                                security.InputSanitizer.validate_ip(value)):
                            self._set_headers(400)
                            self.wfile.write(json.dumps({
                                'error': 'Invalid hostname or IP address'
                            }).encode())
                            return
                    elif key == 'port':
                        if not security.InputSanitizer.validate_port(value):
                            self._set_headers(400)
                            self.wfile.write(json.dumps({
                                'error': 'Invalid port number'
                            }).encode())
                            return
        
        # ==================== AUTHENTICATION ====================
        
        if path == '/api/auth/login':
            # Admin login
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Username and password required'}).encode())
                return
            
            result = db.authenticate_user(username, password)
            
            if result['success']:
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            else:
                self._set_headers(401)
                self.wfile.write(json.dumps(result).encode())
            return
        
        elif path == '/api/auth/logout':
            # Admin logout
            auth_result = verify_auth_token(self)
            
            if not auth_result['valid']:
                self._set_headers(401)
                self.wfile.write(json.dumps({'error': 'Not authenticated'}).encode())
                return
            
            # Extract token from header
            auth_header = self.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '').strip()
            
            result = db.logout_user(token)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
            return
        
        # ==================== CHECK AUTHENTICATION FOR PROTECTED ROUTES ====================
        
        # All routes below require authentication
        auth_result = verify_auth_token(self)
        if not auth_result['valid'] or auth_result.get('role') == 'public':
            self._set_headers(401)
            self.wfile.write(json.dumps({'error': 'Authentication required'}).encode())
            return
        
        # ==================== SERVER MANAGEMENT ====================
        
        if path == '/api/servers':
            # Add new server
            required = ['name', 'host', 'username']
            
            if not all(k in data for k in required):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode())
                return
            
            result = db.add_server(
                name=data['name'],
                host=data['host'],
                port=data.get('port', 22),
                username=data['username'],
                description=data.get('description', ''),
                ssh_key_path=data.get('ssh_key_path', '~/.ssh/id_rsa'),
                ssh_password=data.get('ssh_password', ''),
                agent_port=data.get('agent_port', 8083),
                tags=data.get('tags', '')
            )
            
            if result['success']:
                self._set_headers(201)
            else:
                self._set_headers(400)
            
            self.wfile.write(json.dumps(result).encode())
        
        elif path == '/api/servers/test':
            # Test SSH connection to a server
            required = ['host', 'username']
            
            if not all(k in data for k in required):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode())
                return
            
            result = ssh.test_connection(
                host=data['host'],
                port=data.get('port', 22),
                username=data['username'],
                ssh_key_path=data.get('ssh_key_path', '~/.ssh/id_rsa'),
                password=data.get('password', '')
            )
            
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        # ==================== REMOTE AGENT MANAGEMENT ====================
        
        elif path.startswith('/api/remote/agent/deploy/'):
            # Deploy agent to remote server
            server_id = path.split('/')[-1]
            
            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)
                
                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Server not found'}).encode())
                    return
                
                # Deploy agent
                local_agent_path = os.path.join(os.path.dirname(__file__), 'agent.py')
                remote_agent_path = data.get('remote_path', '/tmp/monitoring_agent.py')
                
                result = ssh.deploy_agent(
                    host=server['host'],
                    port=server['port'],
                    username=server['username'],
                    local_agent_path=local_agent_path,
                    remote_agent_path=remote_agent_path,
                    ssh_key_path=server['ssh_key_path'],
                    password=server.get('ssh_password')
                )
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        elif path.startswith('/api/remote/agent/start/'):
            # Start agent on remote server
            server_id = path.split('/')[-1]
            
            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)
                
                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Server not found'}).encode())
                    return
                
                agent_path = data.get('agent_path', '/tmp/monitoring_agent.py')
                
                result = ssh.start_remote_agent(
                    host=server['host'],
                    port=server['port'],
                    username=server['username'],
                    agent_script_path=agent_path,
                    ssh_key_path=server['ssh_key_path'],
                    password=server.get('ssh_password')
                )
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        elif path.startswith('/api/remote/agent/install/'):
            # Install agent on remote server (NEW)
            server_id = path.split('/')[-1]
            
            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)
                
                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Server not found'}).encode())
                    return
                
                agent_port = data.get('agent_port', 8083)
                
                result = ssh.install_agent_remote(
                    host=server['host'],
                    port=server['port'],
                    username=server['username'],
                    agent_port=agent_port,
                    ssh_key_path=server['ssh_key_path'],
                    password=server.get('ssh_password')
                )
                
                # Update server agent_installed status
                if result.get('success'):
                    db.update_server(server_id, agent_installed=1)
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        elif path.startswith('/api/remote/agent/uninstall/'):
            # Uninstall agent from remote server (NEW)
            server_id = path.split('/')[-1]
            
            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)
                
                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Server not found'}).encode())
                    return
                
                result = ssh.uninstall_agent_remote(
                    host=server['host'],
                    port=server['port'],
                    username=server['username'],
                    ssh_key_path=server['ssh_key_path'],
                    password=server.get('ssh_password')
                )
                
                # Update server agent_installed status
                if result.get('success'):
                    db.update_server(server_id, agent_installed=0)
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        elif path.startswith('/api/remote/agent/info/'):
            # Get agent info and status (NEW)
            server_id = path.split('/')[-1]
            
            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)
                
                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Server not found'}).encode())
                    return
                
                result = ssh.get_agent_info(
                    host=server['host'],
                    port=server['port'],
                    username=server['username'],
                    ssh_key_path=server['ssh_key_path'],
                    password=server.get('ssh_password')
                )
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        elif path.startswith('/api/remote/check-port/'):
            # Check if port is available on remote server (NEW)
            server_id = path.split('/')[-1]
            
            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)
                
                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Server not found'}).encode())
                    return
                
                check_port = data.get('port', 8083)
                
                result = ssh.check_port_available(
                    host=server['host'],
                    port=server['port'],
                    username=server['username'],
                    check_port=check_port,
                    ssh_key_path=server['ssh_key_path'],
                    password=server.get('ssh_password')
                )
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        elif path.startswith('/api/remote/suggest-port/'):
            # Suggest available port on remote server (NEW)
            server_id = path.split('/')[-1]
            
            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)
                
                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Server not found'}).encode())
                    return
                
                start_port = data.get('start_port', 8083)
                
                result = ssh.suggest_available_port(
                    host=server['host'],
                    port=server['port'],
                    username=server['username'],
                    start_port=start_port,
                    ssh_key_path=server['ssh_key_path'],
                    password=server.get('ssh_password')
                )
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        # ==================== REMOTE ACTIONS ====================
        
        elif path.startswith('/api/remote/action/'):
            # Execute action on remote server
            server_id = path.split('/')[-1]
            
            try:
                server_id = int(server_id)
                server = get_server_with_auth(server_id)
                
                if not server:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Server not found'}).encode())
                    return
                
                action_type = data.get('action_type')
                action_data = data.get('action_data', {})
                
                result = ssh.execute_remote_action(
                    host=server['host'],
                    port=server['port'],
                    username=server['username'],
                    action_type=action_type,
                    action_data=action_data,
                    ssh_key_path=server['ssh_key_path'],
                    password=server.get('ssh_password')
                )
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        # ==================== COMMAND SNIPPETS ====================
        
        elif path == '/api/snippets':
            # Create new snippet
            required = ['name', 'command']
            
            if not all(k in data for k in required):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing required fields: name, command'}).encode())
                return
            
            result = db.add_snippet(
                name=data['name'],
                command=data['command'],
                description=data.get('description', ''),
                category=data.get('category', 'general'),
                is_sudo=data.get('is_sudo', 0),
                created_by=auth_result.get('user_id')
            )
            
            if result['success']:
                self._set_headers(201)
            else:
                self._set_headers(400)
            
            self.wfile.write(json.dumps(result).encode())
        
        # ==================== SSH KEY MANAGEMENT ====================
        
        elif path == '/api/ssh-keys':
            # Create new SSH key
            required = ['name', 'private_key_path']
            
            if not all(k in data for k in required):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing required fields: name, private_key_path'}).encode())
                return
            
            result = db.add_ssh_key(
                name=data['name'],
                private_key_path=data['private_key_path'],
                description=data.get('description', ''),
                key_type=data.get('key_type', 'rsa'),
                public_key=data.get('public_key', ''),
                passphrase=data.get('passphrase', ''),
                created_by=auth_result.get('user_id')
            )
            
            if result['success']:
                self._set_headers(201)
            else:
                self._set_headers(400)
            
            self.wfile.write(json.dumps(result).encode())
        
        elif path.startswith('/api/ssh-keys/') and path.endswith('/test'):
            # Test SSH key connection
            key_id = path.split('/')[-2]
            
            try:
                key_id = int(key_id)
                key = db.get_ssh_key(key_id, decrypt_passphrase=True)
                
                if not key:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'SSH key not found'}).encode())
                    return
                
                # Get test host from request data
                test_host = data.get('host')
                test_port = data.get('port', 22)
                test_user = data.get('username', 'root')
                
                if not test_host:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'error': 'Missing host parameter'}).encode())
                    return
                
                # Test connection
                result = ssh.test_ssh_connection(
                    host=test_host,
                    port=test_port,
                    username=test_user,
                    ssh_key_path=key['private_key_path'],
                    password=key.get('passphrase', '')
                )
                
                if result['success']:
                    # Update last used timestamp
                    db.update_ssh_key_last_used(key_id)
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid SSH key ID'}).encode())
        
        # ==================== EMAIL ALERTS ====================
        
        elif path == '/api/email/config':
            # Save email configuration
            result = email.save_email_config(
                smtp_host=data.get('smtp_host'),
                smtp_port=int(data.get('smtp_port', 587)),
                smtp_user=data.get('smtp_user'),
                smtp_password=data.get('smtp_password'),
                from_email=data.get('from_email'),
                to_emails=data.get('to_emails'),
                use_tls=data.get('use_tls', True),
                enabled=data.get('enabled', True)
            )
            
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif path == '/api/email/test':
            # Test email configuration
            result = email.test_email_config()
            
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif path == '/api/email/send-alert':
            # Manually send an alert email
            result = email.send_alert_email(
                server_name=data.get('server_name', 'Unknown Server'),
                alert_type=data.get('alert_type', 'Manual Alert'),
                message=data.get('message', 'Test alert'),
                severity=data.get('severity', 'warning'),
                server_id=data.get('server_id')
            )
            
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())
    
    def do_PUT(self):
        path = self.path
        data = self._read_body()
        
        # Check authentication
        auth_result = verify_auth_token(self)
        if not auth_result['valid'] or auth_result.get('role') == 'public':
            self._set_headers(401)
            self.wfile.write(json.dumps({'error': 'Authentication required'}).encode())
            return
        
        if path.startswith('/api/servers/'):
            # Update server
            server_id = path.split('/')[-1]
            
            try:
                server_id = int(server_id)
                result = db.update_server(server_id, **data)
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        elif path.startswith('/api/snippets/'):
            # Update snippet
            snippet_id = path.split('/')[-1]
            
            try:
                snippet_id = int(snippet_id)
                result = db.update_snippet(snippet_id, **data)
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid snippet ID'}).encode())
        
        elif path.startswith('/api/ssh-keys/'):
            # Update SSH key
            key_id = path.split('/')[-1]
            
            try:
                key_id = int(key_id)
                result = db.update_ssh_key(key_id, **data)
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid SSH key ID'}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())
    
    def do_DELETE(self):
        path = self.path
        
        # Check authentication
        auth_result = verify_auth_token(self)
        if not auth_result['valid'] or auth_result.get('role') == 'public':
            self._set_headers(401)
            self.wfile.write(json.dumps({'error': 'Authentication required'}).encode())
            return
        
        if path.startswith('/api/servers/'):
            # Delete server
            server_id = path.split('/')[-1]
            
            try:
                server_id = int(server_id)
                result = db.delete_server(server_id)
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid server ID'}).encode())
        
        elif path.startswith('/api/snippets/'):
            # Delete snippet
            snippet_id = path.split('/')[-1]
            
            try:
                snippet_id = int(snippet_id)
                result = db.delete_snippet(snippet_id)
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid snippet ID'}).encode())
        
        elif path.startswith('/api/ssh-keys/'):
            # Delete SSH key
            key_id = path.split('/')[-1]
            
            try:
                key_id = int(key_id)
                result = db.delete_ssh_key(key_id)
                
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid SSH key ID'}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    # Initialize database
    db.init_database()
    
    # Cleanup expired sessions (older than 7 days)
    cleanup_result = db.cleanup_expired_sessions()
    
    server = HTTPServer(('0.0.0.0', PORT), CentralAPIHandler)
    print(f'╔══════════════════════════════════════════════════════════╗')
    print(f'║  Central Multi-Server Monitoring API v4                  ║')
    print(f'╚══════════════════════════════════════════════════════════╝')
    print(f'\n🚀 Server running on http://0.0.0.0:{PORT}')
    print(f'🔒 Authentication: Enabled (sessions expire after 7 days)')
    print(f'🧹 Cleaned up {cleanup_result["deleted"]} expired sessions')
    print(f'\n📡 API Endpoints:')
    print(f'   Auth:')
    print(f'   • POST /api/auth/login             - Admin login')
    print(f'   • POST /api/auth/logout            - Admin logout')
    print(f'   • GET  /api/auth/verify            - Verify session token')
    print(f'   Servers:')
    print(f'   • GET  /api/servers                - List all servers (public)')
    print(f'   • POST /api/servers                - Add new server (auth)')
    print(f'   • GET  /api/servers/<id>           - Get server details')
    print(f'   • PUT  /api/servers/<id>           - Update server (auth)')
    print(f'   • DELETE /api/servers/<id>         - Delete server (auth)')
    print(f'   • POST /api/servers/test           - Test SSH connection (auth)')
    print(f'   Monitoring:')
    print(f'   • GET  /api/remote/stats/<id>      - Get server monitoring data')
    print(f'   • GET  /api/remote/stats/all       - Get all servers data')
    print(f'   Agent:')
    print(f'   • POST /api/remote/agent/deploy/<id>    - Deploy agent to server (auth)')
    print(f'   • POST /api/remote/agent/start/<id>     - Start agent on server (auth)')
    print(f'   • POST /api/remote/agent/install/<id>   - Install agent with systemd (auth)')
    print(f'   • POST /api/remote/agent/uninstall/<id> - Uninstall agent (auth)')
    print(f'   • POST /api/remote/agent/info/<id>      - Get agent status (auth)')
    print(f'   • POST /api/remote/check-port/<id>      - Check port availability (auth)')
    print(f'   • POST /api/remote/suggest-port/<id>    - Suggest available port (auth)')
    print(f'   • POST /api/remote/action/<id>          - Execute remote action (auth)')
    print(f'   Snippets:')
    print(f'   • GET  /api/snippets               - List all command snippets')
    print(f'   • POST /api/snippets               - Create snippet (auth)')
    print(f'   • GET  /api/snippets/<id>          - Get snippet details')
    print(f'   • PUT  /api/snippets/<id>          - Update snippet (auth)')
    print(f'   • DELETE /api/snippets/<id>        - Delete snippet (auth)')
    print(f'   SSH Keys:')
    print(f'   • GET  /api/ssh-keys               - List all SSH keys (auth)')
    print(f'   • POST /api/ssh-keys               - Add new SSH key (auth)')
    print(f'   • GET  /api/ssh-keys/<id>          - Get SSH key details (auth)')
    print(f'   • PUT  /api/ssh-keys/<id>          - Update SSH key (auth)')
    print(f'   • DELETE /api/ssh-keys/<id>        - Delete SSH key (auth)')
    print(f'   • POST /api/ssh-keys/<id>/test     - Test SSH key connection (auth)')
    print(f'   Other:')
    print(f'   • GET  /api/ssh/pubkey             - Get SSH public key')
    print(f'   • GET  /api/stats/overview         - Get overview statistics')
    print(f'   • GET  /api/alerts                 - Get alerts')
    print(f'\n✨ Press Ctrl+C to stop')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n\n👋 Shutting down server...')
        ssh.ssh_pool.close_all()
        server.shutdown()
