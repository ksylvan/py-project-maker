# PyHatchery Product Requirements Document (PRD)

## Intro

PyHatchery is a command-line interface (CLI) tool designed to streamline Python project setup. It automates the creation of standardized project structures, pre-configured with modern development tools like `uv`, `ruff`, `pylint`, and `hatchling`, along with boilerplate for GitHub Actions. The goal is to reduce the initial setup time for new Python projects from potentially hours to mere minutes, allowing developers to focus on writing unique application code immediately. This MVP aims to deliver a robust tool for the creator and the broader Python community, embodying best practices in project scaffolding.

## Goals and Context

- **Project Objectives:**
    1. Deliver a functional CLI tool capable of generating a complete, usable Python project template based on best practices.
    2. Enable rapid project scaffolding via an interactive wizard and a non-interactive command-line mode, including checks for PyPI name availability and PEP 8 naming conventions.
    3. Automate the personalization of generated project files with user-provided details.
    4. Ensure the generated project includes a comprehensive suite of pre-configured modern development tools (`uv`, `ruff`, `pylint`, `hatchling`, `pytest`) and a standard directory structure.
    5. Provide ready-to-use GitHub Actions workflows for CI/CD (testing and optional publishing).
- **Measurable Outcomes:**
    1. The tool successfully generates project structures that are immediately usable and align with defined specifications.
    2. The time taken to generate a new project skeleton is consistently under 5 minutes (excluding optional network checks if slow).
    3. The CLI wizard effectively gathers all necessary user inputs and provides helpful warnings (e.g., PyPI name conflicts).
    4. Generated projects are complete, correctly personalized, and require no immediate manual boilerplate additions for the defined MVP scope.
- **Success Criteria:**
  - PyHatchery is successfully used by its creator to scaffold a new, non-trivial follow-on project.
  - The CLI wizard consistently guides users to a successful project generation outcome, offering actionable feedback for potential name conflicts.
  - Generated projects are immediately "pushable" to GitHub and ready for application code development.
  - All specified tooling (`uv`, `ruff`, `pylint`, `hatchling`, `pytest`) is correctly configured (largely via `pyproject.toml`, `.ruff.toml`, `.pylintrc`) and functional in the generated project.
  - Personalization (project name, author details, license, etc.) is accurately reflected in all relevant generated files.
- **Key Performance Indicators (KPIs):**
  - Time-to-Project-Ready (target: < 5 minutes).
  - CLI Wizard Completion Rate (target: >95% for valid inputs).
  - PyPI Name Check accuracy and user feedback on its utility.
  - Number of successful project generations by alpha/beta users.
  - Reported issues related to incorrect personalization or tool configuration in generated projects (target: <5 critical issues post-release).

## Scope and Requirements (MVP / Current Version)

### Functional Requirements (High-Level)

- **FR1: Interactive Project Generation:** The system must provide a CLI command (`pyhatchery new <project_name>`) that initiates an interactive wizard to gather project details (project name, author name, author email, GitHub username, project description, license choice, Python version preference), offering sensible defaults.
- **FR1A: Project Name Validation (Interactive & Non-Interactive):**
  - Check if the derived PyPI package name is potentially already taken on PyPI and warn the user.
  - Check if the derived Python package name conforms to PEP 8 naming conventions and warn the user.
- **FR2: Non-Interactive Project Generation:** The system must allow project generation with all details specified via command-line arguments (e.g., `pyhatchery new my_project --author "Jane Doe" ...`) and support sourcing defaults from `.env` files. Name validation (FR1A) also applies.
- **FR3: Custom Output Location:** The system must allow users to specify a different output directory for the generated project.
- **FR4: Automated Project Scaffolding:** The system must create a standardized Python project directory structure (e.g., `<project_name>/src/<project_name_slug>/`, `tests/`, `docs/`, `src/<project_name_slug>/__about__.py`).
- **FR5: Tooling Integration & Configuration:** The system must generate projects with pre-configured:
  - `uv` for dependency management (configured in `pyproject.toml`).
  - `hatchling` for building/packaging, with dynamic versioning via `__about__.py` (configured in `pyproject.toml`).
  - `ruff` for linting/formatting (configured in a dedicated `.ruff.toml` file).
  - `pylint` for linting (configured in a dedicated `.pylintrc` file).
  - `pytest` for testing (configured in `pyproject.toml`).
