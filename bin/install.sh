#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
# Treat unset variables as an error
# Exit if any command in a pipeline fails
set -euo pipefail

# Set _dir to directory of the script being run
_dir="$(cd "$(dirname "$0")" && pwd)"
_topdir="$(cd "${_dir}/.." && pwd)"

# Color definitions
if command -v tput >/dev/null 2>&1 && [[ -n "${TERM:-}" ]] && [[ "${TERM:-}" != "dumb" ]]; then
    BOLD=$(tput bold)
    GREEN=$(tput setaf 2)
    YELLOW=$(tput setaf 3)
    RED=$(tput setaf 1)
    BLUE=$(tput setaf 4)
    NO_COLOR=$(tput sgr0)
else
    BOLD='\033[1m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NO_COLOR='\033[0m'
fi

# Usage function
usage() {
    echo "Python Project Factory - Create a new Python project from template"
    echo ""
    echo "Usage: curl -sSL https://raw.githubusercontent.com/ksylvan/python-project-template/main/bin/install.sh | bash"
    echo ""
    echo "Options:"
    echo "  --help    Show this help message and exit"
    echo ""
    echo "This script will:"
    echo "  1. Ask for project details (name, author, description)"
    echo "  2. Clone the Python project template"
    echo "  3. Customize the template with your project details"
    echo "  4. Set up the development environment"
    echo ""
    echo "Requirements: git, curl, sed, grep"
}

# Function to print error messages and exit
error() {
    echo -e "${RED}ERROR: $1${NO_COLOR}" >&2
    exit 1
}

# Function to print informational messages
info() {
    echo -e "${BLUE}$1${NO_COLOR}"
}

# Function to print success messages
success() {
    echo -e "${GREEN}$1${NO_COLOR}"
}

# Function to print warning messages
warning() {
    echo -e "${YELLOW}$1${NO_COLOR}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to clean up on error
cleanup() {
    if [ -n "${PROJECT_NAME:-}" ] && [ -d "$PROJECT_NAME" ]; then
        warning "Cleaning up failed installation..."
        rm -rf "$PROJECT_NAME"
    fi
    error "Installation failed. Please check the error message above."
}

# Set up error trap
trap cleanup ERR

# Parse command-line arguments
for arg in "$@"; do
    case $arg in
        --help)
            usage
            exit 0
            ;;
        *)
            warning "Unknown argument: $arg"
            usage
            exit 1
            ;;
    esac
done

# Check for required dependencies
for cmd in git curl sed grep; do
    if ! command_exists "$cmd"; then
        error "$cmd is required but not installed. Please install it and try again."
    fi
done

# If the script is being piped from curl, offer to display its contents
if [ -t 0 ]; then
    # Terminal is interactive, we're not being piped
    :
else
    # We might be being piped from curl
    if [ -t 1 ]; then
        # Stdout is a terminal, we can ask
        echo ""
        echo -n "Would you like to review this script before executing it? [y/N] "
        read -r review_script
        if [[ "$review_script" =~ ^[Yy]$ ]]; then
            # Get the script content
            SCRIPT_CONTENT=$(cat "$0" 2>/dev/null || curl -sSL "https://raw.githubusercontent.com/ksylvan/python-project-template/main/bin/install.sh" 2>/dev/null || echo "Could not retrieve script content")
            echo ""
            echo "=== SCRIPT CONTENT BEGIN ==="
            echo "$SCRIPT_CONTENT"
            echo "=== SCRIPT CONTENT END ==="
            echo ""
            echo -n "Continue with execution? [y/N] "
            read -r continue_execution
            if [[ ! "$continue_execution" =~ ^[Yy]$ ]]; then
                exit 0
            fi
        fi
    fi
fi

echo -e "\n${BOLD}${BLUE}Python Project Factory${NO_COLOR}"
echo -e "${BLUE}=============================${NO_COLOR}\n"

# Function to validate project name
validate_project_name() {
    local project_name="$1"
    # Check if the project name is valid (starts with a letter or underscore, followed by letters, numbers, or underscores)
    if [[ ! "$project_name" =~ ^[a-zA-Z_][a-zA-Z0-9_]+$ ]]; then
        echo "0"
        return
    fi
    # Check if project name is a Python keyword
    local python_keywords=("False" "None" "True" "and" "as" "assert" "async" "await" "break" "class" "continue" "def" "del" "elif" "else" "except" "finally" "for" "from" "global" "if" "import" "in" "is" "lambda" "nonlocal" "not" "or" "pass" "raise" "return" "try" "while" "with" "yield")
    for keyword in "${python_keywords[@]}"; do
        if [ "$project_name" = "$keyword" ]; then
            echo "0"
            return
        fi
    done
    echo "1"
}

