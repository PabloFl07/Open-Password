# Security Policy for Gestor de Olesa

Security is the core of Gestor de Olesa. As a password manager, we enforce strict security practices to protect user data. All contributors must adhere to the following guidelines.

## Reporting a Vulnerability

Do not report security vulnerabilities through public GitHub issues. 

If you discover a security flaw, please practice responsible disclosure by emailing the maintainers directly at pepe.lopez.martinez@udc.es , adrian.gvilar@udc.es , p.fernandezl@udc.es , xabier.pcabanas@udc.es.. We will acknowledge your report within 48 hours and provide status updates as we investigate and resolve the issue.

## Dependency Management

We rely on automated tools (such as Dependabot) to monitor our Python dependencies for known vulnerabilities. 

- Automated Pull Requests updating dependencies should be reviewed and merged promptly.
- Do not downgrade dependencies unless there is a critical, documented compatibility issue.

## Secret Handling

Never commit secrets, API keys, credentials, or passwords to the repository. 

- All local development secrets must be stored in a `.env` file.
- Ensure your `.env` file is never tracked by git (it is already included in our `.gitignore`).
- Use environment variables to handle sensitive configuration in your code.
- Any Pull Request containing hardcoded secrets will be immediately rejected and closed.
