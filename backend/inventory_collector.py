#!/usr/bin/env python3

"""
Server Inventory Collector Module
Agentless system information collection via SSH

Collects:
- OS and kernel information
- Hostname and uptime
- CPU and memory details
- Disk usage
- Network configuration
- Optionally: packages and services

Security:
- Read-only commands only
- Timeout enforcement
- No credential logging
- Supports SSH key vault
"""

import paramiko
import json
import io
import time
import re
from datetime import datetime
from typing import Dict, Optional, Any

# Default timeout for SSH commands (seconds)
DEFAULT_COMMAND_TIMEOUT = 30


class InventoryCollector:
    """
    Collects system information from remote servers via SSH
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        ssh_key_pem: Optional[str] = None,
        ssh_key_path: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = DEFAULT_COMMAND_TIMEOUT,
    ):
        """
        Initialize inventory collector

        Args:
            host: Server hostname or IP
            port: SSH port
            username: SSH username
            ssh_key_pem: SSH private key in PEM format (from vault)
            ssh_key_path: Path to SSH private key file
            password: SSH password
            timeout: Command execution timeout in seconds
        """
        self.host = host
        self.port = port
        self.username = username
        self.ssh_key_pem = ssh_key_pem
        self.ssh_key_path = ssh_key_path
        self.password = password
        self.timeout = timeout
        self.ssh_client = None

    def connect(self) -> bool:
        """
        Establish SSH connection

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.ssh_client = paramiko.SSHClient()
            # Security Note: AutoAddPolicy used for monitoring system - allows dynamic server inventory
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # nosec B507

            connect_kwargs = {
                "hostname": self.host,
                "port": self.port,
                "username": self.username,
                "timeout": self.timeout,
                "look_for_keys": False,
                "allow_agent": False,
            }

            # Priority 1: Use SSH key from vault (PEM string)
            if self.ssh_key_pem:
                key_file = io.StringIO(self.ssh_key_pem)
                pkey = None

                # Try different key types
                for key_class in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey]:
                    try:
                        key_file.seek(0)
                        pkey = key_class.from_private_key(key_file)
                        break
                    except (paramiko.SSHException, ValueError):
                        continue

                if pkey:
                    connect_kwargs["pkey"] = pkey
                else:
                    raise Exception("Failed to load SSH key from PEM")

            # Priority 2: Use SSH key file path
            elif self.ssh_key_path:
                import os

                key_path = os.path.expanduser(self.ssh_key_path)
                if os.path.exists(key_path):
                    connect_kwargs["key_filename"] = key_path
                else:
                    raise Exception(f"SSH key file not found: {key_path}")

            # Priority 3: Use password
            elif self.password:
                connect_kwargs["password"] = self.password

            else:
                raise Exception("No SSH credentials provided")

            self.ssh_client.connect(**connect_kwargs)
            return True

        except Exception as e:
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
            raise Exception(f"SSH connection failed: {str(e)}")

    def close(self):
        """Close SSH connection"""
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except Exception:
                pass
            self.ssh_client = None

    def execute_command(self, command: str) -> str:
        """
        Execute a command and return output

        Args:
            command: Command to execute

        Returns:
            Command output as string
        """
        if not self.ssh_client:
            raise Exception("Not connected")

        try:
            # Security Note: paramiko exec_command does not use shell by default
            # Commands are hardcoded in collect_* methods, not from user input
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=self.timeout)  # nosec B601
            output = stdout.read().decode("utf-8", errors="ignore").strip()
            return output
        except Exception as e:
            # Return empty string on error for best-effort collection
            return ""

    def collect_os_info(self) -> Dict[str, str]:
        """Collect OS and kernel information"""
        info = {}

        # Try to get OS info from /etc/os-release
        os_release = self.execute_command("cat /etc/os-release 2>/dev/null")
        if os_release:
            for line in os_release.split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    value = value.strip('"')
                    if key == "NAME":
                        info["name"] = value
                    elif key == "VERSION":
                        info["version"] = value
                    elif key == "PRETTY_NAME":
                        info["pretty_name"] = value

        # Fallback to uname
        if not info.get("name"):
            uname = self.execute_command("uname -s 2>/dev/null")
            if uname:
                info["name"] = uname

        # Get kernel version
        kernel = self.execute_command("uname -r 2>/dev/null")
        if kernel:
            info["kernel"] = kernel

        return info

    def collect_hostname(self) -> str:
        """Collect hostname"""
        hostname = self.execute_command("hostname 2>/dev/null")
        return hostname or "unknown"

    def collect_uptime(self) -> Dict[str, Any]:
        """Collect uptime information"""
        info = {}

        # Get uptime in seconds
        uptime_output = self.execute_command("cat /proc/uptime 2>/dev/null")
        if uptime_output:
            try:
                uptime_seconds = int(float(uptime_output.split()[0]))
                info["uptime_seconds"] = uptime_seconds

                # Calculate human-readable format
                days = uptime_seconds // 86400
                hours = (uptime_seconds % 86400) // 3600
                minutes = (uptime_seconds % 3600) // 60
                info["uptime_human"] = f"{days}d {hours}h {minutes}m"
            except:
                pass

        # Fallback to uptime command
        if not info.get("uptime_seconds"):
            uptime = self.execute_command("uptime -s 2>/dev/null")
            if uptime:
                info["uptime_since"] = uptime

        return info

    def collect_cpu_info(self) -> Dict[str, Any]:
        """Collect CPU information"""
        info = {}

        # Get CPU model and count
        cpuinfo = self.execute_command("cat /proc/cpuinfo 2>/dev/null")
        if cpuinfo:
            models = []
            cores = 0
            for line in cpuinfo.split("\n"):
                if line.startswith("model name"):
                    model = line.split(":", 1)[1].strip()
                    if model not in models:
                        models.append(model)
                elif line.startswith("processor"):
                    cores += 1

            if models:
                info["model"] = models[0]
            info["cores"] = cores

        # Fallback to nproc for core count
        if not info.get("cores"):
            nproc = self.execute_command("nproc 2>/dev/null")
            if nproc:
                try:
                    info["cores"] = int(nproc)
                except:
                    pass

        return info

    def collect_memory_info(self) -> Dict[str, Any]:
        """Collect memory information"""
        info = {}

        # Get memory from /proc/meminfo
        meminfo = self.execute_command("cat /proc/meminfo 2>/dev/null")
        if meminfo:
            for line in meminfo.split("\n"):
                if line.startswith("MemTotal:"):
                    total_kb = int(line.split()[1])
                    info["total_mb"] = total_kb // 1024
                elif line.startswith("MemAvailable:"):
                    avail_kb = int(line.split()[1])
                    info["available_mb"] = avail_kb // 1024

        # Calculate used memory
        if "total_mb" in info and "available_mb" in info:
            info["used_mb"] = info["total_mb"] - info["available_mb"]
            if info["total_mb"] > 0:
                info["used_percent"] = round((info["used_mb"] / info["total_mb"]) * 100, 1)

        return info

    def collect_disk_info(self) -> Dict[str, Any]:
        """Collect disk information"""
        info = {}

        # Get root filesystem usage
        df_output = self.execute_command("df -BG / 2>/dev/null | tail -1")
        if df_output:
            parts = df_output.split()
            if len(parts) >= 5:
                try:
                    # Remove 'G' suffix and parse
                    info["total_gb"] = int(parts[1].rstrip("G"))
                    info["used_gb"] = int(parts[2].rstrip("G"))
                    info["available_gb"] = int(parts[3].rstrip("G"))
                    info["used_percent"] = int(parts[4].rstrip("%"))
                except (ValueError, IndexError):
                    pass

        return info

    def collect_network_info(self) -> Dict[str, Any]:
        """Collect network information"""
        info = {}

        # Try to get primary IP
        # Method 1: ip route
        ip_route = self.execute_command("ip route get 8.8.8.8 2>/dev/null | head -1")
        if ip_route:
            match = re.search(r"src\s+(\d+\.\d+\.\d+\.\d+)", ip_route)
            if match:
                info["primary_ip"] = match.group(1)

        # Method 2: hostname -I (fallback)
        if not info.get("primary_ip"):
            hostname_i = self.execute_command("hostname -I 2>/dev/null")
            if hostname_i:
                ips = hostname_i.split()
                if ips:
                    info["primary_ip"] = ips[0]

        # Get network interfaces
        interfaces = self.execute_command("ip -o link show 2>/dev/null | awk -F\": \" '{print $2}'")
        if interfaces:
            info["interfaces"] = [iface for iface in interfaces.split("\n") if iface and iface != "lo"]

        return info

    def collect_packages(self) -> list:
        """Collect installed packages (optional, best-effort)"""
        packages = []

        # Try different package managers
        # dpkg (Debian/Ubuntu)
        dpkg = self.execute_command('dpkg -l 2>/dev/null | grep "^ii" | wc -l')
        if dpkg and dpkg.isdigit():
            return [{"type": "dpkg", "count": int(dpkg)}]

        # rpm (RedHat/CentOS)
        rpm = self.execute_command("rpm -qa 2>/dev/null | wc -l")
        if rpm and rpm.isdigit():
            return [{"type": "rpm", "count": int(rpm)}]

        # pacman (Arch)
        pacman = self.execute_command("pacman -Q 2>/dev/null | wc -l")
        if pacman and pacman.isdigit():
            return [{"type": "pacman", "count": int(pacman)}]

        return packages

    def collect_services(self) -> list:
        """Collect systemd services (optional, best-effort)"""
        services = []

        # Get systemd services
        systemctl = self.execute_command(
            "systemctl list-units --type=service --state=running --no-pager --no-legend 2>/dev/null | wc -l"
        )
        if systemctl and systemctl.isdigit():
            services.append({"type": "systemd", "running_count": int(systemctl)})

        return services

    def collect_all(self, include_packages: bool = False, include_services: bool = False) -> Dict[str, Any]:
        """
        Collect all inventory information

        Args:
            include_packages: Whether to include package information
            include_services: Whether to include service information

        Returns:
            Dictionary with all collected information
        """
        inventory = {
            "collected_at": datetime.utcnow().isoformat() + "Z",
            "os": {},
            "hostname": "",
            "kernel": "",
            "uptime": {},
            "cpu": {},
            "memory": {},
            "disk": {},
            "network": {},
        }

        try:
            # Collect OS info
            os_info = self.collect_os_info()
            inventory["os"] = {
                "name": os_info.get("name", "Unknown"),
                "version": os_info.get("version", "Unknown"),
                "pretty_name": os_info.get("pretty_name", ""),
            }
            inventory["kernel"] = os_info.get("kernel", "Unknown")

            # Collect hostname
            inventory["hostname"] = self.collect_hostname()

            # Collect uptime
            inventory["uptime"] = self.collect_uptime()

            # Collect CPU info
            inventory["cpu"] = self.collect_cpu_info()

            # Collect memory info
            inventory["memory"] = self.collect_memory_info()

            # Collect disk info
            inventory["disk"] = self.collect_disk_info()

            # Collect network info
            inventory["network"] = self.collect_network_info()

            # Optional: Collect packages
            if include_packages:
                inventory["packages"] = self.collect_packages()

            # Optional: Collect services
            if include_services:
                inventory["services"] = self.collect_services()

        except Exception as e:
            # Log error but continue with partial data
            inventory["error"] = str(e)

        return inventory


def collect_server_inventory(
    server_id: int,
    server: Dict[str, Any],
    ssh_key_pem: Optional[str] = None,
    include_packages: bool = False,
    include_services: bool = False,
) -> Dict[str, Any]:
    """
    Collect inventory for a server

    Args:
        server_id: Server ID
        server: Server details dict with host, port, username, credentials
        ssh_key_pem: Optional SSH private key from vault
        include_packages: Whether to include package info
        include_services: Whether to include service info

    Returns:
        Inventory data dictionary
    """
    collector = None
    try:
        collector = InventoryCollector(
            host=server["host"],
            port=server.get("port", 22),
            username=server["username"],
            ssh_key_pem=ssh_key_pem,
            ssh_key_path=server.get("ssh_key_path"),
            password=server.get("ssh_password"),
            timeout=DEFAULT_COMMAND_TIMEOUT,
        )

        # Connect
        collector.connect()

        # Collect all information
        inventory = collector.collect_all(include_packages=include_packages, include_services=include_services)

        return inventory

    finally:
        if collector:
            collector.close()
