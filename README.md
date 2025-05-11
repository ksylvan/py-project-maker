# PyHatchery 🐍🥚

[![License: MIT][mit_license]][mit_license_link]

| main  |   |  | develop  |   |
|:---:|:---:|:---:|:---:|:---:|
| [![Main Tests][main_tests]][main_tests_link] | [![Main Publish][main_publish]][main_publish_link] |  | [![Develop Tests][develop_tests]][develop_tests_link] | [![Develop Publish][develop_publish]][develop_publish_link] |

<div align="center">
<img src="https://github.com/ksylvan/pyhatchery/blob/main/docs/hatchery_logo.jpg?raw=true" alt="cute snake hatching" width="267" height="200">
</div>

**Hatch new Python projects instantly!**

PyHatchery is a command-line tool that generates a standardized, best-practice project structure with modern tooling like [uv][astral-uv] for dependency management, and `ruff` and `pylint` for linting/formatting, all pre-configured.

Stop wrestling with boilerplate and start coding faster. Inspired by the efficiency of [hatchling][hatchling_url], PyHatchery helps you seamlessly start new Python projects with a well-organized structure in minutes!

- [PyHatchery 🐍🥚](#pyhatchery-)
  - [Key Goals \& Features](#key-goals--features)
  - [Installation](#installation)
  - [How it Works: The PyHatchery Wizard](#how-it-works-the-pyhatchery-wizard)
  - [Post-Setup Recommendations](#post-setup-recommendations)
  - [Understanding the Project Structure (Optional)](#understanding-the-project-structure-optional)
  - [Contributing](#contributing)
  - [License](#license)

## Key Goals & Features

- 🚀 **Rapid Project Scaffolding:** Generate a complete project skeleton with a single command.
- 🛠️ **Modern Tooling Pre-configured:** Comes with:
  - `uv` for lightning-fast dependency management and virtual environments.
  - `ruff` and `pylint` configurations for immediate code quality checks.
  - ([hatchling][hatchling_url] for building the package).
- ⚙️ **Best Practices Baked In:** Standardized directory layout, basic testing setup, `.gitignore`, and essential configuration files.
- 📝 **Automated Personalization:** Automatically customizes project name, author details, and license information.
- ✅ **Standardized:** Ensures consistency across your Python projects, making them easier to navigate and maintain.
- 🌱 **Foundation for Growth:** Provides a solid, clean base for projects of any scale.

## Installation

You can install PyHatchery directly from PyPI:

pip install pyhatchery

## How it Works: The PyHatchery Wizard

Using PyHatchery is designed to be simple and intuitive. Open your terminal and run:

```bash
# TODO: This needs to be fleshed out...
pyhatchery new your_project_name
```

PyHatchery will then typically:

1. **Ask for Project Details:** Prompt you for information such as:
    - Author Name (e.g., "Your Name")
    - Author Email (e.g., "<your.email@example.com>")
    - Project Description (a short summary of your project)
2. **Clone Template:** Internally, it clones its built-in, best-practice project template.
3. **Personalize Files:** It intelligently updates key files (like `pyproject.toml`, `LICENSE`, `README.md_template`) with your provided project name, author details, and the current copyright year.
4. **Finalize Structure:** Sets up a fresh project structure in a new directory named `your_project_name`.
5. **Clean Up:** Removes the template's `.git` history, allowing you to initialize your own version control.

Once completed, navigate to your new project:

```bash
cd your_project_name
```

Your new Python project is ready. You can now initialize your own Git repository if you wish

```bash
git init
git add .
git commit -m "Initial project structure from PyHatchery"
```

Start developing!

## Post-Setup Recommendations

After your project is hatched, you might want to:

- Review the generated `README.md` in your new project and fill in your project's specific details.
- Begin outlining your project's purpose and vision in a [project brief][project_brief] document.
- To enable auto-publishing of your package to TestPyPI and PyPI (on pushes to `develop` and `main`, respectively) via the included GitHub Actions workflow:
    1. In your new project, set `ENABLE_PUBLISHING` to `true` in `.github/workflows/publish.yml`.
    2. Add the necessary `PYPI_API_TOKEN` (for PyPI) and `TEST_PYPI_API_TOKEN` (for TestPyPI) as GitHub Actions secrets to your new repository.
- To enforce Git PR discipline in your new repository, consider creating Git branch protection rules or rulesets as outlined in PyHatchery's [`docs/contributing.md`][contributing] (adapt as needed for your project).

Happy hacking!!!

## Understanding the Project Structure (Optional)

PyHatchery creates projects based on its embedded template structure. This includes a standard layout for Python projects, such as:

- `src/your_project_name/`: The main package directory.
- `tests/`: For your unit and integration tests.
- `docs/`: For project documentation.
- `pyproject.toml`: Pre-configured for `uv`, `hatchling`, `ruff`, `pylint`, and your project metadata.
- `LICENSE`: Typically an MIT License, personalized with your details.
- `.gitignore`: A standard Python .gitignore file.
- GitHub Actions workflows for testing and publishing.
- `.pylintrc` and `.ruff.toml` settings files.

This structure is designed to be a comprehensive starting point.

## Contributing

Feedback on PyHatchery itself is highly welcome! Please open an issue on the [PyHatchery GitHub repository](https://github.com/ksylvan/pyhatchery) to share your thoughts, suggestions, or report bugs.

Read the [contribution document here][contributing] and please follow the guidelines for this repository.

## License

PyHatchery is licensed under the [MIT License](./LICENSE).
Generated projects will also include a personalized MIT License by default.

Copyright (c) 2025, [Kayvan Sylvan](mailto:kayvan@sylvan.com)

---
[astral-uv]: https://github.com/astral-sh/uv
[contributing]: ./docs/contributing.md
[develop_publish_link]: https://github.com/ksylvan/pyhatchery/actions/workflows/publish.yml?branch=develop
[develop_publish]: https://github.com/ksylvan/pyhatchery/actions/workflows/publish.yml/badge.svg?branch=develop
[develop_tests_link]: https://github.com/ksylvan/pyhatchery/actions/workflows/tests.yml?branch=develop
[develop_tests]: https://github.com/ksylvan/pyhatchery/actions/workflows/tests.yml/badge.svg?branch=develop
[hatchling_url]: https://hatch.pypa.io/latest/
[main_publish_link]: https://github.com/ksylvan/pyhatchery/actions/workflows/publish.yml
[main_publish]: https://github.com/ksylvan/pyhatchery/actions/workflows/publish.yml/badge.svg
[main_tests_link]: https://github.com/ksylvan/pyhatchery/actions/workflows/tests.yml
[main_tests]: https://github.com/ksylvan/pyhatchery/actions/workflows/tests.yml/badge.svg
[mit_license_link]: https://opensource.org/licenses/MIT
[mit_license]: https://img.shields.io/badge/License-MIT-yellow.svg
[project_brief]: ./docs/project_brief.md
