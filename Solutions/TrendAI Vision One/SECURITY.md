# Security Policy

## Reporting a Vulnerability

If you believe you have discovered a security vulnerability in this connector,
**please do not open a public GitHub issue.** Reporting publicly puts every
downstream user at risk before a fix is available.

Instead, please report it privately so the maintainers can investigate and
release a fix before the issue is disclosed.

### How to report

- **Email:** `security@trendmicro.com`
- **Trust Center:** https://www.trendmicro.com/en_us/about/trust-center/responsible-disclosure.html
- **Zero Day Initiative:** https://www.zerodayinitiative.com/

When reporting, please include:

- A description of the vulnerability and its potential impact.
- Steps to reproduce, including ARM template parameters, deploy region, and
  workspace configuration where relevant.
- Affected version / commit SHA.
- Your name and contact information for follow-up (optional but helpful).

We aim to acknowledge new reports within **3 business days** and provide a
status update within **10 business days**.

## Scope

This policy covers the contents of this repository:

- ARM templates under `templates/oat/` and `templates/workbench/`
- Linked-template components (`*/components/*.json`)
- Documentation (`*.md`)
- Examples and supporting scripts

It does **not** cover vulnerabilities in:

- Trend Vision One product itself (use the Trend Vision One support channel).
- Microsoft Sentinel / Azure platform (use Microsoft Security Response Center
  https://msrc.microsoft.com/).
- Third-party integrations that may consume data from this connector.

## Disclosure Process

1. Maintainer triages the report and confirms reproducibility.
2. A fix is prepared on a private branch (security advisory if appropriate).
3. The fix is reviewed and merged to `main`.
4. A new release is tagged with release notes describing the issue and
   credit to the reporter (unless anonymity is requested).
5. The corresponding security advisory is published on GitHub.

## Recognition

We appreciate responsible disclosure. Reporters who follow this policy and
allow time to remediate before public disclosure will be credited in release
notes and the security advisory (unless they prefer to remain anonymous).