- **FR6: Essential File Generation & Personalization:** The system must generate and personalize:
  - `pyproject.toml` (with metadata, dynamic versioning, dependencies, tool configs for hatch, pytest, uv).
  - `src/<project_name_slug>/__about__.py` (with `__version__ = "0.1.0"`).
  - `.ruff.toml` (with ruff configurations).
  - `.pylintrc` (with pylint configurations).
  - `LICENSE` file (e.g., MIT, personalized).
  - `README.md` (templated, with project name/description, badges, setup instructions).
  - Standard `.gitignore`.
  - Example source file (`src/<project_name_slug>/main.py`) and test file (`tests/test_main.py`).
- **FR7: GitHub Actions Workflow Generation:** The system must include ready-to-use GitHub Actions workflow files for automated testing (multi-python version) and (optionally enabled) publishing to PyPI/TestPyPI.
- **FR8: Git Repository Initialization Guidance:** The system must ensure the template's `.git` history is removed and provide clear instructions for initializing a new Git repository.

### Non-Functional Requirements (NFRs)

- **Performance:**
  - Project generation time should be under 5 minutes (excluding network-dependent checks like PyPI availability if connectivity is slow). Ideally under 1 minute for typical scenarios.
  - CLI responsiveness for interactive prompts should be immediate.
  - PyPI name check should have a reasonable timeout (e.g., 5-10 seconds).
- **Scalability:** (Not a primary concern for the CLI tool itself)
  - The tool should handle templating a moderate number of files without significant slowdown.
- **Reliability/Availability:**
  - The project generation process must be robust and handle common user input variations gracefully.
  - Consistent output based on identical inputs.
  - PyPI name check should gracefully handle network errors or API unavailability, informing the user and allowing them to proceed.
- **Security:**
  - PyHatchery's use of `requests` for PyPI checks should follow good practices (e.g., use HTTPS).
  - Generated projects should not include known vulnerable dependency versions by default (tools specified are generally well-maintained).
  - Guidance on managing secrets for PyPI publishing (GitHub secrets) must be clear in the generated `README.md`.
- **Maintainability:**
  - PyHatchery's internal codebase must be well-structured and documented to allow for updates to the template and tooling configurations.
  - The embedded project template (files like `.ruff.toml_template`, `.pylintrc_template`, etc.) must be maintainable and easy to update.
- **Usability/Accessibility:**
  - CLI interactions (wizard, flags, messages, warnings) must be clear, intuitive, and user-friendly.
  - Error messages should be informative and guide the user to correction.
  - Defaults should be sensible and minimize required user input.
  - Warnings (e.g., PyPI name conflict, PEP 8 non-conformance) should be clear but non-blocking.
- **Other Constraints:**
  - PyHatchery itself must be developed in Python `>=3.11`.
  - Generated projects must target Python `>=3.10` (or user preference from wizard).
  - PyHatchery build system: `hatchling >=1.27.0`.
  - Templating: `jinja2`.
  - No higher-level abstraction frameworks like Cookiecutter for templating.
  - Generated projects should use latest stable versions of tools like `uv`, `ruff`, `pylint`, `hatchling`, `pytest`.

### User Experience (UX) Requirements (High-Level)

- **UX Goal 1: Effortless Initiation & Informed Choices:** Users should be able to start a new, well-structured Python project with a single command and minimal, guided configuration, receiving helpful warnings about potential naming issues.
- **UX Goal 2: Confidence in Foundation:** Users should feel confident that the generated project adheres to modern best practices and provides a solid foundation for development.
- **UX Goal 3: Clarity and Guidance:** CLI prompts, messages, warnings, and generated instructions (e.g., in README) must be clear and actionable.
- (For detailed CLI interaction flows, prompt/message specifications, see `docs/ui-ux-spec.md`)

