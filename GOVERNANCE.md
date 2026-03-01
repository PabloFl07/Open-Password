Governance for Gestor de Olesa

This document defines the roles, decision-making processes, and expectations for the maintainers of Gestor de Olesa. As a security-focused project, strict adherence to this governance model is required to ensure the integrity of the password manager.
1. Roles

    Users: Individuals who deploy and use Gestor de Olesa. They are encouraged to report issues and request features.

    Contributors: Community members who submit Pull Requests containing code, tests, or documentation.

    Maintainers: Core team members with write access to the repository. They review and merge code, triage issues, and enforce security standards.

    Lead Maintainers: Administrators of the project. They manage repository settings, handle the release process, and resolve deadlocks in decision-making.

2. Decision-Making Process

Technical decisions are evaluated based on their impact on system security and architecture.

    Lazy Consensus (Minor Changes): Routine bug fixes and minor feature additions operate on a lazy consensus model. A Pull Request requires approval from at least one Maintainer. If no other Maintainer objects within 72 hours, it may be merged.

    Voting and Consensus (Major/Security Changes): Modifications to cryptographic implementations, core architecture, or external dependencies require formal review. These changes must be discussed in a public issue and require explicit approval from a majority of active Maintainers.

    Veto Power: Lead Maintainers retain the right to veto any contribution that introduces unacceptable security risks or deviates from the project's core scope.

3. Maintainer Expectations

Maintainers hold a position of trust and must operate under the following expectations:

    Security Prioritization: Maintainers must thoroughly audit all incoming code for vulnerabilities, logic errors, and secure credential handling. Code review is not a formality; it is a security gate.

    Active Participation: Maintainers are expected to actively triage issues, review Pull Requests, and guide Contributors. Reviews should be completed within a reasonable timeframe (typically 7 days).

    Professional Conduct: Maintainers must enforce and adhere to the project's Code of Conduct, keeping all communication objective, technical, and professional.

    Access Management: To minimize the risk of compromised accounts, Maintainers who remain inactive for a period exceeding six months will have their repository write access revoked. Access can be reinstated upon their return to active development.
