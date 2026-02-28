# Contributing to Gestor de Olesa

This document outlines the guidelines for contributing to Gestor de Olesa. As a password manager, security, stability, and code quality are our top priorities. All contributors are expected to follow these rules strictly.

## Development Setup

1. Fork and clone the repository to your local environment.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Pull Request Workflow

All code contributions must follow this process:

* **Scope:** Submit small, focused Pull Requests. Each PR must address a single issue or feature. Unrelated changes will be rejected.
* **Traceability:** Every PR must reference an existing open issue (e.g., "Closes #10").
* **Testing:** You must test your changes. Contributions that break existing functionality or lack necessary tests will not be accepted.
* **Review:** All code requires a review and formal approval from a project maintainer before it can be merged.

## Definition of Done

A Pull Request is only considered complete and ready for merging when it meets the following criteria:

- The code executes without errors.
- Tests pass.
- Documentation is updated, if applicable.
- A maintainer has approved the Pull Request.

## Issue Reporting

If you encounter a bug or wish to propose a feature:

1. Search the existing issue tracker to ensure it has not been reported already.
2. Open a new issue providing clear, detailed information. For bugs, include the exact steps to reproduce the problem, the expected result, and the actual outcome.
