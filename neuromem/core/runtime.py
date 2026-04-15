"""
NeuraMem Core Runtime Module
Handles OS detection, RAM monitoring, and path management.
"""
import os
import sys
import platform
import psutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RuntimeEnvironment:
    """Manages runtime environment detection and configuration."""
    
    def __init__(self):
        self.os_type = self._detect_os()
        self.python_version = sys.version_info
        self.machine = platform.machine()
        self.processor = platform.processor()
        
    def _detect_os(self) -> str:
        """Detect the operating system."""
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"
    
    def get_base_path(self) -> Path:
        """Get the base path for NeuraMem data storage."""
        if self.os_type == "windows":
            base = Path(os.environ.get("APPDATA", ".")) / "NeuraMem"
        else:
            base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "NeuraMem"
        
        base.mkdir(parents=True, exist_ok=True)
        return base
    
    def get_config_path(self) -> Path:
        """Get the configuration path."""
        if self.os_type == "windows":
            base = Path(os.environ.get("APPDATA", ".")) / "NeuraMem" / "config"
        else:
            base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "NeuraMem"
        
        base.mkdir(parents=True, exist_ok=True)
        return base


class RAMMonitor:
    """Monitors system RAM usage for memory management decisions."""
    
    def __init__(self, threshold_percent: float = 85.0):
        self.threshold_percent = threshold_percent
        
    def get_usage(self) -> Dict[str, Any]:
        """Get current RAM usage statistics."""
        mem = psutil.virtual_memory()
        return {
            "total_gb": mem.total / (1024 ** 3),
            "available_gb": mem.available / (1024 ** 3),
            "used_gb": mem.used / (1024 ** 3),
            "percent": mem.percent,
            "is_critical": mem.percent > self.threshold_percent
        }
    
    def is_memory_available(self, required_gb: float = 1.0) -> bool:
        """Check if sufficient memory is available."""
        usage = self.get_usage()
        available_gb = usage["available_gb"]
        return available_gb >= required_gb and not usage["is_critical"]
    
    def wait_for_memory(self, timeout_seconds: int = 60) -> bool:
        """Wait until memory is available or timeout."""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if self.is_memory_available():
                return True
            time.sleep(1)
        
        return False


# Global runtime instance
_runtime_env: Optional[RuntimeEnvironment] = None
_ram_monitor: Optional[RAMMonitor] = None


def get_runtime() -> RuntimeEnvironment:
    """Get the global runtime environment instance."""
    global _runtime_env
    if _runtime_env is None:
        _runtime_env = RuntimeEnvironment()
    return _runtime_env


def get_ram_monitor() -> RAMMonitor:
    """Get the global RAM monitor instance."""
    global _ram_monitor
    if _ram_monitor is None:
        _ram_monitor = RAMMonitor()
    return _ram_monitor


if __name__ == "__main__":
    runtime = get_runtime()
    print(f"OS: {runtime.os_type}")
    print(f"Python: {runtime.python_version.major}.{runtime.python_version.minor}")
    print(f"Base Path: {runtime.get_base_path()}")
    
    ram = get_ram_monitor()
    usage = ram.get_usage()
    print(f"RAM Usage: {usage['percent']:.1f}%")
    print(f"Available: {usage['available_gb']:.2f} GB")
