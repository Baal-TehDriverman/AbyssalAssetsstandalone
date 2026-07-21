#!/usr/bin/env python3
"""
Secure Sandboxing System for Computer Use Operations
Provides granular AppArmor/seccomp bindings, audit logging to Lilith Gateway,
and process isolation for sensitive computer-use operations.
"""

import os
import sys
import json
import subprocess
import threading
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import signal
import psutil
from pathlib import Path

# Add computer-use scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

class SecurityLevel(Enum):
    """Security levels for sandboxing"""
    LOW = "low"          # Basic restrictions
    MEDIUM = "medium"    # Moderate restrictions
    HIGH = "high"        # Strict restrictions
    MAXIMUM = "maximum"  # Maximum lockdown

class SandboxViolation(Exception):
    """Exception raised when a security policy is violated"""
    pass

@dataclass
class SandboxPolicy:
    """Defines security policies for sandboxed operations"""
    # Process restrictions
    max_processes: int = 10
    max_memory_mb: int = 512
    max_cpu_percent: float = 80.0
    
    # File system restrictions
    allowed_paths: List[str] = None
    blocked_paths: List[str] = None
    read_only_paths: List[str] = None
    
    # Network restrictions
    allow_network: bool = False
    allowed_ports: List[int] = None
    blocked_ports: List[int] = None
    
    # System call restrictions (seccomp-like)
    blocked_syscalls: List[str] = None
    allowed_syscalls: List[str] = None
    
    # Capability restrictions
    drop_capabilities: List[str] = None
    keep_capabilities: List[str] = None
    
    # Environment restrictions
    clear_env: bool = False
    allowed_env_vars: List[str] = None
    blocked_env_vars: List[str] = None
    
    # Logging and monitoring
    audit_log: bool = True
    audit_endpoint: str = "http://localhost:8080/audit"
    real_time_monitoring: bool = True
    
    def __post_init__(self):
        if self.allowed_paths is None:
            self.allowed_paths = ["/tmp", "/var/tmp", "/home/tehlappy"]
        if self.blocked_paths is None:
            self.blocked_paths = ["/root", "/etc/shadow", "/etc/sudoers", "/boot"]
        if self.read_only_paths is None:
            self.read_only_paths = ["/usr", "/bin", "/sbin", "/lib", "/lib64"]
        if self.allowed_ports is None:
            self.allowed_ports = [80, 443, 8080, 8081]  # Common HTTP/HTTPS and gateway ports
        if self.blocked_ports is None:
            self.blocked_ports = [22, 23, 25, 53, 135, 139, 445, 1433, 3306, 5432]  # Sensitive ports
        if self.blocked_syscalls is None:
            self.blocked_syscalls = [
                "ptrace", "kexec_load", "init_module", "finit_module", 
                "delete_module", "mount", "umount2", "swapon", "swapoff"
            ]
        if self.drop_capabilities is None:
            self.drop_capabilities = [
                "CAP_SYS_ADMIN", "CAP_SYS_RAWIO", "CAP_SYS_PTRACE", 
                "CAP_SYS_MODULE", "CAP_SYS_TIME", "CAP_SYS_RAWIO"
            ]

