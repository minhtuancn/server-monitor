#!/usr/bin/env python3

"""
Task Safety Policy Module
Implements command denylist/allowlist to prevent dangerous operations
"""

import os
import re
from typing import List, Dict, Tuple

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Task policy mode: 'denylist' (default) or 'allowlist'
TASK_POLICY_MODE = os.environ.get('TASK_POLICY_MODE', 'denylist').lower()

# Default dangerous command patterns (denylist)
DEFAULT_DANGEROUS_PATTERNS = [
    # Filesystem destruction
    r'\brm\s+(-[rRfF]*\s+)*/',  # rm -rf / or variants
    r'\brm\s+(-[rRfF]*\s+)*/\s',
    r'\bmkfs\b',  # Make filesystem (formats partition)
    r'\bdd\b.*\bof=/dev/',  # dd to device (can destroy data)
    
    # System control
    r'\bshutdown\b',
    r'\breboot\b',
    r'\bhalt\b',
    r'\bpoweroff\b',
    r'\binit\s+[06]',  # init 0 (shutdown) or 6 (reboot)
    
    # User/permission manipulation
    r'\busermod\b',
    r'\bpasswd\b',
    r'\bchmod\s+777',  # Overly permissive
    r'\bchown\s+.*\s+/',  # chown on root
    r'\bvisudo\b',
    
    # Package management (potentially disruptive)
    r'\bapt-get\s+(remove|purge|autoremove)',
    r'\byum\s+(remove|erase)',
    r'\bdnf\s+(remove|erase)',
    
    # Kernel/boot manipulation
    r'\bgrub-',
    r'\bupdate-grub\b',
    r'\bmodprobe\b',
    r'\binsmod\b',
    r'\brmmod\b',
    
    # Network disruption
    r'\bifconfig\s+\w+\s+down',
    r'\bip\s+link\s+set\s+\w+\s+down',
    r'\biptables\s+-F',  # Flush firewall rules
    
    # Fork bombs and resource exhaustion
    r':\(\)\{.*:\|:.*\};:',  # Classic fork bomb
    r'\bwhile\s+true\b.*\bfork\b',
    
    # Dangerous redirects
    r'>\s*/dev/sd[a-z]',  # Writing to disk device
    r'>\s*/dev/nvme',
]

# Custom patterns from environment (comma-separated)
CUSTOM_DENY_PATTERNS = os.environ.get('TASK_DENY_PATTERNS', '').split(',')
CUSTOM_DENY_PATTERNS = [p.strip() for p in CUSTOM_DENY_PATTERNS if p.strip()]

# Allowlist patterns (if using allowlist mode)
DEFAULT_ALLOW_PATTERNS = [
    r'^ls\b',
    r'^cat\b',
    r'^grep\b',
    r'^echo\b',
    r'^pwd$',
    r'^whoami$',
    r'^date$',
    r'^uptime$',
    r'^df\b',
    r'^du\b',
    r'^ps\b',
    r'^top\b',
    r'^free\b',
    r'^netstat\b',
    r'^ss\b',
    r'^systemctl\s+status\b',
    r'^journalctl\b',
    r'^tail\b',
    r'^head\b',
    r'^wc\b',
]

CUSTOM_ALLOW_PATTERNS = os.environ.get('TASK_ALLOW_PATTERNS', '').split(',')
CUSTOM_ALLOW_PATTERNS = [p.strip() for p in CUSTOM_ALLOW_PATTERNS if p.strip()]


class TaskPolicyViolation(Exception):
    """Exception raised when a command violates the task policy"""
    pass


