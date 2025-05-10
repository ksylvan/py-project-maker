# Epic 2: File Templating & Personalization

**Goal:** Implement the generation of all core project files (`pyproject.toml`, `__about__.py`, `LICENSE`, `README.md`, `.gitignore`, `.ruff.toml`, `.pylintrc`, example source/test files) and ensure accurate, robust personalization of their content based on user inputs and defaults, reflecting the preferred lean `pyproject.toml` structure and separate tool configurations.

## Story List

### Story 2.1: `pyproject.toml` Generation and Core Personalization

- **User Story / Goal:** As a Python developer, I want a lean `pyproject.toml` file generated with essential project metadata, dynamic versioning, development dependencies via Hatch's `dependency-groups`, and configurations for Pytest and UV, personalized from my inputs.
- **Detailed Requirements:**
  - Generate a `pyproject.toml` file in the project root.
  - Populate `[build-system]`:
    - `requires = ["hatchling>=1.27.0"]`
    - `build-backend = "hatchling.build"`
  - Populate `[project]` table with:
    - `name = "<pypi_project_slug>"` (e.g., lowercase, hyphenated)
    - `dynamic = ["version"]`
    - `description = "<project_description_input>"`
    - `authors = [{name = "<author_name_input>", email = "<author_email_input>"}]`
    - `readme = "README.md"`
    - `requires-python = ">=<python_version_preference>"`
    - `license = {text = "<license_choice_input>"}`
    - `classifiers = ["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License", "Operating System :: OS Independent"]` (adjust Python versions in classifiers based on `requires-python`)
    - `dependencies = []`
  - Populate `[project.urls]` with "Homepage", "Releases", "Bug Tracker", "Documentation" pointing to derived GitHub URLs (`https://github.com/<github_username>/<pypi_project_slug>`).
  - Populate `[dependency-groups]` (Hatch specific):
    - `dev = ["hatch>=1.14.1", "hatchling>=1.27.0", "pylint>=3.3.7", "pytest>=8.3.5", "pytest-cov>=4.0.0", "ruff>=0.11.8", "uv>=0.7.3"]` (use specified or latest stable versions).
  - Populate `[tool.hatch.version]`:
    - `path = "src/<python_package_slug>/__about__.py"`
  - Populate `[tool.pytest.ini_options]`:
    - `testpaths = ["tests"]`
    - `python_files = "test_*.py"`
    - `addopts = "-ra -q --cov=src/<python_package_slug> --cov-report=term-missing"`
  - Populate `[tool.uv.index]` as specified:

        ```toml
        [tool.uv]
        index = [
          { name = "testpypi", url = "[https://test.pypi.org/simple/](https://test.pypi.org/simple/)", publish-url = "[https://test.pypi.org/legacy/](https://test.pypi.org/legacy/)", explicit = true },
          { name = "pypi", url = "[https://pypi.org/simple/](https://pypi.org/simple/)", publish-url = "[https://upload.pypi.org/legacy/](https://upload.pypi.org/legacy/)", explicit = true },
        ]
        ```

  - No `[tool.ruff]` or `[tool.pylint]` sections in `pyproject.toml`.
  - Use `jinja2` for templating.
- **Acceptance Criteria (ACs):**
  - AC1: `pyproject.toml` is created in the project root.
  - AC2: `[project.name]` correctly reflects the PyPI-slugified version of the project name.
  - AC3: `[project]` metadata (description, authors, license, readme, requires-python, classifiers, urls) is correctly populated.
  - AC4: `[project]` lists `dynamic = ["version"]`.
  - AC5: `[build-system]` is correctly configured for `hatchling`.
  - AC6: `[dependency-groups].dev` lists the specified development tools including `pytest-cov`.
  - AC7: `[tool.hatch.version].path` points to `src/<python_package_slug>/__about__.py`.
  - AC8: `[tool.pytest.ini_options]` is configured as specified, including coverage options.
  - AC9: `[tool.uv.index]` is configured as specified.
  - AC10: `pyproject.toml` does not contain `[tool.ruff]` or `[tool.pylint]` configurations.

### Story 2.1A: `__about__.py` File Generation for Version Management

- **User Story / Goal:** As a Python developer, I want an `__about__.py` file generated in my source directory to manage my project's version, compatible with Hatch's dynamic versioning.
- **Detailed Requirements:**
  - Create a file named `__about__.py` inside `src/<python_package_slug>/`.
  - The file should contain the initial version string: `__version__ = "0.1.0"`.
