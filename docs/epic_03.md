# Epic 3: Development Tooling Integration

**Goal:** Integrate standard Python development tools. `uv`, `hatchling`, and `pytest` will have configurations in `pyproject.toml`. `ruff` and `pylint` will be configured in their own dedicated files (`.ruff.toml`, `.pylintrc`), with all tools listed as development dependencies. Hatch scripts will be set up in `pyproject.toml` for common tasks.

## Story List

### Story 3.1: `uv` Tooling Setup

- **User Story / Goal:** As a Python developer, I want my generated project to list `uv` as a development dependency and have `uv`-specific configurations (like index URLs) in `pyproject.toml`.
- **Detailed Requirements:**
  - Ensure `uv` is listed in `[dependency-groups].dev` in `pyproject.toml`.
  - Ensure `[tool.uv.index]` is configured in `pyproject.toml` as per Story 2.1.
  - The generated `README.md` should include brief instructions on using `uv` with the project (e.g., `uv venv`, `uv pip install -e .[dev]`).
- **Acceptance Criteria (ACs):**
  - AC1: `uv` is listed as a development dependency in `[dependency-groups].dev`.
  - AC2: `pyproject.toml` contains the specified `[tool.uv.index]` configuration.
  - AC3: `README.md` includes basic commands for setting up and using `uv`.

### Story 3.2: `hatchling` and `hatch` Build System Configuration

- **User Story / Goal:** As a Python developer, I want my project to use `hatchling` as the build backend and `hatch` for project management, with configurations in `pyproject.toml` and useful Hatch scripts.
- **Detailed Requirements:**
  - Ensure `pyproject.toml` specifies `hatchling` in `[build-system]` and configures dynamic versioning via `[tool.hatch.version]` (as per Story 2.1).
  - Include `hatch` and `hatchling` in `[dependency-groups].dev` in `pyproject.toml`.
  - Add Hatch scripts for common tasks to `pyproject.toml` under `[tool.hatch.envs.default.scripts]`:

        ```toml
        # General
        clean = "rm -rf .tox .eggs *.egg-info .pytest_cache .coverage htmlcov dist build src/*.egg-info .ruff_cache .mypy_cache" # Comprehensive clean
        build = "python -m hatch build"
        # Linting & Formatting (using ruff and pylint)
        ruff-check = "ruff check src tests"
        ruff-format = "ruff format src tests"
        pylint-check = "pylint src/<python_package_slug> tests"
        lint = ["ruff-check", "pylint-check"] # Run all linters
        format = "ruff-format" # Main formatter
        # Testing
        test = "pytest {args}"
        test-cov = "pytest --cov=src/<python_package_slug> --cov-report=html --cov-report=term-missing {args}"
        # Combined quality check
        check-all = ["lint", "test"]
        ```

  - The `README.md` should mention how to build the project and run these scripts (e.g., `hatch run build`, `hatch run lint`).
- **Acceptance Criteria (ACs):**
  - AC1: `pyproject.toml`'s `[build-system]` and `[tool.hatch.version]` sections are correctly configured.
  - AC2: `hatch` and `hatchling` are listed as development dependencies.
  - AC3: Hatch scripts for `clean`, `build`, `ruff-check`, `ruff-format`, `pylint-check`, `lint`, `format`, `test`, `test-cov`, and `check-all` are defined in `pyproject.toml`.
  - AC4: The project can be successfully built using `hatch run build`.
  - AC5: `README.md` contains instructions for using these Hatch scripts.

### Story 3.3: `ruff` Linter/Formatter Setup

- **User Story / Goal:** As a Python developer, I want `ruff` pre-configured via `.ruff.toml` and listed as a development dependency, with Hatch scripts for easy execution.
- **Detailed Requirements:**
  - Add `ruff` to `[dependency-groups].dev` in `pyproject.toml`.
  - Generate `.ruff.toml` as defined in Story 2.5.
  - Ensure Hatch scripts `ruff-check`, `ruff-format`, `lint`, `format` are defined as in Story 3.2.
- **Acceptance Criteria (ACs):**
  - AC1: `ruff` is included as a development dependency.
  - AC2: A `.ruff.toml` file is generated as per Story 2.5.
  - AC3: Relevant Hatch scripts for `ruff` are available and functional.

### Story 3.4: `pylint` Linter Setup

- **User Story / Goal:** As a Python developer, I want `pylint` pre-configured via `.pylintrc` and listed as a development dependency, with a Hatch script for easy execution.
- **Detailed Requirements:**
  - Add `pylint` to `[dependency-groups].dev` in `pyproject.toml`.
  - Generate `.pylintrc` as defined in Story 2.6.
  - Ensure Hatch scripts `pylint-check` and `lint` are defined as in Story 3.2.
- **Acceptance Criteria (ACs):**
  - AC1: `pylint` is included as a development dependency.
  - AC2: A `.pylintrc` file is generated as per Story 2.6.
  - AC3: Relevant Hatch scripts for `pylint` are available and functional.

### Story 3.5: Test Runner Setup (`pytest`)

- **User Story / Goal:** As a Python developer, I want `pytest` configured as the test runner (with coverage), with its configuration in `pyproject.toml`, listed as a development dependency, and with Hatch scripts for easy execution.
- **Detailed Requirements:**
  - Add `pytest` and `pytest-cov` to `[dependency-groups].dev` in `pyproject.toml`.
  - Ensure `[tool.pytest.ini_options]` in `pyproject.toml` is configured as per Story 2.1.
  - Ensure Hatch scripts `test` and `test-cov` (and `check-all`) are defined as in Story 3.2.
  - The example test from Story 2.7 should run successfully using `hatch run test`.
- **Acceptance Criteria (ACs):**
  - AC1: `pytest` and `pytest-cov` are included as development dependencies.
  - AC2: `[tool.pytest.ini_options]` is correctly configured in `pyproject.toml`.
  - AC3: Relevant Hatch scripts for `pytest` are available and functional.
  - AC4: Example tests pass when run via `hatch run test`.
