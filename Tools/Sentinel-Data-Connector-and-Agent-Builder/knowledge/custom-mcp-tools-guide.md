# Custom MCP Tools — Cowork Knowledge Guide

> Companion to `knowledge/security-copilot-agent-guide.md`. This is the **single source of truth** for the Custom MCP Tools track of the Sentinel Data Connector and Agent Builder flow (Phase 1 branch B → Phase 5B → Phase 6B). When the developer chooses **"Custom MCP tools"** at the Phase 1 track-selection question, every artifact, terminology choice, validation gate, and chat turn in this guide governs the cowork.
>
> Reference implementation studied while authoring this guide (local checkout — **do not vendor**): `/Users/sai/Desktop/sentinel/code/Sentinel-MCP-Client/` (`sentinel_mcp_tools.py` for publishing semantics, `sentinel_mcp_client/headless_client.py` for the consumption JSON-RPC surface, `README.md` for the Entra app reg flow and permission model).

---

## 1. Track positioning

The agent has **two output formats** for an ISV:

| Track | Phase 5 output | Phase 6 output | Who calls it at runtime |
|---|---|---|---|
| Security Copilot Agent | `config/agent-instructions/<slug>.md` | `Package-Agent.ps1` zip | A human analyst chatting in `securitycopilot.microsoft.com` |
| **Custom MCP Tools** *(this guide)* | `config/mcp-tools/<slug>/tools.json` published to the Security Platform AI Primitives API | `config/mcp-tools/<slug>/deployment-guide.md` + `entra-app.json` | The ISV's own product agent — or a customer's custom agent — running unattended, calling the custom collection **alongside** the built-in collections (`data-exploration`, `triage`, `security-copilot-agent-creation`) |

Both tracks share Phases 0–4 (ISV identification, use-case ideation Q2+, data lake onboarding, DCE/DCR ingestion, MCP verification). Only **Phase 1 Q1**, **Phase 5**, and **Phase 6** diverge.

**Always call this "the consuming agent."** Never "headless client" / "headless_client". This rule is enforced by `scripts/Test-McpToolsManifest.ps1` and by a post-write grep in Phase 6B. See section 9.

---

## 2. Two identities, one collection (locked design)

There are **two distinct Entra identities** in this track. Conflating them is the #1 cause of 401/403s in early integrations.

### 2.1 Publisher identity — Phase 5B only

- **Who:** the ISV developer running the agent locally.
- **How they sign in:** `az login` (delegated user token).
- **What they can do:** PUT/GET/DELETE on `https://api.securityplatform.microsoft.com/aiprimitives/mcpToolCollections/{name}` and `…/tools/{toolName}`. Required Azure RBAC on the workspace: at least **Microsoft Sentinel Contributor** (so they can author tools that target it).
- **Lifetime:** publisher tokens are short-lived (~1h). The agent acquires a fresh token at the start of each Phase 5B publication burst via `az account get-access-token --resource 4500ebfb-89b6-4b14-a480-7f749797bfcd --query accessToken -o tsv` and reuses it for the collection PUT + per-tool PUTs + read-after-write `tools/list`.
- **Never used at runtime.** The publisher identity does **not** end up in the deployment guide and does **not** end up in `entra-app.json`.

### 2.2 Consumer identity — runtime (documented in Phase 6B)

The consuming agent runs unattended (no user in the loop), so it authenticates via **client_credentials** flow. However — and this is the trap — the Sentinel Platform Services API exposes its access scope as a **Delegated permission** (`SentinelPlatform.DelegatedAccess`, `type=Scope`), **not** an app role. There is no `Role`-shaped permission to grant.

The supported pattern is therefore:

1. The customer (or ISV) creates a single-tenant app registration with a client secret.
2. They add the Delegated permission **`SentinelPlatform.DelegatedAccess`** (`resourceAppId: 4500ebfb-89b6-4b14-a480-7f749797bfcd`) to the app.
3. **A tenant admin pre-consents** the Delegated permission (one-click in the portal, or via `az ad app permission admin-consent`). This grant survives forever and means no interactive prompt fires at runtime.
4. They assign **Microsoft Sentinel Reader** on the workspace to the app's service principal.
5. At runtime the consuming agent uses `ClientSecretCredential` (Azure Identity SDK) → token acquired via the OAuth 2.0 **client_credentials** flow → scope = `4500ebfb-89b6-4b14-a480-7f749797bfcd/.default`. Because admin pre-consent already covers the Delegated scope, the token is issued for the app itself with the granted privileges.
6. The agent sends the token to `https://sentinel.microsoft.com/mcp/custom/<collectionName>/` and to any built-in MCP collection URL.