- **Acceptance Criteria (ACs):**
  - AC1: `__about__.py` is created in `src/<python_package_slug>/`.
  - AC2: The content of `__about__.py` is `__version__ = "0.1.0"`.

### Story 2.2: `LICENSE` File Generation and Personalization

- **User Story / Goal:** As a Python developer, I want a `LICENSE` file generated corresponding to my chosen license, personalized with my name and the current year.
- **Detailed Requirements:**
  - Based on the user's license choice (e.g., "MIT", "Apache-2.0").
  - Fetch standard license text templates (include at least MIT and Apache 2.0 initially).
  - Personalize the license text with `<author_name_input>` and the current calendar year.
  - Save the result as `LICENSE` in the project root.
- **Acceptance Criteria (ACs):**
  - AC1: A `LICENSE` file is created in the project root.
  - AC2: The content of the `LICENSE` file matches the standard text for the chosen license.
  - AC3: The license text includes the user-provided author name.
  - AC4: The license text includes the current calendar year.

### Story 2.3: `README.md` Template Generation and Personalization

- **User Story / Goal:** As a Python developer, I want a template `README.md` file generated, prepopulated with my project's name, description, badges, and basic usage instructions.
- **Detailed Requirements:**
  - Generate a `README.md` file in the project root.
  - The template should include:
    - `# <original_project_name_input>` as the main heading.
    - The `<project_description_input>` as an introductory paragraph.
    - Badges for Python version, license, PyPI version, build status (GitHub Actions), code coverage. URLs for badges must be correctly derived using GitHub username and PyPI project slug.
    - Sections for "Features", "Installation" (mentioning `uv`), "Usage" (mentioning Hatch scripts for linting, testing, building), "Contributing", "License".
- **Acceptance Criteria (ACs):**
  - AC1: `README.md` is created in the project root.
  - AC2: The main heading of `README.md` is the original user-provided project name.
  - AC3: The user-provided project description is included.
  - AC4: Standard sections (Features, Installation, Usage, etc.) are present.
  - AC5: Relevant badges (Python version, license, PyPI, build status, coverage) are present and correctly formatted with derived URLs.
  - AC6: Installation and usage sections refer to `uv` and Hatch scripts.

### Story 2.4: Standard `.gitignore` File Generation

- **User Story / Goal:** As a Python developer, I want a standard Python `.gitignore` file to be included in my project to keep common unnecessary files out of version control.
- **Detailed Requirements:**
  - Generate a `.gitignore` file in the project root.
  - Populate it with common Python-related ignores (e.g., `__pycache__/`, `*.pyc`, virtual environment directories like `.venv/`, `build/`, `dist/`, `*.egg-info/`, coverage files like `.coverage`, `htmlcov/`), IDE-specific files, and OS-specific files.
- **Acceptance Criteria (ACs):**
  - AC1: A `.gitignore` file is created in the project root.
  - AC2: The file contains comprehensive common Python, venv, build, IDE, and OS ignore patterns.

### Story 2.5: `.ruff.toml` File Generation

- **User Story / Goal:** As a Python developer, I want a `.ruff.toml` file generated with a sensible default configuration for `ruff` linting and formatting.
- **Detailed Requirements:**
  - Generate a `.ruff.toml` file in the project root.
  - Content based on the user-provided example:

        ```toml
        line-length = 88
        target-version = "py<python_version_short>" # e.g., "py310"
        exclude = [
            ".bzr", ".direnv", ".eggs", ".git", ".git-rewrite",
            ".hg", ".ipynb_checkpoints", ".mypy_cache", ".nox",
            ".pants.d", ".pyenv", ".pytest_cache", ".pytype",
            ".ruff_cache", ".svn", ".tox", ".venv", "venv",
            "__pypackages__", "_build", "buck-out", "build", "dist",
            "node_modules", "docs", # Also exclude docs by default
        ]
        [lint]
        select = ["E", "F", "W", "I", "UP", "B", "C4", "SIM", "A"] # Expanded set of useful rules
        ignore = ["E203", "E501"] # E501 if line-length is handled by formatter
        [format]
        quote-style = "double"
        indent-style = "space"
        skip-magic-trailing-comma = false
        line-ending = "auto"
        ```

  - Personalize `target-version` based on the chosen project Python version.