# Function to validate email
validate_email() {
    local email="$1"
    if [[ ! "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        echo "0"
        return
    fi
    echo "1"
}

# Function to validate GitHub username
validate_github_username() {
    local username="$1"
    
    # Check if username is empty
    if [ -z "$username" ]; then
        echo "1"  # Empty is allowed (will use default)
        return
    fi
    
    # Check length (1-39 characters)
    if [ ${#username} -gt 39 ]; then
        echo "0"
        return
    fi
    
    # Check if it contains only alphanumeric characters and single hyphens
    # Cannot start or end with hyphen
    # Cannot have consecutive hyphens
    if [[ ! "$username" =~ ^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$ ]] && [[ ! "$username" =~ ^[a-zA-Z0-9]+$ ]]; then
        echo "0"
        return
    fi
    
    echo "1"
}

# Get project information
info "Let's set up your new Python project!"
echo ""

# Get and validate project name
while true; do
    echo -n "Project name (lowercase with underscores, e.g. my_project): "
    read -r PROJECT_NAME
    
    # Check if project name is empty
    if [ -z "$PROJECT_NAME" ]; then
        warning "Project name cannot be empty."
        continue
    fi
    
    # Validate project name
    if [ "$(validate_project_name "$PROJECT_NAME")" = "0" ]; then
        warning "Invalid project name. It must start with a letter or underscore and contain only letters, numbers, or underscores."
        continue
    fi
    
    # Check if directory already exists
    if [ -d "$PROJECT_NAME" ]; then
        warning "Directory '$PROJECT_NAME' already exists. Please choose a different name."
        continue
    fi
    
    break
done

# Get and validate author name
while true; do
    echo -n "Author name: "
    read -r AUTHOR_NAME
    
    # Check if author name is empty
    if [ -z "$AUTHOR_NAME" ]; then
        warning "Author name cannot be empty."
        continue
    fi
    
    break
done

# Get and validate author email
while true; do
    echo -n "Author email: "
    read -r AUTHOR_EMAIL
    
    # Validate email
    if [ "$(validate_email "$AUTHOR_EMAIL")" = "0" ]; then
        warning "Invalid email address."
        continue
    fi
    
    break
done

# Get and validate GitHub username
while true; do
    echo -n "GitHub username (for repository URLs): "
    read -r GITHUB_USERNAME
    
    # If GitHub username is empty, use a default
    if [ -z "$GITHUB_USERNAME" ]; then
        GITHUB_USERNAME="yourname"
        break
    fi
    
    # Validate GitHub username
    if [ "$(validate_github_username "$GITHUB_USERNAME")" = "0" ]; then
        warning "Invalid GitHub username. It must:"
        warning "  - Be 1-39 characters long"
        warning "  - Contain only alphanumeric characters and hyphens"
        warning "  - Not begin or end with a hyphen"
        warning "  - Not contain consecutive hyphens"
        continue
    fi
    
    break
done

# Get project description
echo -n "Project description: "
read -r PROJECT_DESC

# If description is empty, use a default
if [ -z "$PROJECT_DESC" ]; then
    PROJECT_DESC="A Python project created with python-project-template"
fi

# Get current year
CURRENT_YEAR=$(date +%Y)

# Confirmation
echo ""
echo -e "${BOLD}Project details:${NO_COLOR}"
echo "  Project name: $PROJECT_NAME"
echo "  Author name: $AUTHOR_NAME"
echo "  Author email: $AUTHOR_EMAIL"
echo "  GitHub username: $GITHUB_USERNAME"
echo "  Description: $PROJECT_DESC"
echo "  Year: $CURRENT_YEAR"
echo ""
echo -n "Proceed with these settings? [Y/n] "
read -r proceed

if [[ "$proceed" =~ ^[Nn]$ ]]; then
    info "Installation cancelled by user."
    exit 0
fi

# Clone the template repository
info "Cloning template repository..."
git clone https://github.com/ksylvan/python-project-template.git "$PROJECT_NAME"

# Change into the project directory
cd "$PROJECT_NAME"

# Remove the .git directory
info "Removing existing Git history..."
rm -rf .git

# Function to safely replace text in files
replace_in_files() {
    local search="$1"
    local replace="$2"
    local file_pattern="${3:-.}"
    
    # Use find with -type f to only get files (not directories)
    # Then use grep -l to only list files that match
    # Then use xargs sed to perform the replacement
    find . -type f -not -path "*/\.*" -not -path "*/\.*/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/venv/*" -not -path "*/.venv/*" | xargs grep -l "$search" 2>/dev/null | while read -r file; do
        sed -i.bak "s|$search|$replace|g" "$file"
        rm "${file}.bak"
    done
}

# Replace placeholders in all files
info "Customizing project files..."

# Replace project name
replace_in_files "python-project-template" "$PROJECT_NAME"

# Replace author name
replace_in_files "Your Name" "$AUTHOR_NAME"

# Replace author email
replace_in_files "Your@Email.com" "$AUTHOR_EMAIL"

# Replace project description
replace_in_files "Add your description here" "$PROJECT_DESC"

# Replace general description in __init__.py
replace_in_files "Your general description here" "$PROJECT_DESC"

# Replace year
replace_in_files "2025" "$CURRENT_YEAR"

# Replace GitHub username in URLs
replace_in_files "yourname" "$GITHUB_USERNAME"

# Replace in specific files that might be missed by the generic replacement
# pyproject.toml
if [ -f "pyproject.toml" ]; then
    sed -i.bak "s|python_project_template|${PROJECT_NAME}|g" "pyproject.toml"
    rm "pyproject.toml.bak"
fi

# README.md
if [ -f "README.md" ]; then
    sed -i.bak "s|Python Project Template|${PROJECT_NAME}|g" "README.md"
    rm "README.md.bak"
    sed -i.bak "s|python_project_template|${PROJECT_NAME}|g" "README.md"
    rm "README.md.bak"
fi

# Rename the package directory
if [ -d "python_project_template" ]; then
    info "Renaming package directory..."
    mv "python_project_template" "$PROJECT_NAME"
    
    # Update the path in pyproject.toml (specific to hatch version)
    if [ -f "pyproject.toml" ]; then
        sed -i.bak "s|python_project_template/__about__.py|${PROJECT_NAME}/__about__.py|g" "pyproject.toml"
        rm "pyproject.toml.bak"
    fi
    
    # Update imports in Python files if needed
    find . -name "*.py" -type f | xargs grep -l "python_project_template" 2>/dev/null | while read -r file; do
        sed -i.bak "s|python_project_template|${PROJECT_NAME}|g" "$file"
        rm "${file}.bak"
    done
    
    # Enhance the module docstring in __init__.py
    if [ -f "$PROJECT_NAME/__init__.py" ]; then
        MODULE_DOCSTRING="\"${PROJECT_DESC}\n\nA Python package for ${PROJECT_NAME}.\"\n"
        sed -i.bak "1s|\".*\"|${MODULE_DOCSTRING}|" "$PROJECT_NAME/__init__.py" 
        rm "$PROJECT_NAME/__init__.py.bak"
    fi
fi

# Initialize new git repository
info "Initializing new Git repository..."
git init

# Ask if user wants to make an initial commit
echo -n "Would you like to create an initial Git commit? [Y/n] "
read -r make_commit

if [[ ! "$make_commit" =~ ^[Nn]$ ]]; then
    git add .
    git commit -m "Initial project scaffold"
    success "Created initial Git commit."
fi

# Ensure execute permissions on scripts
if [ -f "bin/setup.sh" ]; then
    chmod +x "bin/setup.sh"
fi

# Run setup.sh to set up development environment
echo ""
echo -n "Would you like to set up the development environment now? [Y/n] "
read -r setup_env

if [[ ! "$setup_env" =~ ^[Nn]$ ]]; then
    info "Setting up development environment..."
    if [ -f "bin/setup.sh" ]; then
        # shellcheck disable=SC1091
        (cd bin && ./setup.sh)
    else
        warning "setup.sh not found. Skipping environment setup."
    fi
fi

# Print success message
echo ""
success "🎉 Your new Python project '$PROJECT_NAME' has been created successfully! 🎉"
echo ""
echo "Next steps:"
echo "  1. cd $PROJECT_NAME"
echo "  2. Activate your virtual environment: source .venv/bin/activate"
echo "  3. Start coding!"
echo ""
info "Happy coding! 🐍"

