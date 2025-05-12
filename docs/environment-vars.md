# Environment Variables in PyHatchery

PyHatchery supports using environment variables both directly and via a `.env` file for configuration and automation.

## Using Environment Variables

Environment variables can be used in two ways:

1. **System Environment Variables**: Set in your shell or system
2. **`.env` File**: Create a `.env` file in your project root

## Available Environment Variables

| Variable Name | Description | Default |
|---------------|-------------|---------|
| `AUTHOR_NAME` | Author name for new projects | Value from git config |
| `AUTHOR_EMAIL` | Author email for new projects | Value from git config |
| `GITHUB_USERNAME` | GitHub username for new projects | None |
| `PROJECT_DESCRIPTION` | Default project description | None |
| `LICENSE` | Default license (MIT, Apache-2.0, GPL-3.0) | MIT |
| `PYTHON_VERSION` | Preferred Python version (3.10, 3.11, 3.12) | 3.11 |
| `PYHATCHERY_DEBUG` | Enable debug mode (1/0, true/false) | false |

## Non-Interactive Mode

You can use environment variables with the `--no-interactive` flag for fully automated project creation:

```bash
# Set variables directly in the shell
export AUTHOR_NAME="Your Name"
export AUTHOR_EMAIL="your.email@example.com"

# Create project in non-interactive mode
pyhatchery new my-awesome-project --no-interactive
```

Alternatively, create a `.env` file and run:

```bash
pyhatchery new my-awesome-project --no-interactive
```

## CLI Arguments vs Environment Variables

When both CLI arguments and environment variables are provided, the precedence is:

1. CLI arguments (highest priority)
2. Environment variables from `.env` file or system
3. Default values (lowest priority)

## Example .env File

Below is an example `.env` file. You can copy `.env.example` as a starting point.

```bash
# Author details
AUTHOR_NAME="Your Name"
AUTHOR_EMAIL="your.email@example.com"
GITHUB_USERNAME="your_github_username"

# Project details
PROJECT_DESCRIPTION="A Python project created with PyHatchery"

# Project configuration
LICENSE="MIT"
PYTHON_VERSION="3.11"
```
