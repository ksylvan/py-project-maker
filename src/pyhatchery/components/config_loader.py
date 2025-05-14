"""
Component responsible for loading configuration from various sources.
"""

import os
import subprocess
from pathlib import Path

from dotenv import dotenv_values


def get_git_config_value(key: str) -> str | None:
    """
    Retrieves a configuration value from git.

    Args:
        key: The git configuration key (e.g., "user.name", "user.email").

    Returns:
        The configuration value if found, otherwise None.
    """
    try:
        process_result = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True,
            text=True,
            check=False,
        )
        if process_result.returncode == 0:
            return process_result.stdout.strip()
        return None
    except FileNotFoundError:
        return None
    except (
        OSError,
        subprocess.SubprocessError,
        subprocess.CalledProcessError,
        PermissionError,
    ):
        return None


def load_from_env(env_file_path: str = ".env") -> dict[str, str]:
    """
    Loads variables from a .env file and system environment variables into a dictionary.

    Args:
        env_file_path: The path to the .env file. Defaults to ".env" in the CWD.

    Returns:
        A dictionary of environment variables loaded from the file and system.
        Returns an empty dictionary if no variables are found.
    """
    # Start with an empty dictionary
    result: dict[str, str] = {}

    # Load from .env file if it exists
    env_path = Path(env_file_path)
    if env_path.is_file():
        loaded_vars = dotenv_values(dotenv_path=env_path)
        result.update({k: v for k, v in loaded_vars.items() if v is not None})

    # Also check system environment variables for our keys
    # These are the environment variables we care about from cli.py
    env_keys = [
        "AUTHOR_NAME",
        "AUTHOR_EMAIL",
        "GITHUB_USERNAME",
        "PROJECT_DESCRIPTION",
        "LICENSE",
        "PYTHON_VERSION",
    ]

    for key in env_keys:
        if key in os.environ and os.environ[key]:
            result[key] = os.environ[key]

    return result
