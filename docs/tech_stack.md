# PyHatchery Technology Stack

## Technology Choices

| Category                      | Technology                                  | Version / Details        | Description / Purpose                                                                 | Justification (Optional)                                       |
| :---------------------------- | :------------------------------------------ | :----------------------- | :------------------------------------------------------------------------------------ | :------------------------------------------------------------- |
| **Languages** | Python                                      | `>=3.11`                 | Core programming language for PyHatchery.                                               | Modern Python features, type hinting, community support.       |
| **Runtime Environment** | Python                                      | Matches language version | Execution environment for the CLI tool.                                               | Native to the chosen language.                                 |
| **Build System & Packaging** | hatchling                                   | `>=1.27.0`               | Build backend for packaging PyHatchery.                                               | Modern, standards-based Python packaging tool.  |
|                               | hatch                                       | Latest stable            | Project management, task running (scripts), and environment management for development. | Complements hatchling, provides robust project workflows.      |
| **Key Libraries (Runtime)** | Jinja2                                      | Latest stable            | For templating all generated project files.                                           | Powerful and widely-used templating engine.     |
|                               | python-dotenv                               | Latest stable            | For loading default configurations from `.env` files in non-interactive mode.       | Standard for managing environment variables.    |
|                               | requests (or similar)                       | Latest stable            | For making HTTP requests to check PyPI for package name availability.                 | Well-established HTTP client library.           |
|                               | Python Standard Library (argparse, pathlib, shutil) | Built-in                 | For CLI argument parsing, file system path manipulation, and file operations.       | Core functionalities, no external dependencies needed.       |
| **Development Tools** | uv                                          | Latest stable            | For managing PyHatchery's own development virtual environment and dependencies.       | Fast, modern Python package installer and resolver. |
|                               | Ruff                                        | Latest stable            | For linting and formatting PyHatchery's own codebase.                                 | Extremely fast Python linter and formatter.     |
|                               | Pylint                                      | Latest stable            | For comprehensive static analysis of PyHatchery's codebase.                           | Thorough linter for ensuring code quality.      |
|                               | Pytest                                      | Latest stable            | For writing and running unit and integration tests for PyHatchery.                    | Popular and flexible Python testing framework.  |
|                               | pytest-cov                                  | Latest stable            | For measuring test coverage of PyHatchery's codebase.                                 | Integrates with Pytest for coverage reporting.               |
| **CI/CD** | GitHub Actions                              | N/A                      | For automating testing and optional publishing workflows.                             | Integrated with GitHub, widely used for open source.         |
| **Distribution** | PyPI (Python Package Index)                 | N/A                      | Platform for distributing PyHatchery to users (`pip install pyhatchery`).           | Standard repository for Python packages.        |
| **Databases** | N/A                                         |                          | PyHatchery is a CLI tool and does not require a database.                             |                                                                |
| **Cloud Platform** | N/A                                         |                          | PyHatchery is a local CLI tool, not a cloud-hosted service.                         |                                                                |
| **Frontend Platform** | N/A                                         |                          | PyHatchery is a CLI tool and does not have a frontend UI.                           |                                                                |
| **Backend Platform** | N/A                                         |                          | PyHatchery is a self-contained CLI application.                                     |                                                                |

## Agile Methodology

1. The tasks are stored in `ai/stories/`
2. Each file there contains a task list that addresses that story.
3. A task is NOT COMPLETE till ALL tests and linters pass. From the top directory of the repo, run:

   ```bash
   uv run pytest -v
   uv run ruff check . && uv run pylint .
   ```

   Also, we enforce strict type-checking, so please install pyright as described in the [contributing](./contributing.md) document, and run it like this:

   ```bash
   uv run pyright
   ```

4. As each task is completed, keep the checklists updated.

## Change Log

| Change        | Date       | Version | Description                                     | Author      |
| ------------- | ---------- | ------- | ----------------------------------------------- | ----------- |
| Initial draft | 2025-05-09 | 0.1     | Initial draft based on PRD and Project Brief. | 3-Architect |
| Agile documented | 2025-05-10 | 0.2     | Added note about AI-Agile tasks folder. | Kayvan |
| pyright added | 2025-05-10 | 0.3    | Pyright and strict typing | Kayvan |
