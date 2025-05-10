# PyHatchery Project Structure

This document outlines the directory and file structure for the PyHatchery project itself. The structure is designed to be clean, maintainable, and follow common Python best practices, utilizing a `src` layout and Hatch for project management.

```plaintext
pyhatchery/
├── .github/
│   └── workflows/
│       ├── tests.yml         # GitHub Actions workflow for automated testing and linting
│       └── publish.yml       # GitHub Actions workflow for publishing to PyPI
├── .vscode/                  # Optional: VSCode editor settings (e.g., settings.json for Python interpreter, linters)
│   └── settings.json
│   └── tasks.json            # Set up environment on folder open, also has Run Linters and Run Tests as tasks
├── ai/                       # Scrum agile stories live here for the Agile AI driven workflow from <https://github.com/bmadcode/BMAD-METHOD>
│   └── po-validation.md.     # Product Owner agent validation document
│   └── stories/
├── docs/                     # Project documentation
│   ├── architecture.md       # Main architecture document
│   ├── tech-stack.md         # Technology stack for PyHatchery
│   ├── project-structure.md  # This file
│   ├── coding-standards.md   # Coding standards and patterns
│   ├── testing-strategy.md   # Testing strategy for PyHatchery
│   ├── data-models.md        # Data models (e.g., context object structure)
│   ├── api-reference.md      # Details of external APIs consumed (e.g., PyPI API)
│   ├── environment-vars.md   # Environment variables relevant to PyHatchery (mostly for CI/CD)
│   ├── project_brief.md      # (User-provided) Project Brief
│   ├── prd.md                # (User-provided) Product Requirements Document
│   └── ...                   # Other Epics, specifications, or design documents
├── src/
│   └── pyhatchery/           # Main application package for PyHatchery
│       ├── __init__.py
│       ├── cli.py            # Main CLI entry point, argument parsing (CLI Handler component logic)
│       ├── components/       # Modules for distinct internal components/services
│       │   ├── __init__.py
│       │   ├── config_loader.py
│       │   ├── interactive_wizard.py
│       │   ├── name_service.py
│       │   ├── http_client.py
│       │   ├── context_builder.py
│       │   ├── template_processor.py  # Wrapper for Jinja2 templating logic
│       │   └── project_generator.py   # Handles file system operations for project creation
│       ├── templates/        # Directory containing the Jinja2 templates for the projects PyHatchery generates
│       │   └── default_project/  # Represents the default project template structure
│       │       ├── .gitignore.j2
│       │       ├── LICENSE.j2
│       │       ├── README.md.j2
│       │       ├── pyproject.toml.j2
│       │       ├── .ruff.toml.j2
│       │       ├── .pylintrc.j2
│       │       ├── src/
│       │       │   └── {{project_package_name}}/ # Jinja2 variable for package name
│       │       │       ├── __about__.py.j2
│       │       │       ├── __init__.py.j2
│       │       │       └── main.py.j2
│       │       ├── tests/
│       │       │   ├── __init__.py.j2
│       │       │   └── test_main.py.j2
│       │       └── .github/workflows/  # Templates for GitHub Actions in generated projects
│       │           ├── ci.yml.j2
│       │           └── publish.yml.j2
│       └── __main__.py       # Allows execution with `python -m pyhatchery`; typically imports and calls main function from cli.py
├── tests/                    # Automated tests for PyHatchery
│   ├── __init__.py
│   ├── conftest.py           # Shared Pytest fixtures
│   ├── unit/                 # Unit tests for individual components/modules
│   │   ├── __init__.py
│   │   ├── test_cli.py
│   │   └── test_components/
│   │       ├── test_config_loader.py
│   │       └── ...           # Other component unit tests
│   └── integration/          # Integration tests
│       ├── __init__.py
│       └── test_project_generation.py # Tests the end-to-end project generation workflow
├── .env.example              # Example environment variables for local development (if any needed by PyHatchery itself)
├── .gitignore                # Specifies intentionally untracked files that Git should ignore
├── .pylintrc                 # Configuration for Pylint for PyHatchery's codebase
├── .ruff.toml                # Configuration for Ruff for PyHatchery's codebase
├── LICENSE                   # PyHatchery's own software license (e.g., MIT License)
├── pyproject.toml            # Project definition for Hatch: metadata, dependencies, build config, scripts
└── README.md                 # Main README for PyHatchery: overview, setup, usage, contribution
```