### Integration Requirements (High-Level)

- PyHatchery itself will integrate with:
  - `pypi.org` (via HTTPS GET request) for package name availability checks.
- Generated projects will be pre-configured for integration with:
  - GitHub (for version control and GitHub Actions).
  - PyPI and TestPyPI (for package publishing, if enabled).
  - Python package index (implicitly, for `uv` to fetch dependencies).

### Testing Requirements (High-Level)

- PyHatchery itself requires comprehensive unit and integration tests for its generation logic, personalization, CLI interactions, and PyPI/PEP 8 name validation features.
- Generated projects must include a functional test setup (e.g., using `pytest`) and a GitHub Actions workflow to run these tests automatically.
- (See `docs/testing-strategy.md` for details)

## Epic Overview (MVP / Current Version)

- **Epic 1: Core Project Generation & CLI** - Goal: Establish the basic CLI command structure, perform initial project name validation (PyPI availability, PEP 8 conventions), facilitate interactive and non-interactive input mechanisms for project details, create the fundamental project directory layout, and manage Git repository initialization.
- **Epic 2: File Templating & Personalization** - Goal: Implement the generation of all core project files (`pyproject.toml`, `__about__.py`, `.ruff.toml`, `.pylintrc`, `LICENSE`, `README.md`, `.gitignore`, example files) and ensure accurate, robust personalization of their content.
- **Epic 3: Development Tooling Integration** - Goal: Configure `uv`, `hatchling`, `pytest` within `pyproject.toml`, and ensure `ruff` and `pylint` are configured via their respective dedicated files, with all tools listed as development dependencies and Hatch scripts for common tasks.
- **Epic 4: CI/CD Workflow Automation** - Goal: Create and include pre-configured GitHub Actions workflow files for automated testing and (optionally enabled) package publishing to TestPyPI/PyPI, with clear instructions for activation.

## Key Reference Documents

- `docs/project-brief.md`
- `docs/architecture.md`
- `docs/epic1.md`, `docs/epic2.md`, `docs/epic3.md`, `docs/epic4.md`
- `docs/tech-stack.md`
- `docs/testing-strategy.md`
- `docs/ui-ux-spec.md` (focused on CLI interactions)

## Post-MVP / Future Enhancements

- Support for more project template variations (e.g., data science, web app backend).
- Option to select specific tools to include/exclude.
- Plugin system for extending templates or adding custom setup steps.
- Integration with `pre-commit` and pre-configured hooks.
- Support for other CI/CD systems (e.g., GitLab CI).
- Configuration persistence for user defaults (`~/.pyhatcheryrc`).
- Generating `Dockerfile` for containerization.
- Option to initialize a Git repository automatically.

## Change Log

| Change        | Date       | Version | Description                                      | Author         |
| ------------- | ---------- | ------- | ------------------------------------------------ | -------------- |
| Initial Draft | 2025-05-09 | 0.1     | First draft based on project brief and iterations | 2-PM           |

## Initial Architect Prompt

The following technical guidance is provided to inform architecture decisions for PyHatchery:

### Technical Infrastructure

- **Starter Project/Template:** Not applicable for PyHatchery itself.
- **Hosting/Cloud Provider:** Not applicable for the CLI tool.
- **Frontend Platform:** Not applicable (CLI tool).
- **Backend Platform:** Not applicable (CLI tool).
- **Database Requirements:** Not applicable for PyHatchery itself.

### Technical Constraints

- **PyHatchery Core Language & Platform:** Python `>=3.11`.
- **PyHatchery Build System:** `hatchling >=1.27.0`.
- **PyHatchery Key Libraries (Runtime Dependencies):**
  - Python Standard Library (`argparse`, `pathlib`, `shutil`).
  - `jinja2` for all file templating.
  - `python-dotenv` for managing environment variables for non-interactive mode defaults.
  - `requests` (or similar robust HTTP client) for PyPI name availability check.
