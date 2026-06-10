# 🔒 INTERNAL — Test-deploy & publishing notes

> **Audience: Trend Micro maintainers only.**
> This page documents the temporary test-deploy plumbing used **while the repository is private**. It references internal hosts and an internal storage account.
>
> **Before the repo goes public, this `internal/` folder should be removed (or the test-deploy section pruned)** and the README's "Test Deploy (Azure Storage-hosted…)" block deleted. See the [Go-Live Checklist](../../.github/GO_LIVE_CHECKLIST.md).

---

## Why this exists

The public "Deploy to Azure" buttons point at **GitHub raw URLs**. Those only work once the repo is **public** — the Azure Portal fetches the nested component templates anonymously, and GitHub raw returns 404 for private repos.

So while the repo is private, we mirror the templates to a **public Azure Blob container** that the portal *can* read without auth, and use a second set of "Test Deploy" buttons that point at the blob URLs.

```
Private repo (templates/)  ──publish-templates.sh──▶  Azure Blob (public read)  ──▶  "Test Deploy" buttons work
```

Once the repo is public, the GitHub-raw buttons work directly and this mirror is no longer needed.

---

## The storage account

| | |
|---|---|
| Account | `trendaiccf45` |
| Container | `arm-templates` (public blob read) |
| Layout | `arm-templates/{workbench,oat}/…` and `arm-templates/assets/…` |

The connector logos and the blob-hosted templates are served from here. Note the connector definitions currently reference the logo at `https://trendaiccf45.blob.core.windows.net/arm-templates/assets/trendai-logo.svg` — that URL must keep resolving (or be repointed to the GitHub raw asset) when this account is retired.

---

## One-time setup (per maintainer)

```bash
# Install Azure CLI
#   macOS:  brew install azure-cli
#   Linux:  https://learn.microsoft.com/cli/azure/install-azure-cli-linux

az login
az account set --subscription "<subscription that owns trendaiccf45>"
```

**Access required:** at least **Contributor** (or **Storage Account Key Operator Service Role**) on `trendaiccf45`, so `az storage account keys list` works. Data-plane-only access? Use a SAS token instead (the script accepts `AZURE_STORAGE_SAS_TOKEN`).

---

## Publishing after you change templates

Every time you edit anything under `templates/`, re-publish so the test-deploy buttons serve current code:

```bash
export AZURE_STORAGE_KEY="$(az storage account keys list \
  --account-name trendaiccf45 \
  --query '[0].value' -o tsv)"

./scripts/publish-templates.sh            # both connectors
# or: ./scripts/publish-templates.sh workbench
# or: ./scripts/publish-templates.sh oat
```

What [scripts/publish-templates.sh](../../scripts/publish-templates.sh) does:

1. Stages `templates/<connector>/` into a temp dir.
2. **Rewrites the `baseUrl`** in `mainTemplate.json` from the GitHub-raw URL to the blob URL, so the nested component fetches resolve from the blob while private.
3. Uploads to `trendaiccf45/arm-templates/<connector>/` with `no-cache` so the portal always gets the latest.
4. Also uploads `assets/`.

**Auth precedence** in the script: `AZURE_STORAGE_KEY` → `AZURE_STORAGE_SAS_TOKEN` → `az login` (needs *Storage Blob Data Contributor*).

> ⚠️ The script edits a staged copy, not your working tree — but it does `sed` the `baseUrl`. Don't commit a `mainTemplate.json` whose `baseUrl` points at the blob; the committed version must keep the **GitHub raw** URL for the public buttons.

---

## Going public — what changes here

When the repo flips to public ([Go-Live Checklist](../../.github/GO_LIVE_CHECKLIST.md)):

1. The GitHub-raw "Deploy to Azure" buttons start working on their own.
2. Delete the **"Test Deploy (Azure Storage-hosted…)"** section from the [README](../../README.md).
3. Repoint or re-host the **logo** asset off `trendaiccf45` if you plan to retire the storage account.
4. Remove this `internal/` folder (or at least this page) so external readers don't see internal hosts.
5. Confirm `mainTemplate.json` `baseUrl` values point at the public GitHub raw path (they should already).

---

## Related internal references

- [Go-Live Checklist](../../.github/GO_LIVE_CHECKLIST.md) — full pre-public checklist (secret scans, branch protection, etc.)
- Trend Micro OpenSource Community Standards Policy (Confluence, internal)
