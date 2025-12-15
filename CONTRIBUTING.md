# Contributing to Brilliance

Thank you for your interest in contributing to Brilliance! We welcome contributions from the community to help make this project better.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/YOUR_USERNAME/brilliance.git
    cd brilliance
    ```
3.  **Set up the environment**:
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r ../requirements.txt
    pip install -e .[dev]  # Install dev dependencies (ruff, black, pytest)
    ```

## Development Workflow

1.  Create a new branch for your feature or fix:
    ```bash
    git checkout -b feature/amazing-feature
    ```
2.  Make your changes.
3.  **Lint and Format**:
    We use `ruff` for linting and `black` for formatting.
    ```bash
    ruff check .
    black .
    ```
4.  **Run Tests**:
    ```bash
    pytest
    ```

## Pull Request Process

1.  Push your changes to your fork.
2.  Submit a Pull Request to the `main` branch.
3.  Describe your changes in detail and link to any relevant issues.
4.  Ensure all CI checks pass.

## Code Style

*   **Python**: Follow PEP 8. Use `black` to automatically format your code.
*   **JavaScript/React**: Follow standard React best practices.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub. Provide as much detail as possible, including steps to reproduce the issue.

Thank you for contributing!
