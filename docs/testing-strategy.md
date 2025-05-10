# PyHatchery Testing Strategy

## 1. Overall Philosophy & Goals

The testing strategy for PyHatchery aims to ensure the tool is robust, reliable, and correctly generates projects according to specifications. We will focus on extensive automation to enable confident refactoring and continuous delivery.

* **Core Principles:**
  * **Automation:** Maximize automated testing coverage across different levels.
  * **Early Feedback:** Tests should provide quick feedback during development and in CI.
  * **Confidence:** A comprehensive test suite should give confidence in releasing new versions.
  * **Maintainability:** Tests should be readable, maintainable, and reflect user scenarios.
* **Primary Goals:**
    1. Verify that all functional requirements outlined in the PRD are met, particularly regarding project generation, personalization, and tooling configuration.
    2. Prevent regressions in core functionality as the tool evolves.
    3. Ensure the CLI (interactive and non-interactive modes) behaves as expected across various inputs and edge cases.
    4. Validate the correctness of the generated project structure and file contents.
    5. Achieve a high level of code coverage for critical components, with an initial target of >90% for core logic.

## 2. Testing Levels

PyHatchery will employ a multi-layered testing approach:

### 2.1 Unit Tests

* **Scope:** Test individual functions, methods, and classes (our defined components like `ConfigLoader`, `ProjectNameService`, `TemplateProcessor`, etc.) in isolation. Focus on business logic, input validation, slugification, context manipulation, and specific utility functions.
* **Tools:** `pytest`, `pytest-mock` (for the `mocker` fixture) for mocking dependencies.
* **Mocking/Stubbing:** External dependencies such as file system operations (for testing components that would normally write files), `git config` calls, and the PyPI API HTTP calls (`requests`) will be mocked to ensure tests are fast and deterministic.
* **Location:** `tests/unit/` (mirroring the `src/pyhatchery/` structure where applicable).
* **Expectations:**
  * These tests will form the largest portion of the test suite.
  * They must be fast-executing.
  * Cover all significant logic paths, branches, and edge cases within each unit.
  * Examples: Test `ProjectNameService` slugification for various inputs, test `InteractiveWizard` prompt flow with mocked `input()`, test `ConfigLoader` with mocked `subprocess` calls for `git config`.

### 2.2 Integration Tests

* **Scope:** Verify the interaction and collaboration between multiple internal components of PyHatchery. For example, testing the flow from `CLIHandler` to `ContextBuilder` to `TemplateProcessor` with a specific set of inputs, ensuring the correct context is built and templates are attempted to be rendered (output can be checked without actual file system writes, or using temporary directories). This also includes testing the PyPI check mechanism by mocking the HTTP response but testing the `ProjectNameService` and `HTTPClient` interaction.
* **Tools:** `pytest`, `pytest-mock`, `tmp_path` fixture (for tests involving file system interactions in a controlled manner).
* **Location:** `tests/integration/`.
* **Expectations:**
  * Focus on the contracts and interactions between components.
  * Slower than unit tests but faster than full E2E tests.
  * Validate that components work together as designed for specific sub-workflows.

### 2.3 End-to-End (E2E) / Acceptance Tests

* **Scope:** Test the entire PyHatchery CLI application from an end-user perspective. This involves invoking the `pyhatchery` command (e.g., via `subprocess`) and verifying the output.
  * These tests will cover both interactive (simulating user input if feasible, or focusing on non-interactive aspects that share core logic) and non-interactive project generation.
  * Verification includes:
    * Correct creation of the project directory structure.
    * Accurate personalization of key files (e.g., `pyproject.toml`, `README.md`, `LICENSE`, `__about__.py`).
    * Presence and basic correctness of all configured tool files (`.ruff.toml`, `.pylintrc`).
    * Functionality of generated GitHub Actions workflows (by checking their content).
    * Correct handling of CLI arguments, flags, and `.env` files.
    * Validation of PyPI/PEP 8 name checks and their warning outputs.
* **Tools:** `pytest`, `subprocess` module to execute the CLI, helper functions for file system assertions.
* **Environment:** These tests will run in the CI environment and locally, creating temporary project directories for generation and then cleaning them up.
* **Location:** `tests/integration/` (as per PRD, these are considered integration tests for PyHatchery, e.g., `test_project_generation.py`) or a dedicated `tests/e2e/` if preferred for clarity.
* **Expectations:**
  * Cover critical user journeys and generation scenarios.
  * Ensure the final generated project is usable and meets requirements.
  * These are the most comprehensive tests and will be slower than unit or integration tests.

## 3. Specialized Testing Types

* **Static Analysis & Linting:** Covered by `Ruff` and `Pylint` as part of the coding standards and CI checks. These tools help catch potential bugs and style issues early.
* **Security Testing (Basic):**
  * Input validation tests (unit and E2E) are critical to prevent issues related to malicious or malformed inputs (e.g., project names, paths).
  * Dependency security: Periodically review dependencies. `uv audit` can be incorporated into developer workflows or CI once it matures and supports this effectively.
* **Performance Testing:** Not a primary focus for the MVP, but the overall project generation time should be monitored informally (target < 5 minutes, ideally much faster). If specific operations are identified as bottlenecks, targeted performance tests might be introduced.

## 4. Test Data Management

* **Unit/Integration Tests:** Test cases will use hardcoded or programmatically generated input data (e.g., different project names, author details, configurations). `pytest` fixtures and parameterization (`@pytest.mark.parametrize`) will be used extensively to cover various scenarios with different data inputs.
* **E2E Tests:** Will use predefined sets of inputs (project name, author, etc.) to generate projects. The "expected output" will be a combination of directory structure assertions and partial content checks for key files.
* **Internal Templates:** The `src/pyhatchery/templates/default_project/` directory itself serves as a form of test data, as its structure and content are key to the generation process.

## 5. CI/CD Integration

* **Execution:** All automated tests (unit, integration, E2E) will be executed automatically in the GitHub Actions CI pipeline on every push to `main` and `develop` branches, and on all pull requests targeting these branches.
* **Commands:** Tests will be run using `uv run pytest -v --cov=src/pyhatchery --cov-report=term-missing` (or similar, specific path to cover PyHatchery's source) to include coverage reporting.
* **Pipeline Failure:** The CI pipeline will fail if any tests fail or if code coverage (if a threshold is set) drops below the defined limit. This prevents merging problematic code.
* **Linters/Formatters:** Ruff and Pylint checks are also part of the CI pipeline, ensuring code quality before tests are run.

## Change Log

| Change        | Date       | Version | Description                                          | Author      |
| ------------- | ---------- | ------- | ---------------------------------------------------- | ----------- |
| Initial draft | 2025-05-09 | 0.1     | Initial draft of the testing strategy for PyHatchery. | 3-Architect |
