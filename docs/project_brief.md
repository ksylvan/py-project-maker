# Project Brief: PyHatchery

## Introduction / Problem Statement

PyHatchery streamlines Python development by instantly generating standardized project structures with modern tooling pre-configured, reducing setup time from hours to minutes. Developers often waste valuable time creating boilerplate project infrastructure (like directory structures, development tool configurations, and CI/CD pipelines) instead of focusing on writing unique application code. PyHatchery eliminates this friction by automating the setup of these elements, incorporating best practices, and allowing developers to immediately focus on the core logic of their new project.

## Vision & Goals

* **Vision:** PyHatchery becomes a go-to tool for senior and staff-level developers, enabling them to quickly standardize new Python projects (from small utilities to large corporate applications) on a best-practice foundation, thereby accelerating development cycles and improving code consistency.
* **Primary Goals (for the current version/MVP):**
    1. **Core Utility for Creator:** Deliver a functional version of PyHatchery capable of generating a complete, usable Python project template (based on the PyHatchery repository's own structure and best practices) for immediate use by the primary developer.
    2. **Rapid Interactive Project Scaffolding:** Enable users to generate a complete project skeleton with a single command (e.g., `pyhatchery new your_project_name`) via an interactive wizard that prompts for project name, author name, author email, GitHub username, and project description. Default values (e.g., from git config, or "MIT" for license) should be suggested where possible.
    3. **Automated Personalization:** Ensure the generated project automatically includes user-provided details (project name, author, email, GitHub username, description, license choice, Python version preference) correctly populated in all relevant files (e.g., `pyproject.toml`, `LICENSE`, `README.md`, GitHub workflow files).
    4. **Comprehensive Tooling & Structure:** The generated project must include pre-configured `uv` for dependency management, `ruff` and `pylint` for linting/formatting, `hatchling` for packaging, a standard Python project directory layout, essential files (`.gitignore`, `.pylintrc`, `.ruff.toml`), and functional GitHub Actions workflows for testing and publishing (with publishing disabled by default but easily configurable).
* **Success Metrics (Initial Ideas):**
  * **Successful Self-Use:** PyHatchery successfully generates the project structure needed for the creator's planned follow-on project, matching the defined specifications.
  * **Time-to-Project-Ready:** The time taken from running `pyhatchery new <project_name>` to having a fully functional, personalized project skeleton ready for application code is under 5 minutes.
  * **CLI Wizard Completion:** The interactive wizard successfully gathers all required inputs and provides clear feedback on the generation process (e.g., "Cloning template...", "Personalizing files...", "Project successfully hatched!").
  * **Completeness & Correctness:** The generated project contains all essential pre-configurations and personalized details accurately, requiring no immediate manual boilerplate additions for the defined MVP scope. The project is immediately "pushable" to GitHub and ready for development.

## Target Audience / Users

PyHatchery is designed for any Python developer seeking to accelerate new project initiation and adhere to modern best practices. This includes:

* **Experienced Developers (Senior, Staff, Lead):** Who want to eliminate repetitive setup tasks, enforce consistency across projects (personal or corporate), and quickly prototype ideas with a robust foundation.
* **Mid-Level Developers:** Looking to streamline their workflow and adopt standardized tooling and project structures.
* **Junior Developers & Learners:** Who can benefit from starting with a best-practice project structure, learning about modern Python tooling (`uv`, `ruff`, `pylint`), and understanding a clean, maintainable project layout from the outset.
* **Open-Source Maintainers & Contributors:** Who need to quickly set up new libraries or applications with standard configurations.

The common characteristic is a desire to reduce boilerplate setup and start coding on the actual project logic faster, with confidence in the underlying project structure and tooling.

## Key Features / Scope (High-Level Ideas for MVP)

The Minimum Viable Product (MVP) for PyHatchery will include the following key features:

1. **Interactive Project Generation Wizard:** A CLI command (`pyhatchery new <project_name>`) that guides the user through essential project setup questions (e.g., author details, GitHub username, description, license choice, Python version preference), offering sensible defaults where possible (e.g., from git config).
2. **Non-Interactive Mode:** Allow project generation with all details specified via command-line arguments (e.g., `pyhatchery new my_project --author "Jane Doe" --email "jane@example.com" --github "janedoe" --description "My project" --no-interactive`), potentially using `.env` files for sourcing default values.
3. **Custom Output Location:** Enable users to specify a different output directory for the generated project via a CLI argument (e.g., `--output /path/to/projects/`).
4. **Automated Project Scaffolding:** Creates a standardized directory structure (e.g., `<project_name>/src/<project_name_slug>/`, `tests/`, `docs/`) based on modern Python best practices.
5. **Pre-configured Modern Tooling Integration:**
    * `uv` for dependency management and virtual environments (configured in `pyproject.toml`).
    * `hatchling` for building and packaging the project (configured in `pyproject.toml`).
    * `ruff` for fast linting and formatting (with a pre-configured `ruff.toml` or `pyproject.toml` settings).
    * `pylint` for comprehensive linting (with a pre-configured `.pylintrc` or `pyproject.toml` settings).
6. **Essential File Generation & Personalization:**
    * Generates a `pyproject.toml` file with project metadata (name, version, description, authors, dependencies, tool configurations).
    * Creates a `LICENSE` file (e.g., MIT License) personalized with the author's name and current year.
    * Provides a template `README.md` for the new project, populated with the project's name and description.
    * Includes a standard Python `.gitignore` file.
    * All relevant files are personalized with user-provided or derived project name, author details, etc.
7. **Integrated GitHub Actions Workflows:** Includes ready-to-use GitHub Actions workflow files for:
    * Automated testing (e.g., on push to `main`/`develop` and on pull requests).
    * Automated publishing to TestPyPI and PyPI (e.g., on pushes to `develop` and `main` respectively), with clear instructions on how to enable this feature by setting `ENABLE_PUBLISHING` to `true` and adding `PYPI_API_TOKEN` / `TEST_PYPI_API_TOKEN` secrets.
8. **Git Repository Initialization Guidance:** Ensures the cloned template's `.git` history is removed, allowing the user to initialize a fresh Git repository for their new project with clear instructions.

## Known Technical Constraints or Preferences

* **Core Language & Platform:**
  * For PyHatchery itself: Python `>=3.11`.
  * For projects generated by PyHatchery: Python `>=3.10`.
* **Build System for PyHatchery:** `hatchling >=1.27.0`.
* **Key Libraries & Runtime Dependencies for PyHatchery:**
  * Python Standard Library (e.g., `argparse`, `pathlib`, `shutil`).
  * `jinja2` for templating files.
  * `python-dotenv` for managing environment variables for non-interactive mode.
* **Templating Approach:** Custom-built project generation logic, directly utilizing `jinja2` for file templating, and avoiding higher-level abstraction frameworks like Cookiecutter.
* **Target Tool Versions (for generated projects):** The projects generated by PyHatchery will be configured to use the latest stable versions of tools like `uv`, `ruff`, `pylint`, and `hatchling` (i.e., versions will generally not be strictly pinned in the generated `pyproject.toml`).
* **Development Dependencies (for PyHatchery itself):** `hatch`, `hatchling`, `pylint`, `pytest`, `ruff`, `uv` (as per PyHatchery's own `pyproject.toml` dev group).
* **Installation Method for PyHatchery:** `pip install pyhatchery` (distribution via PyPI).
* **License for PyHatchery:** MIT License. Generated projects default to MIT License.
* **Development Environment (for PyHatchery):** Standard Python virtual environments on common OSs (Linux, macOS, Windows).
* **Risks:**
  * Keeping the embedded project template and default tool configurations aligned with the rapidly evolving Python best practices and tool updates.
  * Ensuring robust and correct personalization of all files across various user inputs (e.g., project names with hyphens vs. underscores, different author name formats) and operating system nuances.

## Relevant Research (Optional)

The primary 'research' for PyHatchery stems from the accumulated experience of the developer in Python project setup and management, combined with an ongoing synthesis of current Python ecosystem best practices. The project's own `README.md` and the design choices for the default template (e.g., inclusion of `uv`, `ruff`, `pylint`, standardized structure, GitHub Actions) reflect this practical research and understanding of modern developer needs. No formal market validation studies have been conducted for this initial version, as the primary goal is to create a highly useful tool for the developer and the broader Python community based on established best practices.
