# PyHatchery Coding Standards and Patterns

This document outlines the coding standards, architectural patterns, and best practices to be followed during the development of PyHatchery. Adherence to these standards is crucial for maintaining code quality, consistency, and ease of collaboration.

## 1. Architectural / Design Patterns Adopted

The following high-level patterns and decisions, as detailed in `docs/architecture.md`, guide PyHatchery's development:

* **Modular Monolith for CLI:** The application is a single, deployable unit with clearly defined internal components for separation of concerns.
* **Direct Jinja2 Templating:** Core templating logic uses Jinja2 directly for maximum control.
* **Layered Configuration Loading:** CLI flags > `.env` > `git config` > defaults.
* **Component-Based Design:** Code is organized into logical components/services (CLI Handler, Config Loader, Project Name Service, etc.) each with specific responsibilities.
* **Service/Wrapper for External Calls:** The PyPI API interaction is encapsulated in a dedicated HTTP client component.

## 2. Coding Standards

* **Primary Language:** Python (`>=3.11`).
* **Style Guide & Linters:**
  * **PEP 8:** All Python code must adhere to PEP 8 style guidelines.
  * **Ruff:** Used for primary linting (including many Flake8 rules, import sorting, etc.) and code formatting. Configuration is in `.ruff.toml` at the project root. Code should be formatted with Ruff before committing.
  * **Pylint:** Used for more comprehensive static analysis and deeper code quality checks. Configuration is in `.pylintrc` at the project root.
  * **Goal:** Aim for clean passes from both Ruff and Pylint.
* **Naming Conventions:**
  * Modules/Packages: `snake_case` (all lowercase, words separated by underscores).
  * Classes: `PascalCase` (CapWords).
  * Functions, Methods, Variables: `snake_case`.
  * Constants: `UPPER_SNAKE_CASE` (all uppercase, words separated by underscores).
* **File Structure:** Adhere to the layout defined in `docs/project-structure.md`.
* **Asynchronous Operations:**
  * PyHatchery is primarily a synchronous CLI application. Asynchronous operations (e.g., using `asyncio`) are not expected to be a major part of its core logic.
  * If any specific I/O-bound operation (beyond the single PyPI check) is identified as a significant performance bottleneck, `asyncio` might be considered on a case-by-case basis, but the default is synchronous code.
* **Type Safety:**
  * **Type Hints:** Python type hints (PEP 484) must be used for all function signatures (arguments and return types) and variable annotations where appropriate.
  * Strive for code that passes static type checking (e.g., via Ruff's capabilities or implicitly by MyPy if run).
  * Use types from the `typing` module as needed (e.g., `List`, `Dict`, `Optional`, `Any` when truly necessary).
* **Comments & Documentation:**
  * **Docstrings:** All public modules, classes, functions, and methods must have comprehensive docstrings. Google Python Style Docstrings are preferred for consistency.
    * Example:

            ```python
            def my_function(param1: str, param2: int) -> bool:
                """Does something interesting.

                Args:
                    param1: The first parameter, a string.
                    param2: The second parameter, an integer.

                Returns:
                    True if successful, False otherwise.

                Raises:
                    ValueError: If param1 is invalid.
                """
                # ...
            ```

  * **Inline Comments:** Use inline comments (`#`) to explain complex or non-obvious sections of code. Avoid commenting on obvious code.
  * **TODO/FIXME Comments:** Use `TODO:` for planned enhancements and `FIXME:` for known issues that need correction. Include a brief explanation.
* **Dependency Management:**
  * Dependencies are managed using `uv` and defined in `pyproject.toml`.
  * Minimize runtime dependencies. Each addition must be justified.
  * Development dependencies are for local development and testing; they should not be required for the CLI tool to run.
* **Python Idioms:**
  * Prefer idiomatic Python (e.g., list comprehensions, context managers (`with` statement), enumerate).
  * Follow the principle of "Pythonic" code – readability counts.

## 3. Error Handling Strategy

* **General Approach:**
  * Use custom exceptions for application-specific error conditions (e.g., `PyHatcheryError`, `ValidationError`, `TemplateError`). These should ideally inherit from a base `PyHatcheryException`.
  * Use built-in Python exceptions for general errors (e.g., `ValueError`, `TypeError`, `IOError`).
  * Provide clear, user-friendly error messages to the CLI user. Avoid exposing raw stack traces unless in a debug mode.
  * The application should exit with a non-zero status code upon error.
* **Logging:**
  * Use the standard Python `logging` module for any internal logging.
  * Configure a simple default logger that outputs to `stderr`.
  * Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) should be used appropriately.
  * User-facing error messages are distinct from internal debug/info logs. For CLI output, direct `print` to `sys.stdout` or `sys.stderr` (or a helper function for colored/formatted output) is often more appropriate for user messages than the `logging` module. The `logging` module is for internal diagnostics.
* **Specific Handling Patterns:**
  * **External API Calls (e.g., PyPI check):**
    * Wrap calls in `try...except` blocks, catching specific exceptions from the HTTP client library (e.g., `requests.exceptions.Timeout`, `requests.exceptions.ConnectionError`).
    * If the PyPI check fails due to network issues or API unavailability, issue a clear warning to the user but allow the project generation to proceed.
  * **Input Validation (CLI & Wizard):**
    * Validate user inputs as early as possible (e.g., project name format, path validity).
    * Raise specific validation errors or provide clear, actionable feedback to the user, prompting for re-entry if appropriate in interactive mode.
  * **File System Operations:**
    * Wrap file system operations in `try...except` blocks, catching `IOError`, `OSError`, `PermissionError`, etc.
    * Provide informative error messages (e.g., "Error creating directory: <path>. Permission denied.").
  * **Templating Errors:** Catch `jinja2.exceptions.TemplateError` (and subtypes) to report issues with template rendering.

## 4. Security Best Practices

* **Input Sanitization/Validation:**
  * Thoroughly validate all user-provided inputs, especially project names and paths, to prevent unintended behavior or security issues (e.g., path traversal, although `pathlib` helps mitigate this).
  * Ensure that slugs generated for directory and package names are sanitized and conform to expected formats.
* **Secrets Management (for PyHatchery itself):**
  * PyHatchery, as a CLI tool run locally, does not directly manage runtime secrets for its own operation after installation.
  * The PyPI API tokens (`PYPI_API_TOKEN`, `TEST_PYPI_API_TOKEN`) are used only within the CI/CD (GitHub Actions) environment and are managed as GitHub secrets. They are not part of PyHatchery's codebase or distributed package.
* **Dependency Security:**
  * Periodically review dependencies for known vulnerabilities. Tools like `uv audit` (when available/mature) or other third-party scanners can be considered.
  * Keep dependencies updated to their latest stable versions where feasible.
* **External Process Calls (e.g., `git config`):**
  * When calling external processes like `git config` (via `subprocess`), ensure that command arguments are properly escaped or constructed to prevent command injection, especially if any part of the command is derived from user input (though in this case, `git config user.name` is fairly safe). Use list form for `subprocess` arguments rather than string commands with `shell=True`.
* **File Permissions:** When generating project files, ensure they are created with sensible default permissions.

## Change Log

| Change        | Date       | Version | Description                                     | Author      |
| ------------- | ---------- | ------- | ----------------------------------------------- | ----------- |
| Initial draft | 2025-05-09 | 0.1     | Initial draft of coding standards for PyHatchery. | 3-Architect |