class TaskPolicy:
    """
    Task safety policy engine
    Validates commands against denylist/allowlist patterns
    """
    
    def __init__(self, mode: str = None):
        """
        Initialize task policy
        
        Args:
            mode: 'denylist' or 'allowlist'. Defaults to TASK_POLICY_MODE env var.
        """
        self.mode = mode or TASK_POLICY_MODE
        
        # Compile patterns for efficiency
        if self.mode == 'allowlist':
            self.patterns = [re.compile(p, re.IGNORECASE) for p in DEFAULT_ALLOW_PATTERNS + CUSTOM_ALLOW_PATTERNS]
        else:  # denylist
            self.patterns = [re.compile(p, re.IGNORECASE) for p in DEFAULT_DANGEROUS_PATTERNS + CUSTOM_DENY_PATTERNS]
    
    def validate_command(self, command: str) -> Tuple[bool, str]:
        """
        Validate a command against the policy
        
        Args:
            command: Command string to validate
            
        Returns:
            Tuple of (is_valid, reason)
            
        Raises:
            TaskPolicyViolation if command violates policy
        """
        # Basic validation
        if not command or not command.strip():
            return False, "Command is empty"
        
        command = command.strip()
        
        if self.mode == 'allowlist':
            # In allowlist mode, command must match at least one allowed pattern
            for pattern in self.patterns:
                if pattern.search(command):
                    return True, "Command matches allowlist"
            
            return False, f"Command not in allowlist. Allowlist mode requires explicit approval."
        
        else:  # denylist mode
            # In denylist mode, command must not match any dangerous pattern
            for pattern in self.patterns:
                if pattern.search(command):
                    return False, f"Command matches dangerous pattern: {pattern.pattern}"
            
            return True, "Command passes denylist check"
    
    def check_command(self, command: str, raise_on_violation: bool = True) -> bool:
        """
        Check if command is allowed
        
        Args:
            command: Command to check
            raise_on_violation: If True, raise exception on violation. If False, return False.
            
        Returns:
            True if allowed, False if not allowed (when raise_on_violation=False)
            
        Raises:
            TaskPolicyViolation if command violates policy and raise_on_violation=True
        """
        is_valid, reason = self.validate_command(command)
        
        if not is_valid and raise_on_violation:
            raise TaskPolicyViolation(reason)
        
        return is_valid
    
    def get_policy_info(self) -> Dict:
        """
        Get policy configuration information
        
        Returns:
            Dict with policy mode and pattern counts
        """
        return {
            'mode': self.mode,
            'pattern_count': len(self.patterns),
            'default_patterns': len(DEFAULT_DANGEROUS_PATTERNS) if self.mode == 'denylist' else len(DEFAULT_ALLOW_PATTERNS),
            'custom_patterns': len(CUSTOM_DENY_PATTERNS) if self.mode == 'denylist' else len(CUSTOM_ALLOW_PATTERNS)
        }


# Global policy instance
_task_policy = None

def get_task_policy() -> TaskPolicy:
    """Get or create global task policy instance"""
    global _task_policy
    if _task_policy is None:
        _task_policy = TaskPolicy()
    return _task_policy


def validate_task_command(command: str) -> Tuple[bool, str]:
    """
    Convenience function to validate a task command
    
    Args:
        command: Command to validate
        
    Returns:
        Tuple of (is_valid, reason)
    """
    policy = get_task_policy()
    return policy.validate_command(command)


if __name__ == '__main__':
    # Test the policy
    policy = TaskPolicy()
    
    print(f"Task Policy Mode: {policy.mode}")
    print(f"Loaded {len(policy.patterns)} patterns\n")
    
    # Test dangerous commands
    dangerous_tests = [
        "rm -rf /",
        "shutdown -h now",
        "dd if=/dev/zero of=/dev/sda",
        "chmod 777 /etc/passwd",
        "mkfs.ext4 /dev/sda1",
    ]
    
    safe_tests = [
        "ls -la",
        "cat /var/log/syslog",
        "grep error /var/log/app.log",
        "systemctl status nginx",
        "df -h",
    ]
    
    print("Testing dangerous commands (should be blocked):")
    for cmd in dangerous_tests:
        is_valid, reason = policy.validate_command(cmd)
        status = "❌ BLOCKED" if not is_valid else "⚠️  ALLOWED"
        print(f"  {status}: {cmd}")
        if not is_valid:
            print(f"    Reason: {reason}")
    
    print("\nTesting safe commands (should be allowed):")
    for cmd in safe_tests:
        is_valid, reason = policy.validate_command(cmd)
        status = "✓ ALLOWED" if is_valid else "✗ BLOCKED"
        print(f"  {status}: {cmd}")
        if not is_valid:
            print(f"    Reason: {reason}")
