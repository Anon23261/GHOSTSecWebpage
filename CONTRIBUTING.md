# Contributing to GhostSec

First off, thank you for considering contributing to GhostSec! It's people like you that make GhostSec such a great tool for the cybersecurity community.

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check [this list](https://github.com/ghostsec/platform/issues) as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include screenshots if possible

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/ghostsec/platform/issues). When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain the behavior you expected to see
* Explain why this enhancement would be useful

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Development Process

1. Create a new branch:
   ```bash
   git checkout -b feature/my-feature
   # or
   git checkout -b bugfix/my-bugfix
   ```

2. Make your changes:
   * Write meaningful commit messages
   * Follow our coding standards
   * Add tests for new features
   * Update documentation as needed

3. Test your changes:
   ```bash
   # Run tests
   python -m pytest

   # Run linter
   flake8
   ```

4. Push your changes:
   ```bash
   git push origin feature/my-feature
   ```

5. Create a Pull Request

## Coding Standards

* Follow PEP 8 style guide for Python code
* Use meaningful variable and function names
* Write docstrings for all functions and classes
* Keep functions focused and concise
* Comment complex logic
* Use type hints where appropriate

## Testing

* Write unit tests for new features
* Ensure all tests pass before submitting PR
* Include integration tests for complex features
* Test edge cases and error conditions

## Documentation

* Update README.md if needed
* Add docstrings to new functions and classes
* Update API documentation
* Include examples for new features

## Security

* Never commit sensitive data (API keys, passwords, etc.)
* Follow security best practices
* Report security vulnerabilities privately
* Use secure dependencies

## Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

## Additional Notes

### Issue and Pull Request Labels

* `bug`: Something isn't working
* `enhancement`: New feature or request
* `documentation`: Documentation only changes
* `security`: Security related changes
* `good first issue`: Good for newcomers

## Recognition

Contributors who make significant improvements will be added to our [Contributors](README.md#contributors) list.

## Questions?

Feel free to contact the core team if you have any questions. We're here to help!
