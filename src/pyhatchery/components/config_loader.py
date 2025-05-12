"""
Component responsible for loading configuration from various sources.
"""

import subprocess
from pathlib import Path
from typing import Dict

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
            check=False,  # Don't raise an exception for non-zero exit codes
        )
        if process_result.returncode == 0:
            return process_result.stdout.strip()
        return None
    except FileNotFoundError:  # git command not found
        return None
    except (
        OSError,
        subprocess.SubprocessError,
        subprocess.CalledProcessError,
        PermissionError,
    ):
        return None


def load_from_env(env_file_path: str = ".env") -> Dict[str, str]:
    """
    Loads variables from a .env file into a dictionary.

    Args:
        env_file_path: The path to the .env file. Defaults to ".env" in the CWD.

    Returns:
        A dictionary of environment variables loaded from the file.
        Returns an empty dictionary if the file is not found or cannot be read.
    """
    env_path = Path(env_file_path)
    if env_path.is_file():
        # load_dotenv will load them into os.environ and return True if successful
        # We want to return the dict of variables from the file itself
        # So, we use dotenv_values which returns a dict
        # Note: python-dotenv's dotenv_values directly returns the dict
        # from the .env file without modifying os.environ
        # For this to work, we need to ensure python-dotenv is installed.
        # The PRD specifies python-dotenv as a runtime dependency.

        loaded_vars = dotenv_values(dotenv_path=env_path)
        # Filter out None values to match the Dict[str, str] signature
        return {k: v for k, v in loaded_vars.items() if v is not None}
    return {}