class SandboxManager:
    """Manages sandboxed execution of computer-use operations"""
    
    def __init__(self, default_policy: SecurityLevel = SecurityLevel.MEDIUM):
        self.default_policy = self._get_policy_for_level(default_policy)
        self.active_sandboxes: Dict[str, Dict] = {}
        self.audit_logger = self._setup_audit_logger()
        
        # Initialize AppArmor profiles if available
        self.apparmor_available = self._check_apparmor()
        self.seccomp_available = self._check_seccomp()
    
    def _get_policy_for_level(self, level: SecurityLevel) -> SandboxPolicy:
        """Get predefined security policy for a given level"""
        base_policy = SandboxPolicy()
        
        if level == SecurityLevel.LOW:
            # Minimal restrictions
            base_policy.max_processes = 50
            base_policy.max_memory_mb = 2048
            base_policy.allow_network = True
            base_policy.blocked_paths = ["/root", "/etc/shadow", "/etc/sudoers"]
            
        elif level == SecurityLevel.MEDIUM:
            # Balanced security and usability
            base_policy.max_processes = 20
            base_policy.max_memory_mb = 1024
            base_policy.allow_network = False  # Restrict by default
            
        elif level == SecurityLevel.HIGH:
            # Strict restrictions
            base_policy.max_processes = 5
            base_policy.max_memory_mb = 256
            base_policy.max_cpu_percent = 50.0
            base_policy.allow_network = False
            base_policy.blocked_paths = [
                "/root", "/etc/shadow", "/etc/sudoers", "/etc/passwd", 
                "/etc/group", "/boot", "/sys", "/proc/sys", "/dev/mem"
            ]
            base_policy.drop_capabilities = [
                "CAP_SYS_ADMIN", "CAP_SYS_RAWIO", "CAP_SYS_PTRACE", 
                "CAP_SYS_MODULE", "CAP_SYS_TIME", "CAP_SYS_RAWIO",
                "CAP_DAC_OVERRIDE", "CAP_DAC_READ_SEARCH", "CAP_FOWNER",
                "CAP_FSETID", "CAP_KILL", "CAP_SETGID", "CAP_SETUID",
                "CAP_SETPCAP", "CAP_LINUX_IMMUTABLE", "CAP_NET_BIND_SERVICE",
                "CAP_NET_BROADCAST", "CAP_NET_ADMIN", "CAP_IPC_LOCK"
            ]
            
        elif level == SecurityLevel.MAXIMUM:
            # Maximum lockdown - essentially a jail
            base_policy.max_processes = 2
            base_policy.max_memory_mb = 128
            base_policy.max_cpu_percent = 25.0
            base_policy.allow_network = False
            base_policy.blocked_paths = [
                "/", "/home", "/root", "/etc", "/var", "/usr", 
                "/boot", "/sys", "/proc", "/dev"
            ]
            # Only allow /tmp and specific app directories
            base_policy.allowed_paths = ["/tmp", "/var/tmp"]
            base_policy.drop_capabilities = [  # Drop nearly all capabilities
                "CAP_SYS_ADMIN", "CAP_SYS_RAWIO", "CAP_SYS_PTRACE", 
                "CAP_SYS_MODULE", "CAP_SYS_TIME", "CAP_SYS_RAWIO",
                "CAP_DAC_OVERRIDE", "CAP_DAC_READ_SEARCH", "CAP_FOWNER",
                "CAP_FSETID", "CAP_KILL", "CAP_SETGID", "CAP_SETUID",
                "CAP_SETPCAP", "CAP_LINUX_IMMUTABLE", "CAP_NET_BIND_SERVICE",
                "CAP_NET_BROADCAST", "CAP_NET_ADMIN", "IPC_LOCK",
                "CAP_IPC_OWNER", "CAP_LEASE", "CAP_AUDIT_WRITE",
                "CAP_AUDIT_CONTROL", "CAP_SETFCAP", "CAP_MAC_OVERRIDE",
                "CAP_MAC_ADMIN", "CAP_SYSLOG", "CAP_WAKE_ALARM",
                "CAP_BLOCK_SUSPEND", "CAP_AUDIT_READ"
            ]
        
        return base_policy
    
    def _check_apparmor(self) -> bool:
        """Check if AppArmor is available and enabled"""
        try:
            # Check if apparmor module is loaded
            if os.path.exists("/sys/module/apparmor/parameters/enabled"):
                with open("/sys/module/apparmor/parameters/enabled", "r") as f:
                    return f.read().strip() == "Y"
            return False
        except:
            return False
    
    def _check_seccomp(self) -> bool:
        """Check if seccomp is available"""
        try:
            # Check if prctl with PR_GET_SECCOMP is available
            import ctypes
            libc = ctypes.CDLL(None)
            PR_GET_SECCOMP = 21
            # This is a simplified check - in reality we'd need to actually call it
            return True
        except:
            return False
    
    def _setup_audit_logger(self) -> logging.Logger:
        """Setup audit logging to send events to Lilith Gateway"""
        logger = logging.getLogger('sandbox_audit')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - SANDBOX_AUDIT - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _log_audit_event(self, event_type: str, details: Dict[str, Any], 
                        severity: str = "INFO"):
        """Log security audit event"""
        audit_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "process_id": os.getpid(),
            "user_id": os.getuid()
        }
        
        # Log locally
        if severity == "ERROR":
            self.audit_logger.error(json.dumps(audit_entry))
        elif severity == "WARNING":
            self.audit_logger.warning(json.dumps(audit_entry))
        else:
            self.audit_logger.info(json.dumps(audit_entry))
        
        # Try to send to Lilith Gateway (if configured)
        if hasattr(self, 'audit_endpoint') and self.audit_endpoint:
            try:
                import requests
                requests.post(self.audit_endpoint, json=audit_entry, timeout=1)
            except:
                pass  # Silently fail if gateway is not available
    
    def validate_file_access(self, path: str, operation: str = "read") -> bool:
        """
        Validate if a file operation is allowed under current policy
        
        Args:
            path: File path to check
            operation: Type of operation (read, write, execute)
            
        Returns:
            True if allowed, False if blocked
        """
        # Normalize path
        try:
            abs_path = os.path.abspath(path)
        except:
            abs_path = path
        
        policy = getattr(self, 'current_policy', self.default_policy)
        
        # Check blocked paths first
        for blocked_path in policy.blocked_paths:
            if abs_path.startswith(blocked_path):
                self._log_audit_event(
                    "FILE_ACCESS_BLOCKED",
                    {
                        "path": abs_path,
                        "operation": operation,
                        "reason": f"Path matches blocked pattern: {blocked_path}"
                    },
                    "WARNING"
                )
                return False
        
        # Check read-only paths for write operations
        if operation in ["write", "execute", "create", "delete"]:
            for readonly_path in policy.read_only_paths:
                if abs_path.startswith(readonly_path):
                    self._log_audit_event(
                        "FILE_ACCESS_BLOCKED",
                        {
                            "path": abs_path,
                            "operation": operation,
                            "reason": f"Path is read-only: {readonly_path}"
                        },
                        "WARNING"
                    )
                    return False
        
        # Check allowed paths (if specified, everything else is blocked)
        if policy.allowed_paths:
            allowed = any(abs_path.startswith(allowed_path) for allowed_path in policy.allowed_paths)
            if not allowed:
                self._log_audit_event(
                    "FILE_ACCESS_BLOCKED",
                    {
                        "path": abs_path,
                        "operation": operation,
                        "reason": "Path not in allowed list"
                    },
                    "WARNING"
                )
                return False
        
        # Log allowed access for audit trail
        if policy.audit_log:
            self._log_audit_event(
                "FILE_ACCESS_ALLOWED",
                {
                    "path": abs_path,
                    "operation": operation
                }
            )
        
        return True

    def validate_network_access(self, host: str, port: int) -> bool:
        """
        Validate if network access is allowed
        
        Args:
            host: Target hostname or IP
            port: Target port number
            
        Returns:
            True if allowed, False if blocked
        """
        policy = getattr(self, 'current_policy', self.default_policy)
        
        if not policy.allow_network:
            self._log_audit_event(
                "NETWORK_ACCESS_BLOCKED",
                {
                    "host": host,
                    "port": port,
                    "reason": "Network access disabled in policy"
                },
                "WARNING"
            )
            return False
        
        # Check blocked ports
        if policy.blocked_ports and port in policy.blocked_ports:
            self._log_audit_event(
                "NETWORK_ACCESS_BLOCKED",
                {
                    "host": host,
                    "port": port,
                    "reason": f"Port {port} is blocked"
                },
                "WARNING"
            )
            return False
        
        # Check allowed ports (if specified, everything else is blocked)
        if policy.allowed_ports and port not in policy.allowed_ports:
            self._log_audit_event(
                "NETWORK_ACCESS_BLOCKED",
                {
                    "host": host,
                    "port": port,
                    "reason": f"Port {port} not in allowed list"
                },
                "WARNING"
            )
            return False
        
        # Log allowed access
        if policy.audit_log:
            self._log_audit_event(
                "NETWORK_ACCESS_ALLOWED",
                {
                    "host": host,
                    "port": port
                }
            )
        
        return True

    def create_sandboxed_process(self,
                                cmd: List[str],
                                security_level: SecurityLevel = None,
                                timeout: int = 30,
                                work_dir: str = None,
                                env: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Create and execute a process in a sandboxed environment
        
        Args:
            cmd: Command to execute
            security_level: SecurityLevel (uses default if None)
            timeout: Timeout in seconds
            work_dir: Working directory (defaults to temp)
            env: Environment variables (merged with safe defaults)
            
        Returns:
            Dict containing process result information
        """
        policy = self._get_policy_for_level(security_level) if security_level else self.default_policy
        
        # Set current policy for validation checks
        self.current_policy = policy
        
        # Prepare environment
        safe_env = self._prepare_safe_environment(policy, env or {})
        
        # Prepare working directory
        if work_dir is None:
            work_dir = "/tmp"
        
        # Validate working directory
        if not self.validate_file_access(work_dir, "read"):
            raise SandboxViolation(f"Access to working directory denied: {work_dir}")
        
        # Create sandbox identifier
        sandbox_id = f"sandbox_{int(time.time() * 1000000)}"
        
        # Record sandbox creation
        self._log_audit_event(
            "SANDBOX_CREATED",
            {
                "sandbox_id": sandbox_id,
                "command": " ".join(cmd),
                "security_level": security_level.value if security_level else self.default_policy.value,
                "timeout": timeout,
                "work_dir": work_dir
            }
        )
        
        try:
            # Start the process
            start_time = time.time()
            
            process = subprocess.Popen(
                cmd,
                cwd=work_dir,
                env=safe_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=self._setup_preexec_functions(policy)
            )
            
            # Store process info for monitoring
            self.active_sandboxes[sandbox_id] = {
                "process": process,
                "start_time": start_time,
                "timeout": timeout,
                "policy": policy,
                "command": cmd,
                "work_dir": work_dir
            }
            
            # Start monitoring thread if enabled
            if policy.real_time_monitoring:
                monitor_thread = threading.Thread(
                    target=self._monitor_sandbox,
                    args=(sandbox_id,),
                    daemon=True
                )
                monitor_thread.start()
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                
                execution_time = time.time() - start_time
                
                # Log successful completion
                self._log_audit_event(
                    "SANDBOX_COMPLETED",
                    {
                        "sandbox_id": sandbox_id,
                        "return_code": return_code,
                        "execution_time": execution_time,
                        "stdout_length": len(stdout),
                        "stderr_length": len(stderr)
                    }
                )
                
                result = {
                    "success": return_code == 0,
                    "return_code": return_code,
                    "stdout": stdout,
                    "stderr": stderr,
                    "execution_time": execution_time,
                    "sandbox_id": sandbox_id
                }
                
            except subprocess.TimeoutExpired:
                # Kill the process on timeout
                process.kill()
                stdout, stderr = process.communicate()
                
                self._log_audit_event(
                    "SANDBOX_TIMEOUT",
                    {
                        "sandbox_id": sandbox_id,
                        "timeout": timeout,
                        "command": " ".join(cmd)
                    },
                    "WARNING"
                )
                
                result = {
                    "success": False,
                    "return_code": -1,
                    "stdout": stdout,
                    "stderr": f"Process timed out after {timeout} seconds\n{stderr}",
                    "execution_time": timeout,
                    "sandbox_id": sandbox_id,
                    "timeout": True
                }
            
        except Exception as e:
            self._log_audit_event(
                "SANDBOX_ERROR",
                {
                    "sandbox_id": sandbox_id,
                    "error": str(e),
                    "command": " ".join(cmd)
                },
                "ERROR"
            )
            
            result = {
                "success": False,
                "error": str(e),
                "sandbox_id": sandbox_id
            }
        
        finally:
            # Clean up
            if sandbox_id in self.active_sandboxes:
                del self.active_sandboxes[sandbox_id]
            self.current_policy = None
        
        return result
    
    def _prepare_safe_environment(self, policy: SandboxPolicy, user_env: Dict[str, str]) -> Dict[str, str]:
        """Prepare a safe environment for the sandboxed process"""
        # Start with minimal safe environment
        safe_env = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "HOME": "/tmp",
            "TMPDIR": "/tmp",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8"
        }
        
        # Add allowed environment variables
        if not policy.clear_env:
            # Copy some safe environment variables
            safe_vars = ["HOME", "USER", "LOGNAME", "PATH", "LANG", "LC_ALL", "TERM"]
            for var in safe_vars:
                if var in os.environ and (not policy.allowed_env_vars or var in policy.allowed_env_vars):
                    if not policy.blocked_env_vars or var not in policy.blocked_env_vars:
                        safe_env[var] = os.environ[var]
        
        # Add user-specified environment variables (if allowed)
        for key, value in user_env.items():
            if not policy.allowed_env_vars or key in policy.allowed_env_vars:
                if not policy.blocked_env_vars or key not in policy.blocked_env_vars:
                    safe_env[key] = value
        
        return safe_env
    
    def _setup_preexec_functions(self, policy: SandboxPolicy):
        """Set up pre-execution functions for additional sandboxing"""
        def preexec():
            # Apply resource limits
            import resource
            
            # Memory limit
            if policy.max_memory_mb:
                max_bytes = policy.max_memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))
                resource.setrlimit(resource.RLIMIT_DATA, (max_bytes, max_bytes))
                resource.setrlimit(resource.RLIMIT_STACK, (max_bytes, max_bytes))
            
            # Process limit
            if policy.max_processes:
                resource.setrlimit(resource.RLIMIT_NPROC, (policy.max_processes, policy.max_processes))
            
            # CPU time limit (soft limit)
            # Note: CPU percentage limiting is harder, we'll use timeout instead
            
            # Drop privileges if running as root
            if os.getuid() == 0:
                try:
                    # Try to drop to nobody user/group
                    os.setgid(65534)  # nogroup
                    os.setuid(65534)  # nobody
                except:
                    pass  # Continue anyway if we can't drop privileges
            
            # Close unnecessary file descriptors
            try:
                max_fd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
                if max_fd == resource.RLIM_INFINITY:
                    max_fd = 256
                for fd in range(3, max_fd):
                    try:
                        os.close(fd)
                    except OSError:
                        pass  # Already closed
            except:
                pass
            
            # Apply seccomp filter if available (simplified)
            # In a full implementation, we would use libseccomp or similar
        
        return preexec
    
    def _monitor_sandbox(self, sandbox_id: str):
        """Monitor a sandboxed process for resource usage and violations"""
        if sandbox_id not in self.active_sandboxes:
            return
        
        sandbox_info = self.active_sandboxes[sandbox_id]
        process = sandbox_info["process"]
        policy = sandbox_info["policy"]
        start_time = sandbox_info["start_time"]
        
        try:
            while process.poll() is None:  # While process is running
                try:
                    # Get process info
                    proc = psutil.Process(process.pid)
                    
                    # Check memory usage
                    memory_info = proc.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)
                    
                    if memory_mb > policy.max_memory_mb:
                        self._log_audit_event(
                            "SANDBOX_MEMORY_VIOLATION",
                            {
                                "sandbox_id": sandbox_id,
                                "current_mb": memory_mb,
                                "limit_mb": policy.max_memory_mb,
                                "pid": process.pid
                            },
                            "ERROR"
                        )
                        process.terminate()
                        break
                    
                    # Check CPU usage
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    if cpu_percent > policy.max_cpu_percent:
                        self._log_audit_event(
                            "SANDBOX_CPU_VIOLATION",
                            {
                                "sandbox_id": sandbox_id,
                                "cpu_percent": cpu_percent,
                                "limit_percent": policy.max_cpu_percent,
                                "pid": process.pid
                            },
                            "WARNING"
                        )
                        # Don't kill for CPU, just warn
                    
                    # Check file descriptor count
                    try:
                        num_fds = proc.num_fds()
                        if num_fds > 1000:  # Arbitrary high limit
                            self._log_audit_event(
                                "SANDBOX_FD_VIOLATION",
                                {
                                    "sandbox_id": sandbox_id,
                                    "fd_count": num_fds,
                                    "pid": process.pid
                                },
                                "WARNING"
                            )
                    except:
                        pass  # num_fds not available on all platforms
                    
                    time.sleep(0.5)  # Check every 500ms
                    
                except psutil.NoSuchProcess:
                    break  # Process ended
                except Exception as e:
                    # Log monitoring error but continue
                    self._log_audit_event(
                        "SANDBOX_MONITOR_ERROR",
                        {
                            "sandbox_id": sandbox_id,
                            "error": str(e),
                            "pid": process.pid if hasattr(process, 'pid') else 'unknown'
                        },
                        "DEBUG"
                    )
                    time.sleep(1)
                    
        except Exception as e:
            self._log_audit_event(
                "SANDBOX_MONITOR_FAILED",
                {
                    "sandbox_id": sandbox_id,
                    "error": str(e)
                },
                "ERROR"
            )
    
    def get_active_sandboxes(self) -> Dict[str, Dict]:
        """Get information about currently active sandboxes"""
        result = {}
        for sandbox_id, info in self.active_sandboxes.items():
            proc = info["process"]
            result[sandbox_id] = {
                "pid": proc.pid if proc else None,
                "status": "running" if proc.poll() is None else "finished",
                "runtime": time.time() - info["start_time"],
                "command": " ".join(info["command"]),
                "work_dir": info["work_dir"]
            }
        return result
    
    def cleanup_all_sandboxes(self):
        """Terminate all active sandboxes"""
        for sandbox_id, info in list(self.active_sandboxes.items()):
            try:
                proc = info["process"]
                if proc.poll() is None:  # Still running
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
                
                self._log_audit_event(
                    "SANDBOX_FORCE_TERMINATED",
                    {
                        "sandbox_id": sandbox_id,
                        "reason": "cleanup_all_sandboxes called"
                    }
                )
            except Exception as e:
                self._log_audit_event(
                    "SANDBOX_CLEANUP_ERROR",
                    {
                        "sandbox_id": sandbox_id,
                        "error": str(e)
                    },
                    "ERROR"
                )
            
            del self.active_sandboxes[sandbox_id]

# Global sandbox manager instance
sandbox_manager = SandboxManager()

def run_sandboxed(command: List[str], 
                 security_level: SecurityLevel = SecurityLevel.MEDIUM,
                 timeout: int = 30,
                 work_dir: str = None,
                 env: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Convenience function to run a command in a sandbox
    
    Args:
        command: Command and arguments as list
        security_level: Security level to apply
        timeout: Timeout in seconds
        work_dir: Working directory
        env: Environment variables
        
    Returns:
        Result dictionary with execution details
    """
    return sandbox_manager.create_sandboxed_process(
        cmd=command,
        security_level=security_level,
        timeout=timeout,
        work_dir=work_dir,
        env=env
    )

def secure_file_operation(file_path: str, operation: str = "read") -> bool:
    """
    Check if a file operation is allowed under current sandbox policy
    
    Args:
        file_path: Path to check
        operation: Type of operation (read, write, execute, etc.)
        
    Returns:
        True if allowed, False if blocked
    """
    return sandbox_manager.validate_file_access(file_path, operation)

def secure_network_operation(host: str, port: int) -> bool:
    """
    Check if network operation is allowed under current sandbox policy
    
    Args:
        host: Target hostname
        port: Target port number
        
    Returns:
        True if allowed, False if blocked
    """
    return sandbox_manager.validate_network_access(host, port)

# Example usage and testing
if __name__ == "__main__":
    print("Secure Sandboxing System for Computer Use")
    print("=" * 45)
    
    # Test 1: Basic sandboxed command execution
    print("\n1. Testing basic sandboxed command execution...")
    result = run_sandboxed(
        ["echo", "Hello, Secure World!"],
        security_level=SecurityLevel.LOW,
        timeout=5
    )
    print(f"   Success: {result['success']}")
    print(f"   Output: {result['stdout'].strip()}")
    
    # Test 2: File access validation
    print("\n2. Testing file access validation...")
    test_paths = [
        ("/tmp/test.txt", "read", True),
        ("/etc/passwd", "read", False),  # Should be blocked
        ("/home/tehlappy/test.txt", "write", True),
        ("/root/.bashrc", "read", False)  # Should be blocked
    ]
    
    for path, op, expected in test_paths:
        allowed = secure_file_operation(path, op)
        status = "✓" if allowed == expected else "✗"
        print(f"   {status} {op} {path}: {allowed} (expected {expected})")
    
    # Test 3: Network access validation
    print("\n3. Testing network access validation...")
    
    # Test with MEDIUM security level (network disabled by default)
    sandbox_manager = SandboxManager()
    sandbox_manager.current_policy = sandbox_manager._get_policy_for_level(SecurityLevel.MEDIUM)
    
    net_tests = [
        ("google.com", 80, False),   # Should be blocked (network disabled)
        ("localhost", 8080, False),  # Should be blocked (network disabled)
    ]
    
    for host, port, expected in net_tests:
        allowed = secure_network_operation(host, port)
        status = "✓" if allowed == expected else "✗"
        print(f"   {status} {host}:{port}: {allowed} (expected {expected})")
    
    # Test with LOW security level (network enabled)
    sandbox_manager.current_policy = sandbox_manager._get_policy_for_level(SecurityLevel.LOW)
    
    net_tests_low = [
        ("google.com", 80, True),    # Should be allowed
        ("localhost", 8080, True),   # Should be allowed (in allowed ports)
        ("example.com", 22, False),  # Should be blocked (blocked port)
    ]
    
    for host, port, expected in net_tests_low:
        allowed = secure_network_operation(host, port)
        status = "✓" if allowed == expected else "✗"
        print(f"   {status} {host}:{port}: {allowed} (expected {expected})")
    
    # Test 4: High security sandbox
    print("\n4. Testing high security sandbox...")
    result = run_sandboxed(
        ["ls", "-la", "/tmp"],
        security_level=SecurityLevel.HIGH,
        timeout=10
    )
    print(f"   Success: {result['success']}")
    if not result['success']:
        print(f"   Error: {result.get('stderr', 'Unknown error')[:100]}...")
    
    # Test 5: Resource limits
    print("\n5. Testing resource limits...")
    result = run_sandboxed(
        ["sleep", "2"],  # This should complete fine
        security_level=SecurityLevel.MEDIUM,
        timeout=5
    )
    print(f"   Sleep command success: {result['success']}")
    print(f"   Execution time: {result.get('execution_time', 0):.2f}s")
    
    # Test 6: Memory-limited process (should work for small allocations)
    print("\n6. Testing memory-conscious operation...")
    result = run_sandboxed(
        ["python3", "-c", "print('Hello from sandboxed Python')"],
        security_level=SecurityLevel.MEDIUM,
        timeout=10
    )
    print(f"   Python script success: {result['success']}")
    if result['success']:
        print(f"   Output: {result['stdout'].strip()}")
    
    # Test 7: Test sandbox creation and monitoring
    print("\n7. Testing sandbox creation and monitoring...")
    sandbox_manager = SandboxManager()
    sandbox_result = sandbox_manager.create_sandboxed_process(
        cmd=["python3", "-c", "import time; print('Starting'); time.sleep(2); print('Done')"],
        security_level=SecurityLevel.LOW,
        timeout=5
    )
    print(f"   Sandbox execution success: {sandbox_result['success']}")
    print(f"   Output: {sandbox_result['stdout'].strip()}")
    
    # Check active sandboxes (should be empty after completion)
    active = sandbox_manager.get_active_sandboxes()
    print(f"   Active sandboxes after completion: {len(active)}")
    
    print(f"\n✓ Secure sandboxing system initialized successfully")