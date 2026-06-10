# Contributing

We're so glad you're thinking about contributing to the **Trend Vision One – Microsoft Sentinel Data Connectors** repository! This repo contains production ARM templates that ship Trend Vision One security data into Microsoft Sentinel via the Codeless Connector Platform (CCP). Because every change can affect a live deployment in someone's Azure tenant, we ask contributors to keep templates deployable and review-friendly.

We welcome contributions from everyone and are particularly looking for help in the following areas:

- **Fixing template or documentation errors** — typos, broken parameter references, outdated screenshots, incorrect KQL examples, or missing fields in `mainTemplate.json` / `createUiDefinition.json`.
- **Adding new features** — additional Trend Vision One data sources, new parser functions, improved data-collection-rule transforms, or richer connector UI.
- **Improving existing documentation** — clearer deployment walkthroughs, better troubleshooting steps, more useful sample KQL queries.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Reporting Issues

Please report issues in the [GitHub issue tracker](https://github.com/trendmicro/trendai-sentinel-ccf-data-connector/issues) using one of the provided templates. Include as much detail as possible — connector (Workbench / OAT), deploy region, commit SHA, Azure portal error output, and any relevant KQL — so we can reproduce the problem.

> **Security vulnerabilities** must **not** be filed as public issues. See [SECURITY.md](SECURITY.md) for the private reporting process.

## Contributing Code

1. **Fork the repository.** Click the *Fork* button at the top right of the repo page and clone your fork locally.
2. **Create a branch.** Use a descriptive name, e.g. `fix/oat-dcr-transform` or `feat/workbench-parser-iocs`.
3. **Make your changes.** Edit templates, parser functions, or documentation. Keep changes focused — one logical change per PR.
4. **Validate locally** before pushing (see below).
5. **Commit your changes** with a clear message describing the *why*, not just the *what*.
6. **Push to your fork** and open a pull request against `main` using the [PR template](.github/PULL_REQUEST_TEMPLATE.md).

## Local Validation

Before opening a pull request, please run these checks:

### JSON syntax

```bash
find templates -name "*.json" -not -path "*/legacy/*" -print0 \
  | xargs -0 -n1 jq empty
```

Every file must parse cleanly.

### ARM template structure

For changes to `mainTemplate.json` or any file under `templates/*/components/`, confirm the required top-level fields exist:

```bash
jq -e '.["$schema"] and .contentVersion and .resources' \
  templates/workbench/mainTemplate.json
```

### Azure validation (recommended for template changes)

If you have an Azure subscription with a Sentinel-enabled workspace, validate the deployment without actually creating resources:

```bash
az deployment group validate \
  --resource-group <your-test-rg> \
  --template-file templates/workbench/mainTemplate.json \
  --parameters workspace=<workspace-name> trendaiRegion=US
```

### End-to-end deployment

For non-trivial template changes, deploy to a test workspace and confirm data ingestion before requesting review. Note in the PR description which workspace/region you tested against.

## Secure Contributor Setup

A few one-time settings on your GitHub account make every contribution
safer for you and for the people who deploy this connector.

### Sign your commits

We strongly recommend signing your commits with **GPG** or **SSH**. Signed
commits show a green *Verified* badge on GitHub and make it harder for
someone to impersonate you. See GitHub's guide:
[About commit signature verification](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification).

Quick start (SSH signing, Git 2.34+):

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

Then add the **same** SSH public key on GitHub under
*Settings → SSH and GPG keys* as a **Signing key** (not just an auth key).

### Use short-lived Personal Access Tokens

If you authenticate with HTTPS + a Personal Access Token, please set an
**expiration date** on the token (90 days or less is a good default).
Long-lived tokens are a top source of leaked credentials. Better still,
use SSH or the GitHub CLI's OAuth flow.

## Style Guidelines

- **ARM JSON:** 2-space indentation, trailing newline. Keep `apiVersion` values consistent across components.
- **Parameter names:** camelCase (matches existing templates).
- **KQL:** Format multi-line queries with one clause per line; align `|` operators.
- **Documentation:** Markdown headings use sentence case; code fences specify the language.

## Pull Request Review

- A maintainer will review your PR within a few business days.
- Address review feedback in additional commits — don't force-push during active review.
- Once approved, a maintainer will squash-merge to `main`.

## Contact

If you have questions about contributing, open a [GitHub discussion](https://github.com/trendmicro/trendai-sentinel-ccf-data-connector/discussions) or contact us at `alloftrendgithubenterpriseadmin@trendmicro.com`.

## Acknowledgements

Thank you to everyone who has helped improve these connectors. Every typo fix, parameter tweak, and parser improvement makes the project more useful for the Sentinel community.
