# Contributing to Permit Dashboard

Thank you for considering contributing! Please follow these guidelines to help us maintain a high-quality, consistent codebase.

## Code Style
- Format all code with **black**
- Lint with **flake8**
- Use **mypy** for static typing
- Write Google-style docstrings for all functions/classes
- Run `pre-commit install` after cloning to enable pre-commit hooks

## Commit Messages
- Use clear, descriptive commit messages

## New Features
All new features must include:
- At least one unit test
- Docstrings for all public functions/classes
- Pass all linting and typing checks

## Testing
- Run `pytest` for unit tests
- Use `dash.testing` and `playwright` for integration tests
- To check coverage:
  ```bash
  coverage run -m pytest
  coverage report
  ```

## Pull Requests
- Ensure all tests pass before submitting
- All code must be reviewed before merge

## Continuous Integration
- GitHub Actions will run all tests and linting on push/PR
- Code coverage is uploaded to Codecov

## Questions?
Open an issue or contact a maintainer.
