# Contributing to JARVIS

Thank you for considering contributing to JARVIS! We welcome contributions of all kinds.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Branch Naming](#branch-naming)
- [Commit Messages](#commit-messages)
- [Coding Style](#coding-style)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project is governed by the [Contributor Covenant](CODE_OF_CONDUCT.md).
By participating, you agree to uphold its terms.

## Getting Started

1. Fork the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate it and install dependencies: `pip install -r requirements.txt`
4. Make your changes in a new branch.

## Branch Naming

Use descriptive names with a forward slash separator:

- `feature/add-voice-input`
- `fix/memory-leak`
- `docs/improve-readme`
- `refactor/streaming-logic`

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short summary>

<body>
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`

**Examples:**

- `feat(memory): add long-term recall`
- `fix(brain): handle missing model error`
- `docs(readme): add installation steps`
- `refactor(streaming): extract token printer`

## Coding Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/).
- Use 4 spaces for indentation (no tabs).
- Maximum line length: 100 characters.
- Add docstrings to all public functions and modules.
- Keep functions small and focused (single responsibility).
- Use meaningful variable names.
- Run `python -m py_compile` on changed files to verify syntax.

## Pull Request Guidelines

1. Open an issue first to discuss significant changes.
2. Keep PRs focused — one feature or fix per PR.
3. Update the CHANGELOG.md if your change is user-facing.
4. Ensure all tests pass (when tests are added).
5. Link the PR to any related issues.
6. Request review from at least one maintainer.

## Reporting Issues

Report bugs and suggest features via [GitHub Issues](https://github.com/USERNAME/jarvis-ai/issues).
Include steps to reproduce, expected behavior, and actual behavior for bugs.
