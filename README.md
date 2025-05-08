# Py Project Maker

**A template for creating new Python projects.**

This project provides a basic structure and starting point for new Python projects. It includes common configurations and tools to help you get started quickly.

Imagine seamlessly starting your new Python project with a well-organized structure and pre-configured tools in minutes!

## Table of Contents

- [Py Project Maker](#py-project-maker)
  - [Table of Contents](#table-of-contents)
  - [What is this?](#what-is-this)
  - [Key Goals \& Features](#key-goals--features)
  - [How it Works](#how-it-works)
    - [Quick Start with the Project Factory](#quick-start-with-the-project-factory)
    - [Manual Setup](#manual-setup)
  - [Contributing](#contributing)
  - [License](#license)

## What is this?

- **Py Project Maker:** A starting point for new Python projects.

## Key Goals & Features

- **Quick Start:** Get your Python project up and running quickly with a pre-defined structure and an easy-to-use project factory script.
- **Best Practices:** Includes common configurations and tools following Python best practices.
- **Customizable:** Easily adapt the template to your specific project needs.
- **Standardization:** Adhere to common Python project standards.
- **Modern Tooling:** Uses [uv](https://github.com/astral-sh/uv) for dependency management and virtual environments.

## How it Works

### Quick Start with the Project Factory

TODO: The approach and setup script need to be finalized.

Once the script completes, you'll have a beautiful standardized project setup. Look over the `README.md` and
start to complete your `docs/design.md` and start to fill in the details.

To auto-publish your package to TestPyPi and PyPi (on pushes to `develop` and `main`, respectively), you'll have to set `ENABLE_PUBLISHING` to `true` in `.github/workflows/publish.yml` and add the proper GitHub Actions secrets to your new repository. Also, to enforce git PR discipline, consider creating the Git rulesets as outlined in `docs/contributing.md`.

Happy hacking!!!

### Manual Setup

If you prefer to set up manually, you can:

1. **Clone or Use Template:** Start your new project by cloning this repository or using it as a template on GitHub.
2. **Customize:** Modify the project name, description, and other details in `pyproject.toml` and other configuration files.
3. **Develop:** Add your project-specific code and logic.
4. **Test:** Write and run tests for your code.
5. **Build and Distribute:** Build your project and distribute it as needed.

## Contributing

Feedback on the template is highly welcome! Please open an issue to share your thoughts or suggestions.

Read the [contribution document here](./docs/contributing.md) and please follow the guidelines for this repository.

## License

Copyright (c) 2025, [Kayvan Sylvan](kayvan@sylvan.com) Licensed under the [MIT License](./LICENSE).
