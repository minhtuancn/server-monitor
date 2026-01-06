#!/usr/bin/env python3

"""
Lightweight Monitoring Agent
This script runs on remote servers/LXC containers
Provides monitoring data via HTTP API
Minimal dependencies - only uses Python standard library
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import time
from collections import deque
from datetime import datetime

# Version
VERSION = '4.0.0'

# Configuration
PORT = 8083
HOST = '0.0.0.0'

# Historical data storage (in-memory, last 30 minutes)
history_data = {
    'cpu': deque(maxlen=360),
    'memory': deque(maxlen=360),
    'network': deque(maxlen=360),
    'disk_io': deque(maxlen=360)
}

# Network stats tracking
last_network_stats = {'rx_bytes': 0, 'tx_bytes': 0, 'timestamp': time.time()}
last_disk_io = {'read_bytes': 0, 'write_bytes': 0, 'timestamp': time.time()}

def run_command(cmd):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except:
        return ""

def get_os_info():
    """Get detailed OS information"""
    # OS Name and Version
    os_name = run_command("cat /etc/os-release | grep '^PRETTY_NAME' | cut -d'\"' -f2")
    if not os_name:
        os_name = run_command("cat /etc/issue | head -1").strip()
    if not os_name:
        os_name = run_command("uname -o")
    
    # Kernel version
    kernel = run_command("uname -r")
    
    # Architecture
    arch = run_command("uname -m")
    
    # Distro ID
    distro_id = run_command("cat /etc/os-release | grep '^ID=' | cut -d'=' -f2 | tr -d '\"'")
    
    # Version ID
    version_id = run_command("cat /etc/os-release | grep '^VERSION_ID=' | cut -d'=' -f2 | tr -d '\"'")
    
    # Is container (LXC/Docker)
    is_container = False
    container_type = None
    
    # Check for LXC - check if running inside container
    lxc_check = run_command("cat /proc/1/environ 2>/dev/null | tr '\\0' '\\n' | grep -i container")
    if lxc_check:
        is_container = True
        container_type = 'lxc'
    
    # Check for Docker
    if not is_container:
        docker_check = run_command("cat /proc/1/cgroup 2>/dev/null | grep docker")
        if docker_check:
            is_container = True
            container_type = 'docker'
    
    # Check for LXC via cgroup
    if not is_container:
        lxc_cgroup = run_command("cat /proc/1/cgroup 2>/dev/null | grep lxc")
        if lxc_cgroup:
            is_container = True
            container_type = 'lxc'
    
    # Check for container via systemd-detect-virt
    if not is_container:
        virt_type = run_command("systemd-detect-virt 2>/dev/null")
        if virt_type in ['lxc', 'lxc-libvirt']:
            is_container = True
            container_type = 'lxc'
        elif virt_type == 'docker':
            is_container = True
            container_type = 'docker'
    
    return {
        'name': os_name or 'Unknown',
        'kernel': kernel or 'Unknown',
        'arch': arch or 'Unknown',
        'distro_id': distro_id or 'unknown',
        'version_id': version_id or '',
        'is_container': is_container,
        'container_type': container_type
    }

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
        'os': get_os_info(),
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
    
    output = run_command("cat /proc/net/dev")
    total_rx = 0
    total_tx = 0
    
    for line in output.split('\n'):
        if ':' in line and 'lo' not in line:
            parts = line.split()
            if len(parts) >= 10:
                total_rx += int(parts[1])
                total_tx += int(parts[9])
    
    current_time = time.time()
    time_diff = current_time - last_network_stats['timestamp']
    
    if time_diff > 0:
        rx_speed = (total_rx - last_network_stats['rx_bytes']) / time_diff / 1024 / 1024
        tx_speed = (total_tx - last_network_stats['tx_bytes']) / time_diff / 1024 / 1024
    else:
        rx_speed = 0
        tx_speed = 0
    
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
    
    output = run_command("cat /proc/diskstats | grep -E 'sda|vda|nvme0n1' | head -1")
    if not output:
        return {'read_speed': 0, 'write_speed': 0, 'iops': 0}
    
    parts = output.split()
    if len(parts) < 14:
        return {'read_speed': 0, 'write_speed': 0, 'iops': 0}
    
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
    """Get running processes (top 50 by memory)"""
    cmd = "ps aux --sort=-%mem | head -51"
    output = run_command(cmd)
    
    processes = []
    for line in output.split('\n')[1:]:
        parts = line.split(None, 10)
        if len(parts) >= 11:
            processes.append({
                'user': parts[0],
                'pid': parts[1],
                'cpu': float(parts[2]),
                'mem': float(parts[3]),
                'command': parts[10][:100]
            })
    
    return processes

def get_services():
    """Get systemd services status"""
    services = [
        'ssh.service',
        'docker.service',
        'nginx.service',
        'mysql.service'
    ]
    
    result = []
    for svc in services:
        status = run_command(f"systemctl is-active {svc} 2>/dev/null")
        if status:
            result.append({
                'name': svc,
                'status': status
            })
    
    return result

class AgentHandler(BaseHTTPRequestHandler):
    
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/health':
            self._set_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'agent': 'running'}).encode())
        
        elif self.path == '/api/system':
            self._set_headers()
            data = get_system_info()
            self.wfile.write(json.dumps(data).encode())
        
        elif self.path == '/api/network':
            self._set_headers()
            data = get_network_stats()
            self.wfile.write(json.dumps(data).encode())
        
        elif self.path == '/api/disk-io':
            self._set_headers()
            data = get_disk_io()
            self.wfile.write(json.dumps(data).encode())
        
        elif self.path == '/api/processes':
            self._set_headers()
            data = get_processes()
            self.wfile.write(json.dumps(data).encode())
        
        elif self.path == '/api/services':
            self._set_headers()
            data = get_services()
            self.wfile.write(json.dumps(data).encode())
        
        elif self.path == '/api/all':
            self._set_headers()
            data = {
                'system': get_system_info(),
                'network': get_network_stats(),
                'disk_io': get_disk_io(),
                'processes': get_processes(),
                'services': get_services(),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            self.wfile.write(json.dumps(data).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), AgentHandler)
    print(f'Lightweight Monitoring Agent running on {HOST}:{PORT}')
    print('Endpoints:')
    print(f'  - http://{HOST}:{PORT}/api/health')
    print(f'  - http://{HOST}:{PORT}/api/all')
    server.serve_forever()
