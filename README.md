# Python Project Template

**A template for creating new Python projects.**

This project provides a basic structure and starting point for new Python projects. It includes common configurations and tools to help you get started quickly.

Imagine seamlessly starting your new Python project with a well-organized structure and pre-configured tools!

## Table of Contents

- [Python Project Template](#python-project-template)
  - [Table of Contents](#table-of-contents)
  - [What is this?](#what-is-this)
  - [Key Goals \& Features](#key-goals--features)
  - [How it Works](#how-it-works)
    - [Quick Start with the Project Factory](#quick-start-with-the-project-factory)
    - [Manual Setup](#manual-setup)
  - [Project Status](#project-status)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
      - [From Source (for Development)](#from-source-for-development)
      - [From PyPI (for Users)](#from-pypi-for-users)
  - [Contributing](#contributing)
  - [License](#license)

## What is this?

- **Python Project Template:** A starting point for new Python projects.
- **MCP:** An open standard protocol enabling AI applications (like IDEs) to securely interact with external tools and data sources. This template can be used to create projects that may or may not interact with MCP.

## Key Goals & Features

- **Quick Start:** Get your Python project up and running quickly with a pre-defined structure and an easy-to-use project factory script.
- **Best Practices:** Includes common configurations and tools following Python best practices.
- **Customizable:** Easily adapt the template to your specific project needs.
- **Standardization:** Adhere to common Python project standards.
- **Modern Tooling:** Uses [uv](https://github.com/astral-sh/uv) for dependency management and virtual environments.

## How it Works

### Quick Start with the Project Factory

The easiest way to start a new project is to use our Project Factory script:

```bash
curl -sSL https://raw.githubusercontent.com/ksylvan/python-project-template/main/bin/install.sh | bash
```

This interactive script will:

1. Ask for your project details:
   - Project name (must be a valid Python package name)
   - Author name
   - Author email
   - Project description
2. Clone this template and customize it with your details
3. Set up a new Git repository
4. Optionally create an initial commit
5. Set up the development environment with all dependencies

**Prerequisites for using the Project Factory:**

- Git
- curl
- sed and grep (standard on most Unix-like systems)

### Manual Setup

If you prefer to set up manually, you can:

1. **Clone or Use Template:** Start your new project by cloning this repository or using it as a template on GitHub.
2. **Customize:** Modify the project name, description, and other details in `pyproject.toml` and other configuration files.
3. **Develop:** Add your project-specific code and logic.
4. **Test:** Write and run tests for your code.
5. **Build and Distribute:** Build your project and distribute it as needed.

## Project Status

This project is currently in the **design** phase.

The core architecture and proposed tools are outlined in the [High-Level Design Document][design_doc].

The current task list is in the [tasks directory][tasks_directory] and is managed by the excellent [Task Master][taskmaster] tool.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python >= 3.11
- [uv](https://github.com/astral-sh/uv) (Python package and environment manager)

### Installation

#### From Source (for Development)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourname/python-project-template.git
   cd python-project-template
   ```

2. **Install dependencies using uv sync:**

   ```bash
   uv sync --dev
   ```

   This command ensures your virtual environment matches the dependencies in `pyproject.toml` and `uv.lock`, creating the environment on the first run if necessary.

3. **Activate the virtual environment (uv will create it if needed):**

   - On macOS/Linux:

     ```bash
     source .venv/bin/activate
     ```

   - On Windows:

     ```bash
     .venv\\Scripts\\activate
     ```

Now you have the development environment set up!

#### From PyPI (for Users)

If you just want to use the `python-project-template` as a base (though it's more of a template than a library to install directly for typical use), you might fork it or use it as a GitHub template.

If this project were to be published as an installable package (e.g., if it provided some core library functions), the instructions would be:

```bash
# Using pip
pip install python-project-template

# Or using uv
uv pip install python-project-template
```

This will install the package and its dependencies.

## Contributing

Feedback on the template is highly welcome! Please open an issue to share your thoughts or suggestions.

Read the [contribution document here](./docs/contributing.md) and please follow the guidelines for this repository.

## License

Copyright (c) 2025, [Your Name](Your@Email.com) Licensed under the [MIT License](./LICENSE).

[taskmaster]: https://github.com/eyaltoledano/claude-task-master
[tasks_directory]: ./tasks
[design_doc]: ./docs/design.md
