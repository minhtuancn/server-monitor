#!/usr/bin/env python3

"""
Advanced Server Dashboard API v2
Full-featured monitoring and management system
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import os
import re
import time
from urllib.parse import urlparse, parse_qs
from collections import deque
from datetime import datetime

PORT = 9083

# Historical data storage (in-memory, last 30 minutes)
history_data = {
    'cpu': deque(maxlen=360),  # 30 min at 5s intervals
    'memory': deque(maxlen=360),
    'network': deque(maxlen=360),
    'disk_io': deque(maxlen=360)
}

# Network stats tracking
last_network_stats = {'rx_bytes': 0, 'tx_bytes': 0, 'timestamp': time.time()}
last_disk_io = {'read_bytes': 0, 'write_bytes': 0, 'timestamp': time.time()}

# Port descriptions database
PORT_DESCRIPTIONS = {
    '21': {'name': 'FTP', 'desc': 'File Transfer Protocol'},
    '22': {'name': 'SSH', 'desc': 'Secure Shell - Kết nối SSH terminal'},
    '25': {'name': 'SMTP', 'desc': 'Simple Mail Transfer Protocol - Gửi email'},
    '53': {'name': 'DNS', 'desc': 'Domain Name System - Phân giải tên miền'},
    '80': {'name': 'HTTP', 'desc': 'Web Server - HTTP không mã hóa'},
    '110': {'name': 'POP3', 'desc': 'Post Office Protocol - Nhận email'},
    '143': {'name': 'IMAP', 'desc': 'Internet Message Access Protocol'},
    '443': {'name': 'HTTPS', 'desc': 'Web Server - HTTPS mã hóa SSL/TLS'},
    '465': {'name': 'SMTPS', 'desc': 'SMTP qua SSL - Gửi email bảo mật'},
    '587': {'name': 'SMTP Submit', 'desc': 'SMTP Submission - Gửi email'},
    '993': {'name': 'IMAPS', 'desc': 'IMAP qua SSL'},
    '995': {'name': 'POP3S', 'desc': 'POP3 qua SSL'},
    '1433': {'name': 'MSSQL', 'desc': 'Microsoft SQL Server Database'},
    '3000': {'name': 'Dev Server', 'desc': 'Development web server - Node.js'},
    '3306': {'name': 'MySQL', 'desc': 'MySQL Database Server'},
    '5000': {'name': 'Flask/Dev', 'desc': 'Flask development server'},
    '5432': {'name': 'PostgreSQL', 'desc': 'PostgreSQL Database Server'},
    '5672': {'name': 'RabbitMQ', 'desc': 'RabbitMQ Message Queue'},
    '6379': {'name': 'Redis', 'desc': 'Redis Cache & Data Store'},
    '8000': {'name': 'Web Dev', 'desc': 'Development web server'},
    '8080': {'name': 'OpenCode Web', 'desc': 'OpenCode Web Interface'},
    '8081': {'name': 'Dashboard', 'desc': 'Server Dashboard UI'},
    '8082': {'name': 'Control API', 'desc': 'OpenCode Control API'},
    '8083': {'name': 'Server API', 'desc': 'Server Dashboard API Backend'},
    '9000': {'name': 'Web Panel', 'desc': 'Control panel hoặc admin UI'},
    '9200': {'name': 'Elasticsearch', 'desc': 'Elasticsearch Search Engine'},
    '11211': {'name': 'Memcached', 'desc': 'Memcached Caching System'},
    '27017': {'name': 'MongoDB', 'desc': 'MongoDB NoSQL Database'},
}

def run_command(cmd):
    """Execute shell command and return output"""
    try:
        # Security Note: shell=True is used in this DEPRECATED legacy file
        # This file is not actively used (see legacy/README.md)
        # Commands here are predefined strings, not user input
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)  # nosec B602
        return result.stdout.strip()
    except:
        return ""

def get_system_info():
    """Get system information"""
    # Memory
    mem = run_command("free -m | grep Mem")
    mem_parts = mem.split()
    total_mem = int(mem_parts[1]) if len(mem_parts) > 1 else 0
    used_mem = int(mem_parts[2]) if len(mem_parts) > 2 else 0
    free_mem = int(mem_parts[3]) if len(mem_parts) > 3 else 0
    mem_percent = round((used_mem / total_mem * 100), 1) if total_mem > 0 else 0
    
    # Disk
    disk = run_command("df -h / | tail -1")
    disk_parts = disk.split()
    disk_total = disk_parts[1] if len(disk_parts) > 1 else "0G"
    disk_used = disk_parts[2] if len(disk_parts) > 2 else "0G"
    disk_free = disk_parts[3] if len(disk_parts) > 3 else "0G"
    disk_percent = float(disk_parts[4].replace('%', '')) if len(disk_parts) > 4 else 0
    
    # CPU
    cpu_count = run_command("nproc")
    load_avg = run_command("uptime | awk -F'load average:' '{print $2}'").strip()
    cpu_usage = run_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'").replace(',', '')
    
    # Uptime
    uptime_sec = run_command("cat /proc/uptime | awk '{print int($1)}'")
    uptime_sec = int(uptime_sec) if uptime_sec else 0
    uptime_str = f"{uptime_sec//86400}d {uptime_sec%86400//3600}h {uptime_sec%3600//60}m"
    
    # Hostname
    hostname = run_command("hostname")
    
    # Store in history
    cpu_val = float(cpu_usage) if cpu_usage else 0
    history_data['cpu'].append({'time': time.time(), 'value': cpu_val})
    history_data['memory'].append({'time': time.time(), 'value': mem_percent})
    
    return {
        'memory': {
            'total': total_mem,
            'used': used_mem,
            'free': free_mem,
            'percent': mem_percent
        },
        'disk': {
            'total': disk_total,
            'used': disk_used,
            'free': disk_free,
            'percent': disk_percent
        },
        'cpu': {
            'count': int(cpu_count) if cpu_count else 1,
            'load_avg': load_avg,
            'usage': cpu_val
        },
        'uptime': uptime_str,
        'hostname': hostname
    }

def get_network_stats():
    """Get network statistics"""
    global last_network_stats
    
    # Read /proc/net/dev for network stats
    output = run_command("cat /proc/net/dev")
    total_rx = 0
    total_tx = 0
    
    for line in output.split('\n'):
        if ':' in line and 'lo' not in line:  # Skip loopback
            parts = line.split()
            if len(parts) >= 10:
                total_rx += int(parts[1])
                total_tx += int(parts[9])
    
    current_time = time.time()
    time_diff = current_time - last_network_stats['timestamp']
    
    if time_diff > 0:
        rx_speed = (total_rx - last_network_stats['rx_bytes']) / time_diff / 1024 / 1024  # MB/s
        tx_speed = (total_tx - last_network_stats['tx_bytes']) / time_diff / 1024 / 1024
    else:
        rx_speed = 0
        tx_speed = 0
    
    # Store in history
    history_data['network'].append({
        'time': current_time,
        'rx': rx_speed,
        'tx': tx_speed
    })
    
    last_network_stats = {
        'rx_bytes': total_rx,
        'tx_bytes': total_tx,
        'timestamp': current_time
    }
    
    # Active connections
    connections = run_command("ss -tun | wc -l")
    conn_count = int(connections) - 1 if connections else 0
    
    return {
        'rx_speed': round(rx_speed, 2),
        'tx_speed': round(tx_speed, 2),
        'total_rx_mb': round(total_rx / 1024 / 1024, 2),
        'total_tx_mb': round(total_tx / 1024 / 1024, 2),
        'connections': conn_count
    }

def get_disk_io():
    """Get disk I/O statistics"""
    global last_disk_io
    
    # Read /proc/diskstats
    output = run_command("cat /proc/diskstats | grep -E 'sda|vda|nvme0n1' | head -1")
    if not output:
        return {'read_speed': 0, 'write_speed': 0, 'iops': 0}
    
    parts = output.split()
    if len(parts) < 14:
        return {'read_speed': 0, 'write_speed': 0, 'iops': 0}
    
    # Sectors read and written (512 bytes per sector)
    read_sectors = int(parts[5])
    write_sectors = int(parts[9])
    read_bytes = read_sectors * 512
    write_bytes = write_sectors * 512
    
    current_time = time.time()
    time_diff = current_time - last_disk_io['timestamp']
    
    if time_diff > 0:
        read_speed = (read_bytes - last_disk_io['read_bytes']) / time_diff / 1024 / 1024
        write_speed = (write_bytes - last_disk_io['write_bytes']) / time_diff / 1024 / 1024
    else:
        read_speed = 0
        write_speed = 0
    
    last_disk_io = {
        'read_bytes': read_bytes,
        'write_bytes': write_bytes,
        'timestamp': current_time
    }
    
    history_data['disk_io'].append({
        'time': current_time,
        'read': read_speed,
        'write': write_speed
    })
    
    return {
        'read_speed': round(read_speed, 2),
        'write_speed': round(write_speed, 2),
        'iops': int(parts[3]) if len(parts) > 3 else 0
    }

def get_processes():
    """Get running processes"""
    cmd = "ps aux --sort=-%mem | head -51"
    output = run_command(cmd)
    
    processes = []
    for line in output.split('\n')[1:]:  # Skip header
        parts = line.split(None, 10)
        if len(parts) >= 11:
            processes.append({
                'user': parts[0],
                'pid': parts[1],
                'cpu': float(parts[2]),
                'mem': float(parts[3]),
                'vsz': parts[4],
                'rss': parts[5],
                'tty': parts[6],
                'stat': parts[7],
                'start': parts[8],
                'time': parts[9],
                'command': parts[10][:100]
            })
    
    return processes

def get_ports():
    """Get listening ports"""
    cmd = "ss -tlnp | grep LISTEN"
    output = run_command(cmd)
    
    ports = []
    seen_ports = set()
    
    for line in output.split('\n'):
        match = re.search(r'[*0-9.]+:(\d+)', line)
        if match:
            port = match.group(1)
            
            if port in seen_ports:
                continue
            seen_ports.add(port)
            
            proc_match = re.search(r'users:\(\("([^"]+)",pid=(\d+)', line)
            process_name = proc_match.group(1) if proc_match else 'unknown'
            process_pid = proc_match.group(2) if proc_match else '?'
            
            port_info = PORT_DESCRIPTIONS.get(port, {
                'name': f'Port {port}',
                'desc': 'Dịch vụ không xác định'
            })
            
            ports.append({
                'port': port,
                'name': port_info['name'],
                'description': port_info['desc'],
                'process': process_name,
                'pid': process_pid
            })
    
    ports.sort(key=lambda x: int(x['port']))
    return ports

def get_services():
    """Get systemd services status"""
    services = [
        'opencode.service',
        'opencode-dashboard.service', 
        'server-dashboard-api.service',
        'opencode-control-api.service',
        'opencode-watchdog.timer',
        'mysql.service',
        'nginx.service',
        'redis.service',
        'docker.service'
    ]
    
    result = []
    for svc in services:
        status = run_command(f"systemctl is-active {svc} 2>/dev/null")
        enabled = run_command(f"systemctl is-enabled {svc} 2>/dev/null")
        
        if status or enabled:
            result.append({
                'name': svc,
                'status': status if status else 'inactive',
                'enabled': enabled == 'enabled',
                'display_name': svc.replace('.service', '').replace('-', ' ').title()
            })
    
    return result

def get_docker_containers():
    """Get Docker containers if Docker is installed"""
    # Check if docker is available
    docker_check = run_command("which docker")
    if not docker_check:
        return []
    
    cmd = "docker ps -a --format '{{.ID}}|{{.Names}}|{{.Status}}|{{.Image}}' 2>/dev/null"
    output = run_command(cmd)
    
    containers = []
    for line in output.split('\n'):
        if line:
            parts = line.split('|')
            if len(parts) >= 4:
                containers.append({
                    'id': parts[0][:12],
                    'name': parts[1],
                    'status': parts[2],
                    'image': parts[3],
                    'running': 'Up' in parts[2]
                })
    
    return containers

def get_logs(log_file, lines=50):
    """Get system logs"""
    valid_logs = {
        'syslog': '/var/log/syslog',
        'auth': '/var/log/auth.log',
        'opencode': '/var/log/opencode.log',
        'watchdog': '/var/log/opencode-watchdog.log'
    }
    
    if log_file not in valid_logs:
        return []
    
    path = valid_logs[log_file]
    if not os.path.exists(path):
        return []
    
    output = run_command(f"tail -n {lines} {path}")
    return output.split('\n')

def get_security_info():
    """Get security-related information"""
    # Failed SSH attempts
    failed_ssh = run_command("grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -20")
    failed_count = len(failed_ssh.split('\n')) if failed_ssh else 0
    
    # Active SSH sessions
    ssh_sessions = run_command("who")
    sessions = []
    for line in ssh_sessions.split('\n'):
        if line:
            parts = line.split()
            if len(parts) >= 5:
                sessions.append({
                    'user': parts[0],
                    'tty': parts[1],
                    'ip': parts[4].strip('()') if len(parts) > 4 else 'local'
                })
    
    # Firewall status
    ufw_status = run_command("ufw status 2>/dev/null | head -1")
    
    return {
        'failed_ssh_attempts': failed_count,
        'active_sessions': sessions,
        'firewall_status': ufw_status if ufw_status else 'Unknown'
    }

def get_cron_jobs():
    """Get cron jobs"""
    output = run_command("crontab -l 2>/dev/null")
    jobs = []
    
    for line in output.split('\n'):
        if line and not line.startswith('#'):
            jobs.append(line)
    
    return jobs

def get_hardware_info():
    """Get hardware information"""
    # Temperature (if available)
    temp = run_command("sensors 2>/dev/null | grep 'Core 0' | awk '{print $3}'")
    
    # Or try thermal zone
    if not temp:
        temp = run_command("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null")
        if temp and temp.isdigit():
            temp = f"{int(temp)/1000}°C"
    
    return {
        'temperature': temp if temp else 'N/A',
        'cpu_info': run_command("lscpu | grep 'Model name' | cut -d: -f2").strip()
    }

def get_quick_stats():
    """Get quick statistics"""
    processes = get_processes()
    
    top_mem = max(processes, key=lambda x: x['mem']) if processes else None
    top_cpu = max(processes, key=lambda x: x['cpu']) if processes else None
    
    return {
        'top_memory_process': {
            'pid': top_mem['pid'],
            'command': top_mem['command'][:50],
            'mem': top_mem['mem']
        } if top_mem else None,
        'top_cpu_process': {
            'pid': top_cpu['pid'],
            'command': top_cpu['command'][:50],
            'cpu': top_cpu['cpu']
        } if top_cpu else None,
        'total_processes': len(processes)
    }

class DashboardHandler(BaseHTTPRequestHandler):
    
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        
        if parsed.path == '/api/system':
            self._set_headers()
            data = get_system_info()
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/network':
            self._set_headers()
            data = get_network_stats()
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/disk-io':
            self._set_headers()
            data = get_disk_io()
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/processes':
            self._set_headers()
            data = get_processes()
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/ports':
            self._set_headers()
            data = get_ports()
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/services':
            self._set_headers()
            data = get_services()
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/docker':
            self._set_headers()
            data = get_docker_containers()
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/logs':
            self._set_headers()
            log_file = query.get('file', ['syslog'])[0]
            lines = int(query.get('lines', ['50'])[0])
            data = get_logs(log_file, lines)
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/security':
            self._set_headers()
            data = get_security_info()
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/cron':
            self._set_headers()
            data = get_cron_jobs()
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/hardware':
            self._set_headers()
            data = get_hardware_info()
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/quick-stats':
            self._set_headers()
            data = get_quick_stats()
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/history':
            self._set_headers()
            data = {
                'cpu': list(history_data['cpu']),
                'memory': list(history_data['memory']),
                'network': list(history_data['network']),
                'disk_io': list(history_data['disk_io'])
            }
            self.wfile.write(json.dumps(data).encode())
        
        elif parsed.path == '/api/all':
            self._set_headers()
            data = {
                'system': get_system_info(),
                'network': get_network_stats(),
                'disk_io': get_disk_io(),
                'processes': get_processes(),
                'ports': get_ports(),
                'services': get_services(),
                'docker': get_docker_containers(),
                'security': get_security_info(),
                'quick_stats': get_quick_stats(),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            self.wfile.write(json.dumps(data).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body) if body else {}
            
            if self.path == '/api/process/kill':
                pid = data.get('pid')
                if not pid:
                    raise ValueError('PID required')
                
                check = run_command(f"ps -p {pid} -o comm=")
                if not check:
                    raise ValueError(f'Process {pid} not found')
                
                run_command(f"kill -15 {pid}")
                
                self._set_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': f'Sent SIGTERM to process {pid} ({check})'
                }).encode())
            
            elif self.path == '/api/service/action':
                service = data.get('service')
                action = data.get('action')  # start, stop, restart
                
                if not service or not action:
                    raise ValueError('Service and action required')
                
                allowed_actions = ['start', 'stop', 'restart']
                if action not in allowed_actions:
                    raise ValueError('Invalid action')
                
                run_command(f"systemctl {action} {service}")
                
                self._set_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': f'{action.title()}ed service {service}'
                }).encode())
            
            elif self.path == '/api/docker/action':
                container_id = data.get('container')
                action = data.get('action')  # start, stop, restart
                
                if not container_id or not action:
                    raise ValueError('Container ID and action required')
                
                allowed_actions = ['start', 'stop', 'restart']
                if action not in allowed_actions:
                    raise ValueError('Invalid action')
                
                run_command(f"docker {action} {container_id}")
                
                self._set_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': f'{action.title()}ed container {container_id}'
                }).encode())
            
            elif self.path == '/api/system/clear-cache':
                # Clear RAM cache
                run_command("sync")
                run_command("echo 3 > /proc/sys/vm/drop_caches")
                
                self._set_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': 'Cleared system cache'
                }).encode())
            
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'Unknown endpoint'}).encode())
        
        except Exception as e:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), DashboardHandler)
    print(f'Advanced Server Dashboard API v2 running on port {PORT}')
    server.serve_forever()