- **Acceptance Criteria (ACs):**
  - AC1: A `.ruff.toml` file is created in the project root.
  - AC2: The file content matches the specified template, with `target-version` personalized.
  - AC3: The `exclude` list includes common directories and `docs`.
  - AC4: A comprehensive set of `lint.select` rules is included.

### Story 2.6: `.pylintrc` File Generation

- **User Story / Goal:** As a Python developer, I want a `.pylintrc` file generated with a sensible default configuration for `pylint`.
- **Detailed Requirements:**
  - Generate a `.pylintrc` file in the project root.
  - Content based on the user-provided example, adapted:

        ```ini
        [MAIN]
        fail-under=9
        ignore=.git,.venv,venv,__pycache__,docs,build,dist,src/<python_package_slug>/__about__.py
        [FORMAT]
        max-line-length=88
        [MESSAGES CONTROL]
        # disable=missing-docstring,too-few-public-methods # Common to relax for starters
        notes=FIXME,XXX,TODO
        ```

  - Personalize the `ignore` path for `__about__.py`.
- **Acceptance Criteria (ACs):**
  - AC1: A `.pylintrc` file is created in the project root.
  - AC2: The file content matches the specified template, with personalization for ignored paths.

### Story 2.7: Example Source File and Test File Generation

- **User Story / Goal:** As a Python developer, I want a minimal example source file and a corresponding test file to be generated, so I can see the project structure in action and have a starting point for tests.
- **Detailed Requirements:**
  - In `src/<python_package_slug>/`, create an example Python file (e.g., `main.py` or `core.py`).
    - This file could contain a simple function (e.g., `def hello(name: str) -> str: return f"Hello, {name}"`).
    - Ensure this file uses type hints and has a basic docstring.
    - Ensure this file passes the configured `ruff` and `pylint` checks.
  - In `tests/`, create an example test file (e.g., `test_main.py` or `test_core.py`).
    - This file should contain a simple test for the example function using `pytest` conventions (e.g., `from <python_package_slug>.main import hello; def test_hello(): assert hello("World") == "Hello, World"`).
    - An empty `__init__.py` file inside `src/<python_package_slug>/`.
    - An empty `__init__.py` file inside `tests/`.
- **Acceptance Criteria (ACs):**
  - AC1: An example Python source file is created in `src/<python_package_slug>/`.
  - AC2: The example source file contains a simple, runnable function with type hints and a docstring, and passes default linter checks.
  - AC3: An example test file is created in `tests/`.
  - AC4: The example test file contains a valid `pytest` test case for the example function.
  - AC5: The import statement in the test file correctly refers to the example source module.
  - AC6: `__init__.py` files exist in `src/<python_package_slug>/` and `tests/`.

### Story 2.8: Project Name Slugification and Consistent Usage

- **User Story / Goal:** As PyHatchery, I need to correctly derive and consistently use various forms of the project name (e.g., for directory names, Python package names, PyPI names) from the user's input.
- **Detailed Requirements:**
  - Define a clear primary "original project name" as input by the user (e.g., "My Awesome Project").
  - Derive a "Python package slug" (e.g., "my_awesome_project") for use in `src/` directory name, import paths, and `__about__.py` path. Typically all lowercase with underscores. This is the name validated against PEP 8.
  - Derive a "PyPI project slug" (e.g., "my-awesome-project") for use in `pyproject.toml`'s `project.name` and GitHub URLs. Typically all lowercase with hyphens. This is the name checked on PyPI.
  - Ensure all templated files use the correct slug or original name where appropriate.
  - Handle edge cases in user input (e.g., names with leading/trailing spaces, special characters not suitable for slugs) by sanitizing them.
- **Acceptance Criteria (ACs):**
  - AC1: Given input "My Test Project", the `src` directory is `my_test_project`.
  - AC2: Given input "My Test Project", the `project.name` in `pyproject.toml` is `my-test-project`.
  - AC3: Given input "My Test Project", the `README.md` title is `My Test Project`.
  - AC4: Personalization logic correctly applies the appropriate slug version in all relevant files and contexts.
  - AC5: The slugification process handles common variations in project naming (spaces, hyphens, capitalization) predictably and robustly.
