import os
import subprocess
import logging

logger = logging.getLogger(__name__)

# Absolute path of the project root to constrain operations
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _is_safe_path(filepath: str) -> bool:
    """Ensure the target path is within the project directory."""
    try:
        abs_path = os.path.abspath(os.path.join(PROJECT_ROOT, filepath))
        return abs_path.startswith(PROJECT_ROOT)
    except Exception:
        return False


def read_file(filepath: str) -> str:
    """Reads the content of a file."""
    if not _is_safe_path(filepath):
        return f"Error: Inaccessible path. Security policy restricts reading only to files within the project ({PROJECT_ROOT})."

    target_path = os.path.join(PROJECT_ROOT, filepath)
    if not os.path.exists(target_path):
        return f"Error: File not found -> {filepath}"

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"--- Content of {filepath} ---\n{content}"
    except Exception as e:
        return f"Error reading file {filepath}: {str(e)}"


def write_file(filepath: str, content: str) -> str:
    """Writes or overwrites a file with new content."""
    if not _is_safe_path(filepath):
        return f"Error: Inaccessible path. Security policy restricts writing only to files within the project ({PROJECT_ROOT})."

    target_path = os.path.join(PROJECT_ROOT, filepath)

    # Ensure directory exists
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    try:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: File '{filepath}' has been created/modified."
    except Exception as e:
        return f"Error writing file {filepath}: {str(e)}"


def execute_bash(command: str) -> str:
    """Executes a terminal command safely within the project root."""
    forbidden_tokens = ["rm -rf", "format", "shutdown", "reboot"]
    for token in forbidden_tokens:
        if token in command.lower():
            return f"Error: Command '{token}' restricted by security filters (Blocked)."

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=15,  # Max 15 seconds to prevent hanging
        )

        output = result.stdout + result.stderr

        if result.returncode == 0:
            return f"Command Successful (Code 0):\n{output.strip() or 'No output.'}"
        else:
            return f"Command Error (Code {result.returncode}):\n{output.strip()}"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out (15 second limit)."
    except Exception as e:
        return f"Error executing command: {str(e)}"


# The schema definition required by OpenAI Tools API
DEV_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the content of a file in the project directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Relative path of the file to read from the project root (e.g., app/main.py, config.py)",
                    }
                },
                "required": ["filepath"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes content to a file in the project directory (overwrites if exists, creates if not).",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Relative path of the file to write from the project root (e.g., app/views/new_page.py)",
                    },
                    "content": {
                        "type": "string",
                        "description": "FULL CODE or content to write to the file. Should not be partial, must cover the entire file.",
                    },
                },
                "required": ["filepath", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_bash",
            "description": "Executes a secure command in the terminal. (e.g., dir, pip install packageName)",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Terminal command to execute.",
                    }
                },
                "required": ["command"],
            },
        },
    },
]
