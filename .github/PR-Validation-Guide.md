# Azure Sentinel Solutions — PR Validation Guide

This guide covers all GitHub Actions validation checks that run on Pull Requests targeting the `master` branch. Use it to **quickly understand what failed, why it failed, and how to fix it**.

---

## Table of Contents

| # | Validation Check | GitHub Job Name |
|---|---|---|
| 1 | [Sample Data Validation](#1-sample-data-validation) | `sampleDataValidator` |
| 2 | [Scan Secrets in Commit](#2-scan-secrets-in-commit) | `scan-secrets` |
| 3 | [Solution Validations](#3-solution-validations) | `SolutionValidations` |
| 4 | [Validate Classic App Insights](#4-validate-classic-app-insights) | `validateClassicAppInsights` |
| 5 | [Validate Hyperlinks in Pull Request](#5-validate-hyperlinks-in-pr) | `validate-pr-links` |
| 6 | [Validate Parameter Fields Type](#6-validate-parameter-fields-type) | `validate-field-types` |
| 7 | [Workbook Metadata Validations](#7-workbook-metadata-validations) | `WorkbooksValidations` |
| 8 | [Workbook Template Validations](#8-workbook-template-validations) | `WorkbooksTemplateValidations` |
| 9 | [YAML File Syntax Validation](#9-yaml-file-syntax-validation) | `YamlFileValidation` |

---

## Quick-Fix Decision Tree

| Error Pattern | Go To |
|---|---|
| `Email must be sanitized` | [Sample Data Validation — Errors 1–3](#error-1--email-not-sanitized) |
| `Found verified result` (secret) | [Scan Secrets — Errors 1–5](#error-1--active-secret-found) |
| `Invalid domain` / `No support obj` | [Solution Validations — Errors 3–11](#error-3--no-valid-domain) |
| `WorkspaceResourceId` missing | [Classic App Insights — Errors 1–3](#error-1--missing-workspaceresourceid) |
| URL `Invalid URL` / 404 | [Hyperlinks — Errors 1–2](#error-1--url-returns-http-404) |
| `securestring` parameter error | [Parameter Fields Type — Errors 1–3](#error-1--sensitive-global-parameter-not-securestring) |
| WorkbooksMetadata schema error | [Workbook Metadata Validations](#7-workbook-metadata-validations) |
| `sentinel-UserWorkbook` or hardcoded GUID | [Workbook Template — Errors 1–2](#error-1--default-fromtemplateid-value) |
| `bad indentation` / YAML syntax | [YAML File Syntax Validation](#9-yaml-file-syntax-validation) |

> **Infrastructure failures** (npm/tsc errors, PSGallery failures): These are **not your code's fault** — just click **"Re-run failed jobs"** in GitHub Actions.

---

## 1. Sample Data Validation

**GitHub Job:** `sampleDataValidator`  
**Script:** `.script/sampleDataValidator.js`

### What It Checks

Validates that sample data JSON files under `"Sample Data"` folders do **not** contain real or personally identifiable information (PII) — specifically real email addresses.

**Rules enforced:**
- All email addresses must be exactly `"sanitized@sanitized.com"` (case-sensitive)
- The JSON file must be structured as a **top-level array** `[ ... ]`
- Only `.json` files under `"Sample Data"` folders that are **Added** or **Modified** are checked

> **Important:** The validator stringifies the **entire** JSON and regex-matches ALL email patterns — not just dedicated email fields.

---

### Error 1 — Email Not Sanitized

**Error Message:**
```
Email must be sanitized@sanitized.com
```

**Resolution:** Replace ALL real email addresses with `"sanitized@sanitized.com"`. Search for `@` in the file to find all email-like patterns.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"userName": "attacker@evil.com"` | `"userName": "sanitized@sanitized.com"` |
| `"entity_id": "john.doe@contoso.com"` | `"entity_id": "sanitized@sanitized.com"` |
| `"message": "Alert sent to admin@company.org"` | `"message": "Alert sent to sanitized@sanitized.com"` |
| `"Sanitized@Sanitized.com"` ← wrong case! | `"sanitized@sanitized.com"` ← must be lowercase |

---

### Error 2 — Data Not an Array

**Error Message:**
```
Sample data file data must be in the form of array.
```

**Resolution:** Wrap your JSON data in an array `[ ... ]`.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `{ "event": "login", "user": "test" }` | `[{ "event": "login", "user": "test" }]` |
| `"just a string"` | `[{ "event": "login" }]` |
| `42` | `[{ "event": "login" }]` |

---

### Error 3 — Email Hidden in String Values

**Error Message:**
```
Email must be sanitized@sanitized.com
```

**Resolution:** The validator scans the **entire** stringified JSON — not just explicit email fields. Search for `@` everywhere.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"description": "Sent alert to admin@contoso.com at 3pm"` | `"description": "Sent alert to sanitized@sanitized.com at 3pm"` |
| `"rawLog": "From: user@domain.com To: victim@target.org"` | `"rawLog": "From: sanitized@sanitized.com To: sanitized@sanitized.com"` |

---

### Error 4 — Invalid JSON Syntax

**Error Message:**
```
Sample Data Validation Failed. File path: <path>. Error message: <JSON parse error>
```

**Resolution:** Fix JSON syntax errors using a linter (VS Code built-in JSON validation or [jsonlint.com](https://jsonlint.com)).

| ❌ BAD |
|--------|
| `[{"event": "login", "user": "test",}]` ← trailing comma |
| Missing closing bracket, unescaped quotes |

---

### Error 5 — Infrastructure Failure

**Error Message:**
```
npm ERR! code ERESOLVE
error TS2307: Cannot find module './utils/changedFilesValidator.js'
```

> **This is NOT your fault.** Click **"Re-run failed jobs"** in GitHub Actions.

---

### Error 6 — Summary Error

**Error Message:**
```
An error occurred, please open an issue
```

> **This is a summary.** Scroll UP in the job log for the specific error. Look for:  
> `Sample Data Validation Failed. File path: <path>. Error message: <specific error>`

---

### Email Detection Regex

```
/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/gi
```

Every match that is **not exactly** `sanitized@sanitized.com` causes failure. The comparison is **case-sensitive**.

### Best Practice

> Before committing sample data, sanitize ALL PII (emails, usernames, IPs, hostnames). Search for `@` and replace every real email with `sanitized@sanitized.com`.

---

## 2. Scan Secrets in Commit

**GitHub Job:** `scan-secrets`  
**Tool:** TruffleHog (`trufflesecurity/trufflehog@main`)

### What It Checks

Scans the git diff between the Pull Request base commit and the Pull Request head for **verified (live/active)** secrets or credentials. Only secrets confirmed live by TruffleHog's verification engine will block the Pull Request. Inactive, revoked, or pattern-only matches will **NOT** block.

**Exclusions:** File paths listed in `.script/SecretScanning/Excludepathlist`

---

### Error 1 — Active Secret Found

**Error Message:**
```
Found verified result
Detector Type: <type>
File: <path>
```

**Resolution:**
1. **Immediately revoke/rotate** the exposed credential at its source (AWS IAM, Azure Portal, GitHub Settings → Tokens).
2. Remove or replace the secret in code with an environment variable reference, Key Vault link, or placeholder.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"aws_secret_access_key": "active_aws_secret_access_key"` | `"aws_secret_access_key": "<your-secret-access-key>"` |
| `"api_key": "active_api_key"` | `"api_key": "<your-api-key>"` |

---

### Error 2 — Secret in an Earlier Commit

**Error Message:**
```
Found verified result
Commit: <sha> (an earlier commit in the Pull Request, not HEAD)
```

**Resolution:** TruffleHog scans **ALL commits** in the Pull Request — even if you removed the secret in a later commit, the original commit is still flagged.

Use `git rebase -i` to squash or amend the offending commit, removing the secret from history entirely. Then force-push the cleaned branch.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| Simply removing the secret in a later commit | Use `git rebase -i` to erase it from history |

---

### Error 3 — Sample/Test File with Verifiable Key

**Error Message:**
```
Found verified result
Detector Type: AWS
File: Playbooks/sample-connector/...
```

**Resolution:** Add the file path to `.script/SecretScanning/Excludepathlist` to suppress future scans. Or replace the value with a non-functional placeholder like `<aws-access-key-id>`.

---

### Error 4 — Private Key File Committed

**Error Message:**
```
Found verified result
Detector Type: PrivateKey
File: certs/server.key
```

**Resolution:**
- Remove the private key file from the Pull Request
- Add `*.key`, `*.pem` patterns to `.gitignore`
- If the key was for a real service, **regenerate** the certificate/key pair immediately.

---

### Error 5 — Secret in URL, Comment, or Docs

**Error Message:**
```
Found verified result
Detector Type: GitHub
File: docs/setup-guide.md
```

**Resolution:** TruffleHog scans ALL text content — including URLs, comments, and markdown docs. Remove the token and use SSH cloning or instruct users to configure their own credentials.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `git clone https://tfh_ERTGsamplelivetoken4@github.com/org/repo.git` | `git clone git@github.com:org/repo.git` |
| `# API key for testing: Active_API_key` | Use environment variables or Key Vault |

---

### Error 6 — Exit Code 183

> **Exit code 183 is TruffleHog's "secrets found" exit code.** Scroll UP in the log for the "Found verified result" block(s) with Detector Type, File, and Line details.

---

### Error 7 — Base and HEAD Are the Same

**Error Message:**
```
BASE and HEAD commits are the same. TruffleHog won't scan anything
```

**Resolution:** Ensure your Pull Request branch has at least one commit ahead of master.

---

### Error 8 — Insufficient Fetch-Depth (`fatal: bad object`)

**Error Message:**
```
fatal: bad object <sha>
```

**Resolution:** The `fetch-depth: 10` was insufficient to include the base commit. This happens with very long-lived branches or force-pushed histories. Rebase your branch onto the latest master to reduce the commit distance.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| Branch with 50+ commits ahead of master (exceeds `fetch-depth: 10`) | `git rebase origin/master && git push --force` |

---

### Error 9 — Infrastructure Failure

**Error Message:**
```
Error: Unable to pull image ghcr.io/trufflesecurity/trufflehog:latest
OR
Error: Process completed with exit code 1.
```

> **This is NOT your fault.** Click **"Re-run failed jobs"**. Check [GitHub Status](https://www.githubstatus.com/) for ongoing incidents. If persistent, open an issue — the workflow may need to pin a specific TruffleHog version instead of `@main`.

---

### Commonly Detected Secret Types

| Detector Type | Example Pattern | Description |
|---|---|---|
| AWS | `AKIA...` | AWS Access Key ID + Secret Access Key |
| Azure | Subscription keys, client secrets | Azure AD / Cognitive Services / Storage keys |
| GitHub | `ghp_...` / `github_pat_...` | GitHub Personal Access Tokens |
| Slack | `xoxb-...` / `xoxp-...` | Slack Bot or User OAuth Tokens |
| SendGrid | `SG....` | SendGrid API Keys |
| PrivateKey | `-----BEGIN RSA PRIVATE KEY-----` | RSA / EC / DSA / PGP private keys |
| Generic | `password=...` / `secret=...` | High-entropy strings matching known patterns |
| JWT | `eyJ...` | JSON Web Tokens (if verifiable) |

---

## 3. Solution Validations

**GitHub Job:** `SolutionValidations`  
**Script:** `.script/SolutionValidations/`

### What It Checks

Validates that modified or newly added JSON files under `Solutions/` conform to Microsoft Sentinel content marketplace standards. Runs **four sub-validations**:

1. **Domains & Verticals** — solution declares at least one valid domain
2. **Support Object** — metadata includes a properly structured support object
3. **Microsoft Sentinel Branding** — product referred to correctly
4. **Solution ID** — follows `publisherID.offerID` format (lowercase)

> Only `.json` files under `Solutions/` that are **Added** or **Modified** are checked.

---

### Error 1 — Missing `resources` Array

**Error Message:**
```
There are no resources in the file. File path: <path>
```

**Resolution:** Add a top-level `"resources"` array to `mainTemplate.json`.


E.g.: 
```json
{"$schema": "...", "resources": [...], "parameters": {...}}
```

---

### Error 2 — No Metadata Resources

**Error Message:**
```
There are no metadata resources found in the file. File path: <path>
```

**Resolution:** Add a resource of type `Microsoft.OperationalInsights/workspaces/providers/metadata` or `Microsoft.OperationalInsights/workspaces/providers/contentPackages`.

```json
"resources": [
  {
    "type": "Microsoft.OperationalInsights/workspaces/providers/metadata",
    ...
  }
]
```

---

### Error 3 — No Valid Domain

**Error Message:**
```
The solution must include at least one valid domain. Please provide a domain in the 'domains' field of the 'categories' object.
```

**Resolution:** Add at least one valid domain from the approved list to the `categories.domains` array.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"categories": {}` ← no domains field | `"categories": {"domains": ["Application"]}` |
| `"categories": {"domains": []}` ← empty array | `"categories": {"domains": ["Security - Threat Protection", "Identity"]}` |

- [Official Microsoft Docs — Solution Categories](https://learn.microsoft.com/en-us/azure/sentinel/sentinel-solutions#categories-for-microsoft-sentinel-out-of-the-box-content-and-solutions)
- [Repo source of truth](https://github.com/Azure/Azure-Sentinel/blob/master/.script/SolutionValidations/ValidDomainsVerticals.json)

---

### Error 4 — Invalid Domain Value

**Error Message:**
```
Invalid domains: [<list>] provided.
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"domains": ["InvalidDomain"]` ← not in approved list | `"domains": ["Security - Threat Protection"]` |
| `"domains": ["security - threat protection"]` ← wrong case | `"domains": ["Application", "Identity"]` |

---

### Error 5 — Invalid Vertical Value

**Error Message:**
```
Invalid verticals: [<list>] provided.
```

**Resolution:** If provided, verticals must be from the approved list (case-sensitive): `Aeronautics`, `Education`, `Finance`, `Healthcare`, `Manufacturing`, `Retail`. Empty `[]` is valid — verticals are optional.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"verticals": ["Banking"]` ← not in approved list | `"verticals": ["Finance"]` |
| `"verticals": ["finance"]` ← wrong case | `"verticals": []` ← empty is valid |

---

### Error 6 — Missing `support` Object

**Error Message:**
```
The "properties" field must have "support" field.
```

**Resolution:** Add a `"support"` object to `SolutionMetadata.json`. Then **repackage** using `createSolutionV3.ps1` — **do NOT manually edit `mainTemplate.json`**.

```json
"properties": {
  "categories": { ... },
  "support": {
    "name": "Contoso Inc.",
    "tier": "Partner",
    "email": "support@contoso.com"
  }
}
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"properties": {"categories": {...}}` ← no support field | Add `"support": {"name": "...", "tier": "...", "email": "..."}` |

---

### Error 7 — Missing `name` in Support Object

**Error Message:**
```
The support object must have a "name" field.
```

**Resolution:** Add a `"name"` field to the `"support"` object in `SolutionMetadata.json`. Then repackage using `createSolutionV3.ps1`.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"support": {"tier": "Partner"}` ← missing name | `"support": {"name": "Contoso Inc.", "tier": "Partner", "email": "support@contoso.com"}` |

---

### Error 8 — Empty Support `name`

**Error Message:**
```
The support object "name" field value cannot be empty.
```

**Resolution:** Provide a non-empty, non-whitespace string for `"name"` in the `"support"` object.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"name": ""` ← empty string | `"name": "Microsoft"` |
| `"name": "   "` ← whitespace only | `"name": "Contoso Inc."` |

---

### Error 9 — Missing `tier` in Support Object

**Error Message:**
```
The support object must have a "tier" field.
```

**Resolution:** Add a `"tier"` field. Valid values: `"Microsoft"`, `"Partner"`, `"Community"` (case-sensitive).

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"support": {"name": "Contoso"}` ← missing tier | `"support": {"name": "Contoso", "tier": "Partner"}` |

---

### Error 10 — Invalid Support `tier`

**Error Message:**
```
Invalid value for the support "tier" field. Supported values are: Microsoft, Partner, Community.
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"tier": "microsoft"` ← wrong case | `"tier": "Microsoft"` |
| `"tier": "partner"` ← wrong case | `"tier": "Partner"` |
| `"tier": "Enterprise"` ← not a valid value | `"tier": "Community"` |

---

### Error 11 — Missing `email` or `link` in Support Object

**Error Message:**
```
The support object must have either "email" or "link" field and the value should not be empty.
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `{"name": "Contoso", "tier": "Partner"}` ← no email or link | `{..., "email": "support@contoso.com"}` |
| `{..., "email": ""}` ← empty email | `{..., "link": "https://contoso.com/support"}` |

---

### Error 12 — Invalid Email Format

**Error Message:**
```
Invalid email format for support email: <value>
```

**Resolution:** Provide a valid email address matching the format `user@domain.tld` in the `"support"` object of `SolutionMetadata.json`. Then repackage using `createSolutionV3.ps1`.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"email": "not-an-email"` | `"email": "support@contoso.com"` |
| `"email": "support@"` ← missing domain | `"email": "team@company.org"` |

---

### Error 13 — Invalid URL Format for Support Link

**Error Message:**
```
Invalid url format for support link: <value>
```

**Resolution:** Provide a valid URL starting with `http://` or `https://` in the `"support"` object of `SolutionMetadata.json`. Then repackage using `createSolutionV3.ps1`.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"link": "www.contoso.com/support"` ← missing protocol | `"link": "https://contoso.com/support"` |
| `"link": "ftp://contoso.com"` ← wrong protocol | `"link": "http://support.company.com"` |

---

### Error 14 — Incorrect Branding

**Error Message:**
```
Inaccurate product branding used in '<attribute>' for '<value>'. Use "Microsoft Sentinel" instead of "Sentinel" or "Azure Sentinel".
```

**Resolution:** Replace standalone `"Sentinel"` or `"Azure Sentinel"` with `"Microsoft Sentinel"` in source content files (analytic rules YAML, data connector JSON, workbook JSON, etc.) — **not** in `mainTemplate.json` directly. Then repackage.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"description": "This solution provides Sentinel analytics rules."` | `"description": "This solution provides Microsoft Sentinel analytics rules."` |
| `"text": "Connect your Azure Sentinel workspace..."` | `"text": "Connect your Microsoft Sentinel workspace..."` |

---

### Error 15 — Missing `solutionId`

**Error Message:**
```
Missing 'solutionId' attribute in the file. File path: <path>
```

**Resolution:** Add a `"solutionId"` key in `SolutionMetadata.json` in the format `publisherid.offerid` (all lowercase, dot-separated). Then repackage using `createSolutionV3.ps1`.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"variables": {"workspaceName": "..."}` ← no solutionId | `"variables": {"solutionId": "publisherid.offerid", ...}` |

---

### Error 16 — Empty Solution ID

**Error Message:**
```
Empty solution ID. Expected format: publisherID.offerID. and it must be in lowercase. Found empty value.
```

**Resolution:** Provide a non-empty value for `solutionId` in `SolutionMetadata.json` in the format `publisherid.offerid` (all lowercase, dot-separated). Then repackage using `createSolutionV3.ps1`.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"solutionId": ""` ← empty | `"solutionId": "contoso.threathunting"` |

---

### Error 17 — Invalid Solution ID Format

**Error Message:**
```
Invalid solution ID format. Expected format: publisherID.offerID. and it must be in lowercase. Found: <value>
```

**Rules:**
- Exactly two parts separated by a single dot
- Entirely **lowercase**
- No uppercase letters, no extra dots, no spaces

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"ContosoThreatHunting"` ← no dot separator | `"contoso.threathunting"` |
| `"Contoso.ThreatHunting"` ← uppercase | `"contoso.mysolution"` |
| `"contoso.threat.hunting"` ← too many dots | |

---

### Error 18 — Infrastructure Failure

**Error Message:**
```
npm ERR! code ERESOLVE
OR
error TS2307: Cannot find module '../utils/changedFilesValidator.js'
```

> **npm/tsc errors are not your fault.** Click **"Re-run failed jobs"**.

---

## 4. Validate Classic App Insights

**GitHub Job:** `validateClassicAppInsights`  
**Script:** `.script/package-automation/validateClassicAppInsights.ps1`

### What It Checks

Validates that **newly added** ARM templates (`azuredeploy*.json`) under `Solutions/` and `DataConnectors/` directories do **not** use Classic Application Insights (retired **29 Feb 2024**).

**Rule:** Every `Microsoft.Insights/components` resource **MUST** include `WorkspaceResourceId` in its `properties` object.

> Only **newly added** files are checked (not modified or deleted).

---

### Error 1 — Missing `WorkspaceResourceId`

**Error Message:**
```
::error:: Please add property 'WorkspaceResourceId' for 'Microsoft.Insights/components' type in below given file(s)!
::error:: --> <filePath>
```

**Resolution:** Add `WorkspaceResourceId` to the `properties` object of every `Microsoft.Insights/components` resource:

```json
"properties": {
  "Application_Type": "web",
  "WorkspaceResourceId": "[resourceId('Microsoft.OperationalInsights/workspaces', variables('workspaceName'))]",
  "publicNetworkAccessForIngestion": "Enabled",
  "publicNetworkAccessForQuery": "Enabled"
}
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"properties": {"Application_Type": "web"}` | `"properties": {"Application_Type": "web", "WorkspaceResourceId": "[resourceId(...)]"}` |
| `WorkspaceResourceId` placed outside `"properties"` | `WorkspaceResourceId` as direct child of `"properties"` |

---

### Error 2 — Multiple Resources, Some Missing `WorkspaceResourceId`

**Resolution:** If a template has multiple `Microsoft.Insights/components` resources, **every one** of them must have `WorkspaceResourceId`. If ANY is missing, the entire file is flagged.

---

### Error 3 — `WorkspaceResourceId` at Wrong Nesting Level

**Resolution:** The property must be a **direct child** of `"properties"` at the same level as `Application_Type`.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"WorkspaceResourceId"` at resource root level | `"properties": {"WorkspaceResourceId": "..."}` |
| `"properties": {"configuration": {"WorkspaceResourceId": "..."}}` | `"properties": {"WorkspaceResourceId": "..."}` |

---

### Error 4 — Invalid JSON

**Error Message:**
```
Error Occured in validateClassicAppInsights script. Error Details: ConvertFrom-Json: Invalid JSON primitive: ...
```

**Resolution:** Fix JSON syntax errors (trailing commas, missing brackets, unescaped characters) using VS Code or [jsonlint.com](https://jsonlint.com).

| ❌ BAD |
|--------|
| Trailing comma: `"WorkspaceResourceId": "[resourceId(...)]",` ← inside `"properties"` |
| Missing closing bracket, unescaped quotes |

---

### Error 5 — File Read Error (`ReadFileContent` failure)

**Error Message:**
```
Error occurred in ReadFileContent. Error details: <message>
```

**Resolution:** The script could not read or access a file on disk. This is typically an infrastructure issue (file path resolution, permission, or disk error). Re-run the workflow. If persistent, verify the file path is correct and the file exists in the Pull Request branch.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| File path contains special characters the runner cannot resolve | Use standard characters in file paths; re-run the workflow |

---

### Error 6 — Infrastructure / Runner Failure

**Error Message:**
```
Install-Module: Unable to resolve package source 'PSGallery'
OR
Error: Process completed with exit code 1.
```

> **This is NOT your fault.** The job installs the `powershell-yaml` module, and if module installation fails, the runner has connectivity issues, or the GitHub App token generation fails, the job errors out before validation runs.

**Resolution:** Click **"Re-run failed jobs"** in GitHub Actions. Check [GitHub Status](https://www.githubstatus.com/) for ongoing incidents.

---

### Error 7 — Unhandled Script Exception

**Error Message:**
```
Error Occured in validateClassicAppInsights script. Error Details: <message>
```

**Resolution:** An unhandled exception occurred during script execution. The job exits with code 1. Check the full log output for the specific error message.

| Cause | Fix |
|-------|-----|
| Malformed JSON | Fix ARM template syntax (see Error 4) |
| Infrastructure / module install failure | Re-run the workflow (see Error 6) |
| Git history issues | Ensure branch is properly rebased on master |

---

### Important Note

> Classic Application Insights was **retired on 29 February 2024**. All new App Insights resources must be workspace-based.  
> See: [Convert Classic App Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/convert-classic-resource)

---

## 5. Validate Hyperlinks in Pull Request

**GitHub Job:** `validate-pr-links`  
**Script:** `.script/package-automation/hyperlink-validation.ps1`

### What It Checks

Validates that all HTTP/HTTPS URLs in modified/added files under `Solutions/` are reachable (20-second timeout).

**Build FAILS for:** HTTP 404 or HTTP 500 responses  
**Warnings only (build still passes):** Timeouts

---

### Excluded File Extensions

`.py`, `.png`, `.jpg`, `.jpeg`, `.conf`, `.svg`, `.html`, `.ps1`, `.psd1`, `.xml`, `.zip`, `.md`, `requirements.txt`, `host.json`, `proxies.json`, `function.json`

---

### Error 1 — URL Returns HTTP 404

**Error Message:**
```
<url> : Invalid URL
```

**Resolution:** Update the URL to point to the current/correct location or remove the broken link.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"https://docs.example.com/removed-page"` | Update to current URL or remove |
| `"https://api.example.com/deprecated-endpoint"` | Update to working endpoint |

---

### Error 2 — URL Returns HTTP 500

**Resolution:** First re-run the workflow (may be transient). If persistent, verify the URL and update or remove it.

---

### Error 3 — URL Timeout (WARNING only)

**Error Message:**
```
<url> : Timeout(Warning)
```

> This does **NOT** fail the build. Verify the URL manually in a browser. No action required if the URL is genuinely valid but slow.

---

### Error 4 — Rate Limiting (Multiple URL Failures)

**Resolution:** When multiple URLs from the same domain fail together, the server is likely rate-limiting the CI runner. Re-run the workflow — rate limiting is often transient.

> **Tip:** Consider using defanged URLs (`hxxps://`) in sample data to prevent the hyperlink validator from checking them.

---

### Error 5 — Infrastructure Failure

> **Not your code's fault.** Click **"Re-run failed jobs"**.

---

### Excluded Domains Reference

These domains are **always skipped** (not validated):

| Domain | Reason |
|--------|--------|
| `github.com` | Rate-limits CI runners aggressively |
| `schema.management.azure.com` | ARM schema endpoints (always valid) |
| `schemas.microsoft.com` | Microsoft schema definitions |
| `twitter.com` | Blocks automated requests |
| `s-platform.api.opendns.com` | API endpoint requiring auth |
| `azure.microsoft.com` | Microsoft docs (high availability) |
| `sts.windows.net` | Azure AD STS (auth endpoint) |
| `oauth2.googleapis.com` | Google OAuth (requires auth) |
| `monitoring.googleapis.com` | Google Cloud Monitoring API |
| `api2.eu.prismacloud.io` | Prisma Cloud API (requires auth) |
| `api.lookout.com` | Lookout API (requires auth) |
| `accounts.google.com` | Google accounts (auth pages) |

### Key Behavior

> ⚠️ **Only HTTP 404 and HTTP 500 fail the build.** Timeouts are warnings only. One bad URL fails the entire build regardless of how many other URLs pass.

---

## 6. Validate Parameter Fields Type

**GitHub Job:** `validate-field-types`  
**Script:** `.script/package-automation/validateFieldTypes.ps1`

### What It Checks

Validates that sensitive parameters in `Solutions` package `mainTemplate.json` files use **secure types**.

**Two rules:**
1. **Global-level** parameters with sensitive name patterns → must be `"securestring"`
2. **All parameters** inside `ResourcesDataConnector` content templates → must be `"securestring"`, `"object"`, or `"array"`

> Only triggers on PRs modifying `**/Package/mainTemplate.json` targeting master.

---

### Sensitive Keyword Patterns (Global Level)

| Pattern | Example Parameter Names |
|---------|------------------------|
| `*Password*` | `workspacePassword`, `adminPassword` |
| `*ClientSecret*` | `oauthClientSecret`, `aadClientSecretValue` |
| `*Authorization*` | `authorizationKey`, `customAuthorization` |
| `*AuthorizationCode*` | `oauthAuthorizationCode` |
| `*Secret*` | `apiSecret`, `clientSecretValue` |
| `*token*` | `accessToken`, `refreshTokenValue` |
| `*apptoken*` | `customAppToken` |
| `*appkey*` | `applicationAppKey`, `apiAppKey` |

---

### Error 1 — Sensitive Global Parameter Not `securestring`

**Error Message:**
```
Invalid global level parameters field(s) type. Please update the 'type' value for below given list to 'securestring'
--> <paramName>
```

**Resolution:** Change the parameter type to `"securestring"` for any top-level parameter matching a sensitive pattern:

```json
"parameters": {
  "workspacePassword": {
    "type": "securestring",
    "metadata": { "description": "The workspace password" }
  }
}
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"workspacePassword": {"type": "string"}` | `"workspacePassword": {"type": "securestring"}` |
| `"apiClientSecret": {"type": "string"}` | `"apiClientSecret": {"type": "securestring"}` |
| `"accessToken": {"type": "string"}` | `"accessToken": {"type": "securestring"}` |

---

### Error 2 — Invalid Resource-Level Parameter Type

**Error Message:**
```
Invalid resource level parameters field(s) type. Please update the 'type' value for below given list to 'securestring', 'object' or 'array'.
--> <paramName>
```

**Resolution:** ALL parameters inside `ResourcesDataConnector` content templates must use `"securestring"`, `"object"`, or `"array"`:

```json
"resources": [{
  "type": "Microsoft.OperationalInsights/workspaces/providers/contentTemplates",
  "properties": {
    "contentKind": "ResourcesDataConnector",
    "mainTemplate": {
      "parameters": {
        "connectorApiKey": { "type": "securestring" },
        "workspaceId": { "type": "securestring" }
      }
    }
  }
}]
```

---

### Error 3 — Non-Sensitive Resource Parameters Also Flagged

> This is **strict** — even `workspaceId`, `subscriptionId`, `location` inside `ResourcesDataConnector` must be `"securestring"`, `"object"`, or `"array"`. This is a repository security requirement.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"workspaceId": {"type": "string"}` | `"workspaceId": {"type": "securestring"}` |
| `"subscriptionId": {"type": "string"}` | `"subscriptionId": {"type": "securestring"}` |
| `"location": {"type": "string"}` | `"location": {"type": "securestring"}` or wrap in `"object"` |

---

### Error 4 — Invalid JSON

**Resolution:** Fix JSON syntax errors (trailing commas, BOM characters, unescaped quotes) using VS Code or [jsonlint.com](https://jsonlint.com).

---

### Error 5 — Informational Skip (Exit 0)

**Error Message:**
```
Skipping validation as there is no change in maintemplate.json file for solution <name>
```

> **This is informational, NOT an error.** No action required.

---

### Error 6 — Infrastructure Failure

**Error Message:**
```
Error occurred in validateFieldTypes file. Error Details: ...
OR
Install-Module: Unable to resolve package source 'PSGallery'
```

> **This is NOT your fault.** The job installs the `powershell-yaml` module and generates a GitHub App token. If module installation fails, token generation fails, or the runner has network issues, the job errors out before validation begins.

**Resolution:** Click **"Re-run failed jobs"** in GitHub Actions. Check [GitHub Status](https://www.githubstatus.com/) for ongoing incidents.

---

## 7. Workbook Metadata Validations

**GitHub Job:** `WorkbooksValidations`  
**Script:** `.script/workbooksMetadataValidator.js`

### What It Checks

Validates modifications to `Workbooks/WorkbooksMetadata.json`. Runs **six sub-validators**:

1. JSON Schema validation
2. Unique workbook keys
3. Preview image file names
4. Logo image file existence
5. Preview image file existence
6. Version increment on modification

---

### Required Metadata Fields

Each entry in `WorkbooksMetadata.json` must include:

| Field | Type | Description |
|-------|------|-------------|
| `workbookKey` | string | Unique identifier |
| `logoFileName` | string | Must exist in `Workbooks/Images/Logos/` |
| `description` | string | Workbook description |
| `dataTypesDependencies` | array\<string\> | Non-empty strings only |
| `dataConnectorsDependencies` | array\<string\> | Non-empty strings |
| `previewImagesFileNames` | array\<string\> | `.png`, theme keyword, must exist |
| `version` | string | Must increment on template modification |
| `title` | string | Workbook title |
| `templateRelativePath` | string | Relative path to workbook JSON file |
| `subtitle` | string | Workbook subtitle |
| `provider` | string | Workbook provider/publisher |

> The schema uses `additionalProperties: false` — **no extra fields allowed**.

---

### 1. JSON Schema Errors

**Error 1 — Missing Required Property**

```
Invalid Schema. Validation errors: instance[<n>] requires property "<field>"
```

**Resolution:** Add the missing field to the metadata entry at the indicated index.

---

**Error 2 — Additional Property Not Allowed**

```
Invalid Schema. Validation errors: instance[<n>] additionalProperty "<field>" exists in instance when not allowed
```

**Resolution:** Remove the unrecognized field. Check for typos (`"tilte"` instead of `"title"`).

---

**Error 3 — Empty String in `dataTypesDependencies`**

```
instance[<n>].dataTypesDependencies[<m>] does not meet minimum length of 1
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"dataTypesDependencies": ["SecurityEvent", ""]` | `"dataTypesDependencies": ["SecurityEvent"]` |

---

**Error 4 — Wrong Field Type**

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"dataTypesDependencies": "SecurityEvent"` | `"dataTypesDependencies": ["SecurityEvent"]` |
| `"version": 1.0` | `"version": "1.0.0"` |

---

### 2. Unique Workbook Keys

**Error 5 — Duplicate `workbookKey`**

```
WorkbooksMetadata keys must be unique. Remove any duplicate keys.
```

**Resolution:** Rename one of the duplicates to a unique identifier.

---

### 3. Preview Image File Name Errors

**Error 6 — Not `.png` Files**

```
Invalid Preview Images for workbook <key>. All preview images must be png files
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `["MyWorkbookBlack.jpg", "MyWorkbookWhite.svg"]` | `["MyWorkbookBlack.png", "MyWorkbookWhite.png"]` |

---

**Error 7 — Missing Theme Keyword**

```
All preview image file names must include either "Black", "Dark", "White" or "Light"
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `["MyWorkbook1.png", "MyWorkbook2.png"]` | `["MyWorkbookBlack.png", "MyWorkbookWhite.png"]` |

---

**Error 8 — Missing Dark or Light Theme Variant**

```
Preview images must contain at least one white or light background image and one black or dark background image.
```

**Resolution:** Include both a dark-themed (`Black` or `Dark`) AND a light-themed (`White` or `Light`) image.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `["MyWorkbookWhite.png", "MyWorkbookLight.png"]` ← no dark! | `["MyWorkbookBlack.png", "MyWorkbookWhite.png"]` |

---

### 4. Image File Existence Errors

**Error 9 — Logo File Not Found**

```
Can't locate logo image file <filename> under the Workbooks/Images/Logos directory
```

**Resolution:** Add the logo file to `Workbooks/Images/Logos/` or fix the `logoFileName` to match an existing file.

---

**Error 10 — Preview Image File Not Found**

```
Can't locate preview image file <filename> under the Workbooks/Images/Preview directory
```

**Resolution:** Add the preview image to `Workbooks/Images/Preview/` or fix the file name.

---

### 5. Version Increment Errors

**Error 11 — Version Not Incremented**

```
The workbook <path> has been modified but the version has not been incremented
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"version": "1.0.0"` (same as before Pull Request) | `"version": "1.1.0"` (incremented) |

---

**Error 12 — New Version Not Greater Than Old**

| ❌ BAD | ✅ GOOD |
|--------|---------|
| Old: `"1.2.0"` → New: `"1.1.0"` | Old: `"1.2.0"` → New: `"1.3.0"` |
| Old: `"2.0.0"` → New: `"1.9.9"` | Old: `"1.0.0"` → New: `"1.0.1"` |

---

## 8. Workbook Template Validations

**GitHub Job:** `WorkbooksTemplateValidations`  
**Script:** `.script/workbooksTemplateValidator.js`

### What It Checks

Validates workbook template JSON files under `Workbooks/` and `Solutions/`. Only files matching both conditions are checked:
- `$schema` contains `"schema/workbook.json"` AND
- `version` equals `"Notebook/1.0"`

---

### Error 1 — Default `fromTemplateId` Value

**Error Message:**
```
Value for "fromTemplateId" must be other than "sentinel-UserWorkbook".
```

**Resolution:** Replace the default portal value with a unique, descriptive identifier for your workbook:

```json
"fromTemplateId": "AzureSentinel-NetworkOverview-v1"
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `"fromTemplateId": "sentinel-UserWorkbook"` | `"fromTemplateId": "AzureSentinel-NetworkOverview-v1"` |
| `"fromTemplateId": ""` | `"fromTemplateId": "MyCompany-ThreatHunting-abc123"` |

> `"sentinel-UserWorkbook"` is the default assigned by the Azure portal when creating a new workbook. Always replace it before submitting.

---

### Error 2 — Hardcoded Azure Resource Path

**Error Message:**
```
Contains info of a resource at offset <n>. A workbook template must not contain any references to resources.
```

**Resolution:** The validator searches the raw file content for this pattern:
```
subscriptions/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/
```

Replace hardcoded subscription GUIDs with workbook resource parameters:

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `/subscriptions/a1b2c3d4-e5f6-7890-abcd-ef1234567890/resourceGroups/myRG/...` | `/subscriptions/{SubscriptionId}/resourceGroups/{ResourceGroup}/...` |
| `"resourceId": "subscriptions/12345678-ABCD-EF01-2345-6789ABCDEF01/..."` | Use `{Subscription:id}`, `{ResourceGroup:name}` parameters |

---

### Error 3 — Summary Error

**Error Message:**
```
An error occurred, please open an issue
```

> Scroll UP in the log for `WorkbooksTemplate Validation Failed. File path: <path>. Error message: <msg>`. Fix per Error 1 or Error 2.

---

### Error 4 — Hardcoded Resource in Non-Obvious Location

**Common locations where resource paths hide:**

| Location | Example |
|----------|---------|
| Query strings | `"resources \| where id == '/subscriptions/GUID/...'"` |
| Scope selectors | `"resourceId": "/subscriptions/GUID/resourceGroups/..."` |
| Link targets | `"linkTarget": "/subscriptions/GUID/providers/..."` |

Use the character offset from the error message to locate the exact position.

---

## 9. YAML File Syntax Validation

**GitHub Job:** `YamlFileValidation`  
**Script:** `.script/yamlFileValidator.js`

### What It Checks

Validates that all modified or newly added `.yaml`/`.yml` files in the Pull Request are **syntactically valid** YAML. Applies to ALL directories — no folder restriction.

> This checks YAML syntax only — not content semantics.

---

### Error 1 — Bad Indentation

**Error Message:**
```
Incorrect yaml file. File path: <path>. Error message: bad indentation of a mapping entry (<line>:<col>)
```

**Resolution:** Fix indentation at the indicated line. Use **spaces only** (never tabs), typically 2 spaces per level.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `severity: High` indented 6 spaces when siblings use 2 | `severity: High` at same level as sibling keys |

---

### Error 2 — Unexpected End of Stream

**Error Message:**
```
unexpected end of the stream within a ... (<line>:<col>)
```

**Resolution:** Close all open quotes, brackets, and braces.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `name: "Incomplete quote` ← unclosed | `name: "Incomplete quote"` |
| `tags: [detection, network` ← no closing `]` | `tags: [detection, network]` |

---

### Error 3 — Duplicate Mapping Key

**Error Message:**
```
duplicated mapping key (<line>:<col>)
```

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `severity: Medium` then `severity: High` again | Only one `severity` key |

---

### Error 4 — Cannot Read Block Mapping Entry

**Error Message:**
```
can not read a block mapping entry; a multiline key may not be an implicit key (<line>:<col>)
```

**Resolution:** Ensure every key has a colon and space after it (`key: value`).

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `name Suspicious Activity` ← missing `:` | `name: Suspicious Activity` |

---

### Error 5 — Incomplete Explicit Mapping Pair

**Error Message:**
```
incomplete explicit mapping pair; a key node is missed (<line>:<col>)
```

**Resolution:** Ensure every value has a corresponding key.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `metadata: {author: "Contoso", : "missing key"}` | `metadata: {author: "Contoso", version: "1.0"}` |

---

### Error 6 — Did Not Find Expected Character

**Resolution:** Check for unclosed quotes, brackets, or missing colons after keys.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `name: "My Rule` ← unclosed quote | `name: "My Rule"` |
| `tags: [detection, network` | `tags: [detection, network]` |

---

### Error 7 — Unknown Escape Sequence

**Error Message:**
```
unknown escape sequence (<line>:<col>)
```

**Resolution:** Use single quotes for strings with backslashes, or escape backslashes in double-quoted strings.

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `path: "C:\Users\admin\file.txt"` | `path: 'C:\Users\admin\file.txt'` |
| | `path: "C:\\Users\\admin\\file.txt"` |

---

### Error 8 — Tab Character for Indentation

**Error Message:**
```
found character \t that cannot start any token (<line>:<col>)
```

**Resolution:** YAML **strictly forbids tabs**. Replace all tabs with spaces. Use your editor's "Convert Indentation to Spaces" command.

---

### Error 9 — Summary Error

**Error Message:**
```
An error occurred, please open an issue
```

> Scroll UP in the log for `Incorrect yaml file. File path: <path>. Error message: <msg>`.

---

### Error 10 — Infrastructure Failure

> **Not your code's fault.** Click **"Re-run failed jobs"**.

---

### YAML Quick Reference

| Rule | Example |
|------|---------|
| Use spaces only, never tabs | `  key: value` (2 spaces) |
| Consistent indentation (2 spaces) | `parent:` → `  child: value` |
| Colon + space after keys | `name: My Rule` (space after `:`) |
| Quote strings with special chars | `"value: with colon"` |
| Unique keys within a mapping | No duplicate keys at same level |
| Close all quotes and brackets | `"complete"` `{key: val}` `[item]` |
| Block scalars for multi-line | `query: \|` then indented content |
| No trailing commas in flow style | `[a, b, c]` NOT `[a, b, c,]` |

---

## Common Patterns & Tips

### When to Repackage vs. Edit Directly

| Scenario | Action |
|----------|--------|
| Fixing `SolutionMetadata.json` fields (support, domains, solutionId) | Edit `SolutionMetadata.json`, then run `createSolutionV3.ps1` |
| Fixing branding in source content (YAML rules, workbook JSON) | Edit source files, then run `createSolutionV3.ps1` |
| Fixing `mainTemplate.json` parameter types | Edit `mainTemplate.json` directly (generated file) |
| Fixing workbook template `fromTemplateId` | Edit the workbook template `.json` directly |

> **Never manually edit `mainTemplate.json` for solution metadata** (support object, domains, solutionId, branding). Always fix the source (`SolutionMetadata.json` or content files) and repackage.

---

### Infrastructure vs. Content Failures

If you see any of these, **just re-run the workflow** — they are not caused by your changes:

```
npm ERR! code ERESOLVE
error TS2307: Cannot find module '...'
Install-Module: Unable to resolve package source 'PSGallery'
Error: Unable to pull image ghcr.io/trufflesecurity/trufflehog:latest
Error: Process completed with exit code 1
```

1. Go to the **Actions** tab in GitHub
2. Click on the failed workflow run
3. Click **"Re-run failed jobs"**
4. If the failure persists after 2–3 re-runs, open an issue in the repository

---

### File Scope Reference

| Validation | Files Checked | Filter |
|-----------|--------------|--------|
| Sample Data | `**/Sample Data/*.json` | Added + Modified |
| Scan Secrets | All files in Pull Request diff | All commits in Pull Request |
| Solution Validations | `Solutions/**/*.json` | Added + Modified |
| Classic App Insights | `Solutions/**/azuredeploy*.json`, `DataConnectors/**/azuredeploy*.json` | Added only |
| Hyperlinks | `Solutions/**/*` | Added + Modified (excluding certain extensions) |
| Parameter Fields | `**/Package/mainTemplate.json` | Modified |
| Workbook Metadata | `Workbooks/WorkbooksMetadata.json` | Modified only |
| Workbook Template | `Workbooks/**/*.json`, `Solutions/**/*.json` | Added + Modified |
| YAML Syntax | `**/*.yaml`, `**/*.yml` | Added + Modified |

---

*Last updated: August 2026*