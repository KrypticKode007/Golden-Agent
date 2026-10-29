# Security Policy

## Supported Versions

Security fixes are applied to the latest release on the `main` branch.

## Reporting a Vulnerability

Please do not open a public issue for security problems.

Report vulnerabilities privately through GitHub's
**Security > Report a vulnerability** feature on this repository.

Include:

- A description of the issue and its impact
- Steps to reproduce, or a proof of concept
- Affected files, versions, or commits

You can expect an acknowledgment within 5 business days.

## Deployment Guidance

Golden-Agent is designed to run with elevated, hardware-level access.

- Run on dedicated or tightly controlled hosts.
- Encrypt model weights at rest with `encrypt_weights.py`.
- Rotate keys regularly with `key_rotation_manager.py`.
- Never commit keys, tokens, or credentials.
- Bind the streaming interface to trusted network interfaces only.
