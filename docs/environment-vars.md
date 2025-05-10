# PyHatchery Environment Variables

This document outlines environment variables that are primarily relevant to the development, CI/CD pipeline, and publishing process of the PyHatchery tool itself. PyHatchery as a CLI application, when run by an end-user, mainly relies on command-line arguments, interactive prompts, and an optional `.env` file (for sourcing project generation inputs in non-interactive mode) rather than system environment variables for its core operation.

## 1. Configuration Loading Mechanism (for PyHatchery's own context)

* **Local Development (PyHatchery CLI Itself):** PyHatchery itself does not generally require specific environment variables to be set for its core logic to run during local development or when used by an end-user.
* **`.env` File for Project Generation Defaults:** PyHatchery *can read* a `.env` file located in the current working directory when the `--no-interactive` flag is used. This file is used to source default values for *project generation parameters* (e.g., `AUTHOR_NAME`, `PROJECT_DESCRIPTION`) if they are not provided as CLI flags. The `python-dotenv` library is used for this. These are not environment variables that configure PyHatchery's own behavior but rather provide input data for its generation task. An `.env.example` in the PyHatchery project root guides developers on these potential variables.
* **CI/CD (GitHub Actions):** Environment variables listed below are primarily set and used within the GitHub Actions workflows. Secrets are managed using GitHub encrypted secrets.

## 2. Key Environment Variables (for CI/CD and Publishing)

The following table lists environment variables specifically used in the context of PyHatchery's automated testing and publishing workflows:

| Variable Name           | Description                                                                                                | Example / Default Value (in workflow) | Required? (for CI/CD task) | Sensitive? (Yes/No) | Notes                                                                                                |
| :---------------------- | :--------------------------------------------------------------------------------------------------------- | :------------------------------------ | :------------------------- | :------------------ | :--------------------------------------------------------------------------------------------------- |
| `ENABLE_PUBLISHING`     | Controls whether the `publish.yml` GitHub Actions workflow proceeds with publishing to PyPI/TestPyPI.        | `true` (as set in `publish.yml`)      | Yes (for publishing job logic) | No                  | Defined directly in the `env` block of the `publish.yml` workflow file. To disable, this line must be edited. |
| `PYPI_API_TOKEN`        | API token for authenticating with the official Python Package Index (PyPI) for publishing PyHatchery.      | `${{ secrets.PYPI_API_TOKEN }}`       | Yes (for PyPI publishing)  | Yes                 | Must be configured as an encrypted secret in the GitHub repository settings.                             |
| `TEST_PYPI_API_TOKEN`   | API token for authenticating with the TestPyPI repository for publishing test versions of PyHatchery.        | `${{ secrets.TEST_PYPI_API_TOKEN }}`  | Yes (for TestPyPI publishing) | Yes                 | Must be configured as an encrypted secret in the GitHub repository settings.                             |
| `GITHUB_TOKEN`          | Automatically provided by GitHub Actions. Used by actions for various API interactions (e.g., checking out code). | (Token string)                        | Yes (by GitHub Actions)    | Yes                 | No manual setup needed; used implicitly by many actions.                                             |

## 3. Notes

* **Secrets Management:** All sensitive environment variables (`PYPI_API_TOKEN`, `TEST_PYPI_API_TOKEN`, `GITHUB_TOKEN`) used in the CI/CD pipeline are managed as encrypted secrets within the GitHub repository settings. They are not hardcoded in workflow files or the codebase (they are referenced via `${{ secrets.SECRET_NAME }}`).
* **`ENABLE_PUBLISHING` Control:** As `ENABLE_PUBLISHING` is defined within the `publish.yml` file, enabling or disabling the actual publishing step requires modifying this workflow file directly. The `README.md` generated for new projects by PyHatchery should accurately reflect this method of control for its own template publishing workflow. *(Self-correction: The PRD/Epic 4 for *generated projects* mentioned `ENABLE_PUBLISHING` as a repo variable. This detail for PyHatchery itself is different and now noted. The templates PyHatchery *generates* for other projects might still suggest a repo variable as per Epic 4, Story 4.3 for *those generated projects*).*
* **`.env` File for Project Generation Inputs:**
  * PyHatchery can load values from a `.env` file in the current working directory when generating a project non-interactively (if specific CLI flags for project details are omitted).
  * This `.env` file is for providing *inputs to PyHatchery's generation process* (e.g., `AUTHOR_NAME="Jane Doe"`, `PROJECT_DESCRIPTION="My new project"`).
  * An `.env.example` file is included in the PyHatchery project root to show the structure and variables that can be used in such a `.env` file by users of PyHatchery or developers testing non-interactive mode. This file is **not** for configuring PyHatchery's own runtime behavior in a service-like manner.
* **No Runtime Environment Variables for PyHatchery Core CLI:** PyHatchery's core CLI functionality on an end-user's machine is not designed to be configured by system environment variables.

## Change Log

| Change        | Date       | Version | Description                                                                               | Author      |
| ------------- | ---------- | ------- | ----------------------------------------------------------------------------------------- | ----------- |
| Initial draft | 2025-05-09 | 0.1     | Initial draft of environment variables for CI/CD and clarifications.                      | 3-Architect |
| Revision      | 2025-05-09 | 0.1.1   | Corrected `ENABLE_PUBLISHING` to reflect it's set in workflow YAML, not as a repo variable. | 3-Architect |