- **Templating Approach:** Custom-built project generation logic using `jinja2`. Avoid higher-level frameworks like Cookiecutter.
- **Target Tool Versions (for generated projects):** Generated projects should be configured to use the latest stable versions of `uv`, `ruff`, `pylint`, `hatchling`, and `pytest`.
- **Personalization Robustness:** High attention must be paid to the logic that personalizes file content. This includes handling project names that require slugification (e.g., "My Awesome Project" -> "my-awesome-project" for PyPI name, "my_awesome_project" for Python package/directory name), different author name formats, and ensuring correctness across all templated files (`pyproject.toml`, `README.md`, `LICENSE`, `__about__.py`, tool config files, GitHub Actions workflow files).
- **Template Maintainability:** The structure of the embedded template files and their `jinja2` variables should be designed for ease of update as Python best practices evolve. Configuration for tools like `ruff` and `pylint` will be in their own template files (`.ruff.toml_template`, `.pylintrc_template`).
- **Configuration Structure:** Generated projects will have `pyproject.toml` for core metadata and configurations for `hatch`, `pytest`, `uv`. `ruff` will be configured in `.ruff.toml`, and `pylint` in `.pylintrc`.

### Deployment Considerations

- **PyHatchery Distribution:** `pip install pyhatchery` (via PyPI).
- **Generated Project CI/CD:** Must include GitHub Actions workflows for testing and publishing (publishing disabled by default, user must enable via `ENABLE_PUBLISHING` var and `PYPI_API_TOKEN` / `TEST_PYPI_API_TOKEN` secrets). Instructions for enabling this must be clear in the generated `README.md`.

### Local Development & Testing Requirements (for PyHatchery itself)

- **PyHatchery Development Environment:** Standard Python virtual environments on common OSs (Linux, macOS, Windows). Use `uv` for managing PyHatchery's own dev environment.
- **PyHatchery Development Dependencies:** `hatch`, `hatchling`, `pylint`, `pytest`, `ruff`, `uv` (as per its own `pyproject.toml` dev group).
- **Testing PyHatchery:**
  - Unit tests for individual functions (e.g., personalization logic, slugification, CLI argument parsing, PyPI/PEP 8 check logic).
  - Integration tests that run `pyhatchery new ...` (both interactive and non-interactive modes) and verify the generated project's structure, file content, tool configurations, and presence of correct Hatch scripts.
  - Tests should cover various valid and invalid inputs, including edge cases for project naming and network conditions for the PyPI check.
- **Testing Generated Projects:** Generated projects must have a working test setup (`pytest`) and a GitHub Action to run tests. A simple example test should be included and pass.

### Other Technical Considerations

- **CLI User Experience:**
  - Interactive wizard: Clear prompts, input validation (including for project name with PyPI/PEP 8 checks providing non-blocking warnings and option to re-enter name), sensible defaults (e.g., deriving author name/email from `git config`, default license "MIT").
  - Non-interactive mode: Comprehensive CLI flags, support for `.env` files for sourcing defaults. Project name validation also applies.
  - Error handling: Clear, informative error messages for issues like invalid project names (syntactically), existing output directories, missing required inputs in non-interactive mode. Graceful handling of PyPI check failures.
  - Feedback: Provide user feedback during generation (e.g., "Checking PyPI for name availability...", "Personalizing files...", "Project successfully hatched at /path/to/project!").
- **Git History:** The `.git` directory from any internal template source must be removed from the generated project. Clear instructions should be provided to the user on how to `git init` and make their first commit in the newly generated project.
- **License for PyHatchery:** MIT License. Generated projects default to MIT License but should allow user choice during setup.
- **Evolving Best Practices:** The design should facilitate updating the bundled template files and default tool configurations as Python best practices evolve.

This PRD should now be comprehensive and ready for the Architect.
