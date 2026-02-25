import os
import glob
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Fallback wrapper for psutil in environments where it might not be installed yet
try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def get_system_vitals() -> Dict[str, Any]:
    """Retrieves real-time OS metrics to give the LLM awareness of its physical environment."""
    if not HAS_PSUTIL:
        return {
            "error": "The psutil library is not installed. Run 'pip install psutil' in the terminal to install."
        }

    try:
        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "status": "success",
            "os_metrics": {
                "cpu_percent": cpu_usage,
                "ram_total_gb": round(ram.total / (1024**3), 2),
                "ram_used_gb": round(ram.used / (1024**3), 2),
                "ram_percent": ram.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "disk_percent": disk.percent,
            },
        }
    except Exception as e:
        logger.error(f"Error reading OS vitals: {e}")
        return {"error": str(e)}


def scan_directory(directory_path: str, file_extension: str = "*") -> Dict[str, Any]:
    """Allows the agent to scan given absolute paths to locate foreign files (e.g., in Downloads)."""
    if not os.path.exists(directory_path):
        return {"error": f"Directory not found: {directory_path}"}

    if not os.path.isdir(directory_path):
        return {"error": f"The provided path is not a directory: {directory_path}"}

    try:
        search_pattern = os.path.join(
            directory_path, f"*.{file_extension}" if file_extension != "*" else "*"
        )
        files = glob.glob(search_pattern)

        # Prevent oversized payloads by limiting results
        max_files = 50
        result_files = files[:max_files]

        details = []
        for f in result_files:
            if os.path.isfile(f):
                stat = os.stat(f)
                details.append(
                    {
                        "name": os.path.basename(f),
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    }
                )

        return {
            "status": "success",
            "directory": directory_path,
            "total_found": len(files),
            "files_shown": len(details),
            "files": details,
        }
    except Exception as e:
        return {"error": str(e)}


OS_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_system_vitals",
            "description": "Returns real-time operating system (OS) metrics such as CPU, RAM, and Disk usage.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scan_directory",
            "description": "Scans files inside any directory on the local computer and lists them with their sizes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "ABSOLUTE directory path to scan. (e.g., C:/Users/User/Downloads OR /home/user/Documents)",
                    },
                    "file_extension": {
                        "type": "string",
                        "description": "File extension to filter by (e.g., pdf, csv, txt). Use '*' for all files.",
                    },
                },
                "required": ["directory_path"],
            },
        },
    },
]
