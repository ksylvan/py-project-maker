# Epic 1: Core Project Generation & CLI

**Goal:** Establish the basic CLI command structure (`pyhatchery new`), perform initial project name validation (PyPI availability, PEP 8 conventions), facilitate interactive and non-interactive input mechanisms for project details, create the fundamental project directory layout according to Python best practices, and manage Git repository initialization for the newly generated project.

## Story List

### Story 1.1: Basic CLI Command and Project Name Input

- **User Story / Goal:** As a Python developer, I want to run `pyhatchery new <project_name>` so that I can initiate the project generation process and specify the name for my new project.
- **Detailed Requirements:**
  - Implement a main CLI entry point using `argparse` or a similar library.
  - The `new` subcommand should accept a mandatory `project_name` argument.
  - Perform basic validation on the `project_name` (e.g., ensure it's a valid potential directory name, not empty). Complex validation like PEP 8 and PyPI checks will be handled in Story 1.1A.
  - Store the provided project name for later use in generation and further validation.
- **Acceptance Criteria (ACs):**
  - AC1: Running `pyhatchery new my_new_project` executes the command successfully.
  - AC2: Running `pyhatchery new` without a project name displays a helpful error message and usage instructions.
  - AC3: Invalid project names based on basic syntax (e.g., empty string) result in a clear error message.
  - AC4: The provided `project_name` is correctly captured for subsequent processing.

### Story 1.1A: Project Name Validation (PyPI Availability & PEP 8 Convention)

- **User Story / Goal:** As a Python developer, when I provide a project name, I want to be warned if its derived package name is likely already taken on PyPI or if it doesn't follow PEP 8 naming conventions, so I can make an informed decision before proceeding.
- **Detailed Requirements:**
  - This story's checks should occur after the project name is input (either via CLI argument from Story 1.1 or during the interactive wizard if it allows name input/confirmation in Story 1.2).
  - **PyPI Check:**
        1. Derive the potential PyPI package name from the input project name (e.g., a lowercase, hyphenated slug like "my-project-name").
        2. Query `pypi.org` (using an HTTP client like `requests`) to check if this PyPI package name appears to be taken.
        3. The check must handle network errors (e.g., timeouts, no connection) gracefully. If an error occurs, inform the user that the PyPI check could not be completed and allow them to proceed.
        4. If the name seems to be taken on PyPI, display a non-blocking warning to the user (e.g., "Warning: The name '{pypi_package_name}' might already be taken on PyPI. You may want to choose a different name if you plan to publish this package publicly.").
  - **PEP 8 Package Name Check:**
        1. Derive the Python package/module name from the input project name (e.g., an all-lowercase slug with underscores, like "my_project_name", intended for `src/my_project_name` and Python imports).
        2. Validate this derived Python package name against PEP 8 naming conventions for packages (e.g., must be all lowercase, words can be separated by underscores, must be a valid Python identifier).
        3. If the derived name does not conform, display a non-blocking warning (e.g., "Warning: The derived Python package name '{python_package_name}' (from your input '{original_project_name}') does not strictly follow PEP 8 package naming conventions (e.g., 'all_lowercase_with_underscores'). Consider a name that results in a conforming slug for better Python ecosystem compatibility.").
  - The user must be able to proceed with the project generation despite any of these warnings. The wizard should ideally ask if they want to proceed or re-enter the name after warnings are shown.
  - **Dependency Note:** PyHatchery will require the `requests` library (or a similar HTTP client) as a runtime dependency to implement the PyPI check.
- **Acceptance Criteria (ACs):**
  - AC1: If the derived PyPI package name is likely taken on PyPI, a clear, non-blocking warning is displayed.
  - AC2: If the derived Python package name does not conform to PEP 8 package naming conventions, a clear, non-blocking warning is displayed.
  - AC3: These checks are performed after the project name is provided, before asking for subsequent details in the interactive wizard.
  - AC4: The user can explicitly choose to continue with the current project name despite any warnings, or is offered a chance to re-enter the name.
  - AC5: PyPI check failures due to network issues are handled gracefully, inform the user, and do not halt the tool.
  - AC6: `requests` (or equivalent) is identified as a new runtime dependency for PyHatchery.

### Story 1.2: Interactive Wizard for Core Project Details

- **User Story / Goal:** As a Python developer, I want an interactive wizard after running `pyhatchery new <project_name>` (and after initial name validation) to easily provide essential project details.
- **Detailed Requirements:**
  - The wizard prompts for:
    - Author Name (default: from `git config user.name`, else empty)
    - Author Email (default: from `git config user.email`, else empty)
    - GitHub Username (default: empty)
    - Project Description (default: empty)
    - License (default: "MIT"; provide a small list of common choices e.g., MIT, Apache-2.0, GPL-3.0)
    - Python Version Preference for the generated project (default: suggest a recent stable version like 3.10 or 3.11 from a predefined list).
  - Each prompt should clearly indicate what information is needed.
  - User input should be captured for personalization.
  - The wizard should only proceed after the project name has been captured and validated (as per Story 1.1 and 1.1A), potentially offering a chance to re-input the project name if warnings occurred.
- **Acceptance Criteria (ACs):**
  - AC1: After `pyhatchery new my_project` and successful name validation (Story 1.1A), the wizard prompts for Author Name, Author Email, GitHub Username, Description, License, and Python Version.
  - AC2: Defaults for Author Name and Email are correctly pre-filled if available in git config.
  - AC3: User can navigate through prompts and provide input for all required fields.
  - AC4: All inputs provided through the wizard are correctly captured.
  - AC5: User can accept default values by pressing Enter (if applicable).

### Story 1.3: Non-Interactive Mode with CLI Flags and `.env` Support

- **User Story / Goal:** As a Python developer, I want to generate a project non-interactively by providing all details via CLI flags or an `.env` file for automation and consistency.
- **Detailed Requirements:**
  - Implement CLI flags for all details gathered by the wizard: `--author`, `--email`, `--github-username`, `--description`, `--license`, `--python-version`.
  - Add a `--no-interactive` flag to suppress the wizard and rely on CLI flags or `.env` file.
  - Project name validation (Story 1.1A) must still be performed; warnings will be displayed, but in non-interactive mode, the process continues without prompting to re-enter (unless a fatal error like output dir exists).
  - If `--no-interactive` is used and required details are missing from flags, the tool should attempt to load them from a `.env` file in the current directory.
  - If required details are still missing in non-interactive mode, display an error message listing the missing parameters and exit.
  - CLI flags should override `.env` values, which override defaults.
- **Acceptance Criteria (ACs):**
  - AC1: Running `pyhatchery new my_project --no-interactive --author "Test User" --email "test@example.com" ...` generates a project without prompts (but will show PyPI/PEP8 warnings if applicable).
  - AC2: If a `.env` file exists with `AUTHOR_NAME="Env User"`, and `pyhatchery new my_project --no-interactive` is run without an `--author` flag, "Env User" is used.
  - AC3: If `--no-interactive` is used and a required field (e.g., author name, if no default mechanism) is not provided via flag or `.env`, an informative error is shown and the tool exits.
  - AC4: CLI flags correctly override values from a `.env` file.

### Story 1.4: Basic Project Directory Structure Creation

- **User Story / Goal:** As a Python developer, I want PyHatchery to create a standard, best-practice directory structure for my new project.
- **Detailed Requirements:**
  - Create a root directory named `project_name` (original user input, can have spaces/caps).
  - Inside the root, create:
    - `src/<project_name_slug>/` (where `project_name_slug` is the Python module-friendly version like "my_project_name").
    - `tests/`
    - `docs/` (can be empty initially)
- **Acceptance Criteria (ACs):**
  - AC1: After successful execution, a root directory matching `project_name` is created.
  - AC2: The `src/<project_name_slug>/`, `tests/`, and `docs/` subdirectories are created within the root.
  - AC3: `project_name_slug` is correctly derived (e.g., "My Project" becomes "my_project").

### Story 1.5: Custom Output Location

- **User Story / Goal:** As a Python developer, I want to specify where PyHatchery creates the new project directory, instead of always using the current working directory.
- **Detailed Requirements:**
  - Implement an `--output-dir` (or `-o`) CLI flag.
  - If provided, the root project directory should be created inside this specified path.
  - If the output directory does not exist, attempt to create it.
  - If the target project directory (`<output_dir>/<project_name>`) already exists, the tool should warn the user and exit.
- **Acceptance Criteria (ACs):**
  - AC1: Running `pyhatchery new my_project --output-dir /tmp/projects` creates `my_project` inside `/tmp/projects/`.
  - AC2: If `/tmp/projects` does not exist, it is created.
  - AC3: If `/tmp/projects/my_project` already exists, an error message is displayed, and no files are overwritten.
  - AC4: If `--output-dir` is not provided, project is created in the current working directory.

### Story 1.6: Git Repository Initialization Guidance

- **User Story / Goal:** As a Python developer, after PyHatchery generates my project, I want clear instructions on how to initialize it as a new Git repository, ensuring no template history is included.
- **Detailed Requirements:**
  - If PyHatchery uses an internal template that is itself a Git repository, ensure the `.git` directory from this template is *not* copied to the generated project.
  - After project generation, display a success message that includes concise instructions:

        ```
        Project <project_name> successfully hatched at <project_path>!
        Next steps:
          cd <project_path>
          git init
          git add .
          git commit -m "Initial commit: project structure from PyHatchery"
        ```

- **Acceptance Criteria (ACs):**
  - AC1: The generated project directory does not contain a `.git` sub-directory from any template.
  - AC2: A success message is displayed upon completion.
  - AC3: The success message includes the recommended `git init`, `git add`, and `git commit` commands.
  - AC4: The `<project_path>` in the message correctly points to the newly created project directory.