Confirmation in the reference checkout: `sentinel_mcp_client/headless_client.py` builds tokens with `ClientSecretCredential(...).get_token("4500ebfb-89b6-4b14-a480-7f749797bfcd/.default")`, and `README.md` section "Entra App Registration for Headless Client" says **"add Delegated permission `SentinelPlatform.DelegatedAccess` → grant admin consent → assign Sentinel Reader on workspace."**

This is why `entra-app.json` (section 7.2 of the [Phase 6B section of `.github/copilot-instructions.md`](../.github/copilot-instructions.md#phase-6b)) declares:

```jsonc
{
  "permissionName": "SentinelPlatform.DelegatedAccess",
  "permissionType": "Scope",
  "tokenAcquisitionFlow": "client_credentials",
  "adminConsentRequired": true
}
```

If a customer's tenant policy forbids client_credentials against Delegated permissions, the fallback is an interactive Foundry-hosted agent path (see section 11) — but that's an interactive-agent scenario and falls outside this track's "ISV product agent runs unattended" remit.

---

## 3. Publisher prerequisites — what Phase 5B requires before it can start

Before the agent emits the first `curl PUT`, the developer must have:

1. **`az` CLI installed and logged in** to a tenant where the Sentinel Platform Services AI Primitives API is enabled. `az account show` should print the right `tenantId` matching `config/workspace.json`.
2. **Phase 4 verification complete.** `config/progress.json` `phases.4_mcp_verification.status == "verified"`. This guarantees every table referenced in Phase 5B is real and every column name is correct against the live workspace.
3. **A populated `config/use-case-brief.md`** with a "Custom MCP Tools" section listing the candidate tool inventory (name, one-line description, KQL question answered, required + optional parameters) — drafted during Phase 1 branch B (the 5-question ideation in section D2 of [the locked plan](../.copilot/session-state/.../plan.md)).
4. **Workspace context locked.** `config/progress.json` `phase2.workspace.{customerId,subscriptionId,resourceGroup,workspaceName}` must be non-null; the publisher needs at least Sentinel Contributor on that workspace.

If any of (1)–(4) is missing, the agent refuses to enter Phase 5B and prints the missing item back to the developer.

---

## 4. Kqs tool payload — what `tools.json` actually contains

Every entry in `config/mcp-tools/<slug>/tools.json` is a Kqs payload matching the Security Platform AI Primitives API shape. Schema (confirmed against `sentinel_mcp_tools.py`):

```jsonc
{
  "displayName":  "summarize-user-signins-24h",
  "description":  "Summarises sign-in success/failure for a UPN in the last 24h. Use when you need authentication context for an identity-driven investigation.",
  "mcpToolType":  "Kqs",
  "queryFormat":  "SigninLogs_CL\n| where TimeGenerated > ago(24h) and UserPrincipalName has '{{UserPrincipalName}}'\n| summarize Total=count(), Successes=countif(ResultType==0), Failures=countif(ResultType!=0), DistinctIPs=dcount(IPAddress) by UserPrincipalName",
  "arguments": {
    "type": "object",
    "properties": {
      "UserPrincipalName": { "type": "string", "description": "UPN to investigate, e.g. alice@contoso.com" },
      "workspaceId":       { "type": "string", "description": "Sentinel workspace customer ID (GUID)" }
    },
    "required": ["UserPrincipalName", "workspaceId"]
  },
  "defaultArgumentValues": {
    "workspaceId": "<workspace-customer-id-guid>"
  }
}
```

### 4.1 `workspaceId` rule (K4, locked)

**Every tool MUST include `workspaceId` in `arguments.properties` AND in `arguments.required`, AND have its default in `defaultArgumentValues.workspaceId` set to the value of `phase2.workspace.customerId` from `progress.json`.** This is enforced by `scripts/Test-McpToolsManifest.ps1` (section 8). Reason: when the consuming agent calls the collection URL, the Sentinel Platform routes the query to the right workspace based on this argument; without it, every `tools/call` returns 400.

### 4.2 Placeholder discipline

- Every `{{Placeholder}}` token in `queryFormat` MUST be declared in `arguments.properties` with a matching name (case-sensitive).
- Every name in `arguments.required` MUST appear at least once in `queryFormat` OR be `workspaceId` (the platform may inject it without you templating it).
- Default values for any *non*-`workspaceId` argument are allowed but optional. The static validator only mandates the workspaceId default.

### 4.3 Naming

- `displayName` is kebab-case, unique within the collection, ≤64 chars. The validator rejects duplicates.
- `description` is **what the calling LLM reads** — write it as model-facing prose ("Use when…", "Returns…"), not as engineering docs.
- Collection name (`<collectionName>` in the API URL) is `<isv-slug>-<usecase-slug>` (e.g. `acme-identity-triage`), 3–40 chars, lowercase, `-` separators only.

### 4.4 What's banned in `queryFormat`

- Tables not present in `phase4_mcp_verification.tablesValidated` for this slug.
- The terms `headless_client` / `headless client`.
- `let`/`function` declarations referring to outside-collection tools (Kqs is a single-statement template, not a multi-tool pipeline).
- Hard-coded workspace IDs / tenant IDs — always use `{{workspaceId}}`.

---

## 5. The Phase 4 → Phase 5B bridge artifact (K1, locked)

Phase 4 (MCP verification) persists per-**table** validation. Phase 5B needs per-**tool** templates. The agent writes a bridge artifact **before** `tools.json`:

`config/mcp-tools/<slug>/validated-tool-queries.json`

```jsonc
[
  {
    "toolName": "summarize-user-signins-24h",
    "queryFormatTemplate": "SigninLogs_CL | where TimeGenerated > ago(24h) and UserPrincipalName has '{{UserPrincipalName}}' | summarize ...",
    "placeholders": ["UserPrincipalName", "workspaceId"],
    "sampleArgs": { "UserPrincipalName": "test.user@contoso.com" },
    "renderedValidationQuery": "SigninLogs_CL | where TimeGenerated > ago(24h) and UserPrincipalName has 'test.user@contoso.com' | summarize ...",
    "rowsReturned": 4,
    "sampleResponseShape": {
      "columns": ["UserPrincipalName","Total","Successes","Failures","DistinctIPs"],
      "rowSample": ["test.user@contoso.com", 7, 3, 4, 2]
    },
    "tablesReferenced": ["SigninLogs_CL"],
    "validatedAt": "2026-05-17T19:14:02Z"
  }
]
```

The agent renders each templated query with `sampleArgs` substituted in, runs it via the built-in Sentinel MCP `query_lake` tool inside the cowork chat, and writes one entry per tool. This file is the **source of truth** for two later checks:

- The static validator (section 8) recomputes the sha256 of each `queryFormatTemplate` and matches it to the `tools.json` entry's `queryFormat` after canonicalisation. Drift fails.
- Phase 5B step 6 hashes `validated-tool-queries.json` per-tool entries as `validatedHash` and stamps them into `progress.json.customMcpTools.tools[i].validatedHash`.

`knowledge/mcp-verification-guide.md` has a parallel callout: in the Custom MCP Tools track Phase 4 outputs become *per-tool* templated KQL during Phase 5B preflight, not per-table.

---

## 6. Publication recipe (Phase 5B steps 3–5)

### 6.1 Step 3 — Collection PUT

```bash
COL=<isv-slug>-<usecase-slug>
TOKEN=$(az account get-access-token --resource 4500ebfb-89b6-4b14-a480-7f749797bfcd --query accessToken -o tsv)

curl -sS -X PUT \
  "https://api.securityplatform.microsoft.com/aiprimitives/mcpToolCollections/$COL?api-version=2025-03-01-preview" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "<ISV Display Name> <Use-Case> Tools",
    "description": "Custom Kqs tools for <ISV> <use-case> scenarios."
  }'
```

Expected response: `200 OK` with the resource representation. `409 Conflict` means a collection with that name already exists in this tenant — either update via PUT (idempotent) or pick a new name.

### 6.2 Step 4 — Per-tool PUTs

For each entry `T` in `tools.json`:

```bash
TOOL_NAME=$(jq -r .displayName <<< "$T")
curl -sS -X PUT \
  "https://api.securityplatform.microsoft.com/aiprimitives/mcpToolCollections/$COL/tools/$TOOL_NAME?api-version=2025-03-01-preview" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$T"
```

200/201 are both success. Capture the response body and stamp `publishedHash` = sha256 of the canonical-JSON request body.

### 6.3 Step 4b — Read-after-write race (K5, locked)

After every per-tool PUT, the platform takes **a few seconds** to propagate. Without this guard, step 5's `tools/list` returns an empty array and the developer thinks publication failed.

```text
poll GET …/aiprimitives/mcpToolCollections/$COL/tools (max 6 retries × 5s)
  → assert each just-PUT tool name appears in the response array
poll JSON-RPC tools/list on https://sentinel.microsoft.com/mcp/custom/$COL/ (max 6 × 5s)
  → assert each tool appears with a populated inputSchema
```

If either poll exhausts retries, fail loudly. **Do not** proceed to `tools/call`.

### 6.4 Step 5 — Consumer-shape validation (K3, locked lifecycle)

This proves the authoring `arguments` → consumer `inputSchema` translation works end-to-end. The agent uses the **publisher's** token here (still has access to the consumption surface).

Lifecycle, in order:

1. **`initialize`** — JSON-RPC notification declaring client capabilities. Capture server caps in response.
2. **`notifications/initialized`** — required ack notification per MCP spec; no response expected.
3. **`tools/list`** — assert each tool name from `tools.json` appears AND `inputSchema` matches the published `arguments` JSON-schema (deep-equal modulo key ordering).
4. **`tools/call`** — one invocation per tool, with `sampleArgs` from `validated-tool-queries.json`. Assert the response contains a `content` array with at least one text/JSON block AND a non-error `isError: false`. Capture the first row of the response for the deployment guide's "Sample response shape" section.

### 6.5 Step 5b — Optional consumer-SP smoke test (K2)

If the developer has already created the consumer SP in this tenant (offered by the agent), the agent can:

```bash
# Use the consumer SP credentials (developer pastes them inline; we never store them)
read -s CLIENT_SECRET
TENANT=ca68c0e4-…
CLIENT=…
TOKEN=$(curl -sS -X POST "https://login.microsoftonline.com/$TENANT/oauth2/v2.0/token" \
  -d "grant_type=client_credentials&client_id=$CLIENT&client_secret=$CLIENT_SECRET&scope=4500ebfb-89b6-4b14-a480-7f749797bfcd/.default" \
  | jq -r .access_token)

# Re-run tools/list + tools/call with the consumer token
```

This is **optional and skippable**. Its only purpose is to catch admin-consent-missing errors before the deployment guide is handed to a customer. If skipped, move on.

### 6.6 Step 6 — Hash stamping into `progress.json` (K7 gate)

For each tool:

```jsonc
{
  "name": "summarize-user-signins-24h",
  "manifestHash":  "<sha256 of canonical tools.json entry>",
  "publishedHash": "<sha256 of canonical PUT request body>",
  "publishedAt":   "2026-05-17T19:21:33Z",
  "validatedHash": "<sha256 of validated-tool-queries.json entry>",
  "validatedAt":   "2026-05-17T19:23:18Z"
}
```

**Hard gate to Phase 6B**: for every tool, `manifestHash == publishedHash == validatedHash` AND `validatedAt >= publishedAt`. If any tool's manifest is edited after publication, its hashes diverge and the gate forces a re-publish + re-validate. Stamping happens in `progress.json.customMcpTools.tools[]` with overall `status` flipping `draft → published → validated`.

---

## 7. Validation runbook (what the static + dynamic gates check)

| Gate | Tool / step | Catches |
|---|---|---|
| Pre-publish static | `scripts/Test-McpToolsManifest.ps1` (section 8) | Duplicate tool names; undeclared `{{placeholders}}`; missing `workspaceId` (K4); banned vocabulary (K9); optional `-Render` dumps rendered KQL for visual review |
| Read-after-write | Step 4b polling | Empty `tools/list` (eventual-consistency) |
| Live shape | Step 5 `tools/list` + `tools/call` | `arguments` ≠ `inputSchema`; `tools/call` returns error; permission/RBAC gaps |
| Hash gate | Step 6 / `progress.json.customMcpTools.tools[]` | Manifest edited after publication; stale validation |
| Post-write lint (Phase 6B) | grep on `deployment-guide.md` + `entra-app.json` | "headless client" / "headless_client" drift |

---

## 8. `scripts/Test-McpToolsManifest.ps1` — what it does

Created in todo C12 (was C12-publish-script, retitled). Required, not optional.

```
Test-McpToolsManifest.ps1 -ManifestPath config/mcp-tools/<slug>/tools.json [-Render] [-JsonOutput]
```

Checks:

1. JSON parses; top level is an array.
2. Every entry has the required keys: `displayName`, `description`, `mcpToolType=="Kqs"`, `queryFormat`, `arguments`, `defaultArgumentValues`.
3. `displayName` values are unique within the file; match `^[a-z][a-z0-9-]{1,62}[a-z0-9]$`.
4. Every `{{token}}` in `queryFormat` appears in `arguments.properties`.
5. Every name in `arguments.required` is either present in `queryFormat` OR is `workspaceId`.
6. `arguments.properties.workspaceId` exists with `type=="string"`; `workspaceId` is in `arguments.required`; `defaultArgumentValues.workspaceId` is a non-empty GUID-looking string.
7. No occurrence of `headless client` or `headless_client` (case-insensitive) anywhere in any string value, anywhere in the file (K9).
8. With `-Render`: substitutes `defaultArgumentValues` + (optional) sample placeholders into each `queryFormat` and prints the rendered KQL to stdout, one block per tool. Useful for visual sanity-check before publication.
9. With `-JsonOutput`: writes a structured pass/fail JSON to stdout (CI-friendly).

Exit codes: `0` clean, `1` validation failures present, `2` file unreadable.

---

## 9. Terminology rules (K9, enforced)

Approved: **"the consuming agent"** or **"a service-principal-based consuming agent"**.

Banned anywhere in track output:

- `headless client`
- `headless_client`
- `headless-client`

Enforcement points:

- `Test-McpToolsManifest.ps1` (section 8 check 7).
- Phase 6B post-write grep over `deployment-guide.md` + `entra-app.json` + `progress.json.customMcpTools`.
- Reviewer responsibility for prose in this guide and `mcp-verification-guide.md`.

Rationale: the term "headless client" appears in the reference implementation repo (`sentinel_mcp_client/headless_client.py`), but it's an internal SDK name. ISVs and customers don't think of their product as "headless" — they think of it as their agent. Calling it "the consuming agent" keeps the deployment guide consumable by both audiences.

---

## 10. Deployment-guide handoff (Phase 6B output, what Phase 6B writes)

Phase 6B is fully covered in [`.github/copilot-instructions.md` section Phase 6B](../.github/copilot-instructions.md). This guide focuses on the **publisher-side** prerequisites; once Phase 5B ends, the developer hands the folder `config/mcp-tools/<slug>/` to the customer (or to their own product team) and that's the deliverable.

`deployment-guide.md` sections (auto-filled from `progress.json` + `tools.json`):

1. Overview
2. Architecture diagram (consuming agent → Entra → `sentinel.microsoft.com/mcp/custom/<name>/` + built-in collections → Sentinel Data Lake)
3. Entra app registration (5 steps, mirrors section 2.2 of this guide)
4. Wiring built-in MCP collections alongside the custom collection — the consuming agent registers **multiple** MCP servers/collections in parallel:
   - `https://sentinel.microsoft.com/mcp/data-exploration/`
   - `https://sentinel.microsoft.com/mcp/triage/`
   - `https://sentinel.microsoft.com/mcp/security-copilot-agent-creation/`
   - `https://sentinel.microsoft.com/mcp/custom/<name>/` ← from this build
5. MCP client config snippets — JSON for `mcp.json` (VS Code Copilot Chat), Foundry tool list, and a generic Python `ClientSession` example.
6. Tool reference — name, description, params, sample invocation, sample response (captured in Phase 5B step 5).
7. Permissions matrix — minimum RBAC + API permission per section 2.2.
8. Updating tools — point at re-running Phase 5B + the optional `scripts/Publish-CustomMcpTools.ps1` sidecar (deferred).
9. Troubleshooting — 401/403 (admin consent missing, wrong audience, missing workspace role), 404 (collection name mismatch), empty `tools/list` (eventual-consistency — re-poll).

`entra-app.json` is the machine-readable record (section 2.2 shape).

---

## 11. No zip packager (K11, locked)

Unlike Security Copilot's `Package-Agent.ps1`, **the Custom MCP Tools track has no zip/store packaging step**. The deliverable is the folder `config/mcp-tools/<slug>/`. The collection itself lives on the authoring API (`api.securityplatform.microsoft.com`); the folder contains only the *consumer-facing* artifacts:

- `tools.json` — the manifest the publisher used (kept for audit + diff against future updates)
- `validated-tool-queries.json` — the bridge artifact, for traceability
- `deployment-guide.md` — for the customer / ISV product team
- `entra-app.json` — for Bicep/`az ad app create` automation

This asymmetry vs Security Copilot is intentional, not accidental. Do not invent a packaging step. Defer `Export-CustomMcpToolsBundle.ps1` until a real customer asks for a bundle format.

---

## 12. Foundry-hosted interactive agent (out-of-band path, FYI only)

If a customer needs an **interactive** agent (analyst-in-the-loop) rather than an unattended product agent, the Custom MCP Tools they publish through this flow are still consumable — by adding the custom collection URL to a Foundry agent's tool list alongside the built-in collections. That path uses **delegated tokens with a real user signed in** (no client_credentials, no admin pre-consent needed — the user consents at first use).

This is not a separate output of the agent; it's a downstream usage pattern. We don't generate Foundry config in `config/mcp-tools/<slug>/`. If the customer asks for it, point them at Foundry docs and re-use the same `<collectionName>`.

---

## 13. Quick reference — endpoints, IDs, scopes

| What | Value |
|---|---|
| Sentinel Platform Services app ID (token resource) | `4500ebfb-89b6-4b14-a480-7f749797bfcd` |
| Token scope for client_credentials | `4500ebfb-89b6-4b14-a480-7f749797bfcd/.default` |
| Required Delegated permission on the consumer app | `SentinelPlatform.DelegatedAccess` (admin pre-consent required) |
| Required workspace RBAC for consumer SP | `Microsoft Sentinel Reader` |
| Required workspace RBAC for publisher (developer) | `Microsoft Sentinel Contributor` (or higher) |
| Collection PUT/GET/DELETE | `https://api.securityplatform.microsoft.com/aiprimitives/mcpToolCollections/{name}?api-version=2025-03-01-preview` |
| Per-tool PUT/GET/DELETE | `https://api.securityplatform.microsoft.com/aiprimitives/mcpToolCollections/{name}/tools/{toolName}?api-version=2025-03-01-preview` |
| Custom collection consumption (JSON-RPC) | `https://sentinel.microsoft.com/mcp/custom/{name}/` |
| Built-in collections (parallel to custom) | `https://sentinel.microsoft.com/mcp/{data-exploration,triage,security-copilot-agent-creation}/` |
| Reference SDK (local, do not vendor) | `/Users/sai/Desktop/sentinel/code/Sentinel-MCP-Client/` |

---

## 14. Cross-references

- Phase 1 track-selection question + 5-question ideation — `.github/copilot-instructions.md` Phase 1 branch B
- Phase 5B cowork flow (steps 1–6) — `.github/copilot-instructions.md` Phase 5B
- Phase 6B deployment-guide & entra-app generator — `.github/copilot-instructions.md` Phase 6B
- Per-tool validation bridge — `knowledge/mcp-verification-guide.md` Custom MCP Tools callout
- Skill activation + trigger phrases — `.github/skills/sentinel-data-connector-agent-builder/SKILL.md`
