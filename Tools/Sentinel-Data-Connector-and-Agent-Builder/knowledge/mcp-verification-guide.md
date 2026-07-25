# MCP-Driven Schema & Query Verification Guide
**Phase 4 of the Sentinel Data Connector and Agent Builder flow — mandatory before Phase 5.**

> This guide replaces the prior `mcp-server-guide.md` + `foundry-agent-guide.md`. It tells the agent how to use the Microsoft Sentinel MCP server to **discover real table schemas, fetch sample data, and dry-run candidate KQL** against the data the developer just ingested in Phase 3 — and then **cowork with the developer** to confirm those findings before Phase 5 instruction authoring begins.

---

## 1. Purpose

After Phase 3 ingestion, the ISV's lab workspace contains real `_CL` tables with real rows. The agent must **ground its Phase 5 KQL in the actual schema** — never assume column names, never invent tables. This Phase 4 verification gate enforces that discipline.

Cowork framing: the agent narrates each MCP call it makes, surfaces what it learned, and asks the developer to confirm — *not* "here's the answer, take it or leave it."

Why Sentinel MCP is sufficient on its own (no Foundry, no custom tools needed for Phase 4):
- `search_tables` returns the **actual** column list for a table in the bound workspace
- `query_lake` runs the candidate KQL against real data — same engine the production Security Copilot agent will use in Phase 5
- VS Code chat is the cowork surface; nothing else is required

---

## 2. Prerequisites

- ✅ Phase 3 ingestion validated (`config/progress.json.phases.3_data_ingestion.status == "ingestion_complete"`)
- ✅ Per-use-case table allowlist defined in `config/use-case-brief.md` and `scenarios/<advisor>.json`
- ✅ Entity pools defined in `config/entities.json`
- ✅ Sentinel MCP server connected in VS Code (see section 3)

---

## 3. Connect to the Sentinel MCP server (VS Code)

The Sentinel MCP server runs **inside VS Code** as an MCP transport managed by `.vscode/mcp.json`.

### 3a. Auto-setup (agent driven — DEFAULT PATH)

Whenever the agent attempts an MCP tool call and sees any of these failure signatures from the VS Code MCP client output, it **must** run the auto-setup routine below before retrying — do NOT just surface the raw error to the developer:

- `404 status sending message to https://sentinel.microsoft.com/mcp`
- `Connection state: Error 404 status connecting to … as SSE`
- `MCP server '<name>' not found` / `No MCP server matching pattern`
- Any `mcp_*` tool returning "tool not available" / "no MCP servers configured"

**Auto-setup routine (the agent performs steps 1–3 itself; the developer only clicks Start + Allow in step 4):**

1. Confirm `az` login + tenant context match `config/progress.json.phases.2_data_lake_onboarding.tenantId`. If mismatched, run `az login --tenant <tenantId>` first (this is the same identity VS Code will use to authenticate the MCP server below).
2. Read `.vscode/mcp.json` in the repo root.
   - **If the file is absent**, create it with the block in section 3b below.
   - **If the file exists** but is missing the `sentinel-mcp-data-exploration` entry, **merge** the entry into the existing `servers` object (preserve any other MCP servers the developer has configured — do NOT clobber the file).
   - **If the entry exists but the URL is bare `https://sentinel.microsoft.com/mcp`** (the 404 root cause — the bare host has no MCP protocol handler; every collection needs a suffix), patch the URL to `https://sentinel.microsoft.com/mcp/data-exploration` and save.
3. Tell the developer **verbatim** in chat:

   > I wrote `.vscode/mcp.json` with the Sentinel MCP server (`data-exploration` collection). To finish setup:
   >
   > 1. Open `.vscode/mcp.json` in the editor (**Cmd/Ctrl + P** → type `.vscode/mcp.json`).
   > 2. You'll see an inline action row directly **above** the `"sentinel-mcp-data-exploration"` entry: click **▶ Start**.
   > 3. VS Code pops an **Allow** authentication dialog → click **Allow** and sign in with an account that has **Security Reader** (or higher) on the Sentinel workspace.
   > 4. The CodeLens above the server entry will change to `⏹ Stop | 🔄 Restart | 🛠 <N> Tools | Running`. That **`Running`** label + the tool count is your green light.
   > 5. (Optional double-check: **View → Output**, switch the channel dropdown to **`MCP: sentinel-mcp-data-exploration`** — the last line should read `Connection state: Running`.)
   > 6. Reply `connected` once you see `Running`.
   >
   > (Reference: <https://github.com/suchandanreddy/Microsoft-Sentinel-Labs/blob/main/03-Sentinel-MCP-VSCode-Setup.md> steps 1–2.)

4. Pause this phase until the developer replies `connected` (or equivalent). Then retry the original MCP tool call. If the same 404 / not-found error returns, re-read `.vscode/mcp.json` and verify the URL is exactly `https://sentinel.microsoft.com/mcp/data-exploration` — a stale workspace-level `mcp.json` in `~/Library/Application Support/Code/User/` can shadow the repo file; surface that possibility before asking the developer to re-authenticate.

### 3b. `.vscode/mcp.json` canonical content

```json
{
  "servers": {
    "sentinel-mcp-data-exploration": {
      "type": "http",
      "url": "https://sentinel.microsoft.com/mcp/data-exploration"
    }
  }
}
```

**Why `/data-exploration` and not bare `/mcp`:** `https://sentinel.microsoft.com/mcp` is just the host root — the MCP protocol is served per **collection**. The four built-in collections each have their own URL: `/mcp/data-exploration`, `/mcp/triage`, `/mcp/security-copilot-agent-creation`, and `/mcp/custom/<name>` for ISV-published collections. Pointing at the bare host returns HTTP 404 because there is no transport handler there — this is exactly the symptom in the 404 error pattern listed in section 3a.

If the agent also needs `triage` or `security-copilot-agent-creation` tools, add additional entries to the same `servers` object (one per collection).

### 3c. Manual fallback (when auto-setup can't run — e.g., no file-write access)

Fall back to the lab-03 manual flow:

1. Sign in to Azure CLI: `az login --tenant <tenantId>`
2. Confirm subscription: `az account show --query "{name:name, id:id}" -o table`
3. Press **Cmd/Ctrl + Shift + P** → **`MCP: Add Server`** → **HTTP (HTTP or Server-Sent Events)**.
4. Enter the URL: **`https://sentinel.microsoft.com/mcp/data-exploration`**.
5. Assign the Server ID **`sentinel-mcp-data-exploration`**; choose workspace or global scope.
6. Click **Allow** on the authentication dialog and sign in.
7. Confirm the server shows **Running** via the CodeLens in `.vscode/mcp.json` (see section 3a step 4).

Reference: <https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-server> and lab-03 (<https://github.com/suchandanreddy/Microsoft-Sentinel-Labs/blob/main/03-Sentinel-MCP-VSCode-Setup.md>).

---

## 4. Built-in tools reference (what the agent uses in Phase 4)

| Tool | Purpose | Phase 4 use |
|---|---|---|
| `list_sentinel_workspaces` | Enumerate workspaces visible to the signed-in identity | Confirm workspace binding matches `config/workspace.json` / `phases.2_data_lake_onboarding.workspaceName` |
| `search_tables <pattern>` | Return tables with metadata + **actual column list** | Discover real schema per table in the use-case allowlist |
| `query_lake <kql>` | Execute KQL against the data lake | Freshness probe + sample rows + dry-run candidate KQL |

Other built-ins (`list_incidents`, `list_entities`, `list_alerts`, etc.) are not part of the mandatory Phase 4 recipe but may be invoked opportunistically by the agent if the developer asks.

---

## 5. The Phase 4 verification recipe (5 steps + confirmation)

The agent executes these steps **conversationally** — each tool call is narrated, results are summarized, and the developer is asked one consolidated question at the end.

### Step 1 — Confirm workspace binding
- Call `list_sentinel_workspaces`
- Pick the workspace whose `customerId` matches `config/workspace.json`
- If no match → abort: "Phase 2 onboarding does not match any MCP-visible workspace. Stop and re-run `Validate-DataLake.ps1`."

### Step 2 — Resolve canonical table names
Tables in `config/use-case-brief.md` may be written in lab form (`SigninLogs_CL`) but the workspace may also expose native form (`SigninLogs`). For each table in the allowlist:
- Call `search_tables <TableName>` and also `search_tables <TableName-without-_CL>` for native-mirror candidates
- Record the **actual table name present** in the workspace
- If neither form is found → flag as **missing** (Phase 3 ingestion incomplete for that table — block Phase 4)

### Step 3 — Discover schema + freshness per table
For each resolved table, call `query_lake`:
```kql
<TableName>
| summarize rowCount = count(), latest = max(TimeGenerated), earliest = min(TimeGenerated)
```
Record `{rowCount, latest, earliest}`. Then call `search_tables <TableName>` to capture the **actual column list**.

Block if: `rowCount == 0` for any allowlisted table, OR `latest` falls outside the use-case time window declared in `scenarios/<advisor>.json` (e.g. last 24h for SigninLogs, last 7d for SecurityAlert).

### Step 4 — Validate required keys (correlation + entity binding)
For each table the use case will join or filter on, assert the columns exist:
- **Time key**: `TimeGenerated` (or table-specific equivalent)
- **Primary entity key**: e.g. `UserPrincipalName`, `AccountUpn`, `SourceUserName`
- **Correlation keys**: per `scenarios/<advisor>.json` (e.g. `CorrelationId`, `PathId`, `DeviceName`)
- **Vendor filters** for native-shared tables (e.g. `SecurityAlert | where ProductName == "<vendor>"`)

If any required key is missing from a table's schema, the agent must surface the gap and propose a fix (drop the table, swap to an alternate, or ask the developer to extend the ingestion).

### Step 5 — Dry-run candidate KQL per table
The agent drafts one candidate query per table using the **discovered** columns (not assumed). For each candidate:
- Substitute a placeholder entity from `config/entities.json` (typically the primary breach UPN)
- Execute via `query_lake`
- Record `{queryValid: true|false, entityRowCount: N, broadRowCount: M, error: null|string}`

Two distinct outcomes are tracked: a query can be syntactically valid (`queryValid=true`) yet return zero rows for the chosen entity (`entityRowCount=0`). The latter is not necessarily a failure — but is surfaced for developer review.

### Step 6 — Conversational confirmation (one checkpoint per pass)
The agent posts ONE consolidated summary to chat — never per-table interrogation — shaped like:

> Using the Sentinel MCP server against your `<workspace-name>` workspace I confirmed:
> - **`SigninLogs_CL`**: 4 rows, latest 18 min ago, columns include `UserPrincipalName, TimeGenerated, RiskLevelDuringSignIn, IPAddress, ResultType` (✅ all required keys present). Candidate KQL returned 2 rows for `<entity-example>@<isv-slug>.demo`.
> - **`<IsvCustomTable>_CL`**: 6 rows, latest 22 min ago, columns include `PathId, RiskScore, SourceObjectId, TargetObjectId` (✅). Candidate KQL returned 4 high-risk paths.
> - **`SecurityAlert_CL`**: 3 rows, latest 24 min ago, columns include `AlertName, ProductName, CompromisedEntity` (✅). Candidate KQL returned 1 row for `ProductName == "<ISV Product Name>"`.
> - ⚠️ **`DeviceLogonEvents_CL`**: 3 rows present, but `AccountUpn` column missing — only `AccountName` available. Proposed adjustment: join on `AccountName == split(UserPrincipalName, "@")[0]`.
>
> Want me to:
>  (a) **proceed to Phase 5** with these schemas + draft KQL?
>  (b) **adjust** — e.g. drop a table, add a column to ingestion, swap a join key?
>  (c) **re-run verification** after you tweak the data?

The agent must **wait for developer confirmation** before advancing.

---

## 6. Persist findings to `config/progress.json`

After confirmation, the agent auto-edits `phases.4_mcp_verification`:

```json
{
  "status": "confirmed",
  "workspace": {
    "name": "<workspace-name>",
    "customerId": "<workspace-customer-id-guid>"
  },
  "tablesChecked": [
    {
      "requestedName": "SigninLogs_CL",
      "resolvedName": "SigninLogs_CL",
      "rowCount": 4,
      "latest": "2026-05-16T14:32:11Z",
      "columnsPresent": ["UserPrincipalName", "TimeGenerated", "RiskLevelDuringSignIn", "IPAddress", "ResultType"],
      "requiredKeysOk": true
    }
  ],
  "candidateKqlResults": [
    {
      "table": "SigninLogs_CL",
      "kql": "SigninLogs_CL | where TimeGenerated > ago(24h) and UserPrincipalName has '<placeholder>' | summarize ...",
      "queryValid": true,
      "entityRowCount": 2,
      "broadRowCount": 4,
      "error": null
    }
  ],
  "developerFeedback": "proceed",
  "confirmedAt": "2026-05-16T14:55:02Z",
  "confirmedBy": "developer@isv.com"
}
```

Allowed `status` values:
- `not_started` — Phase 4 not yet entered
- `in_progress` — agent currently running the recipe
- `confirmed` — developer explicitly approved findings
- `grandfathered` — Phase 4 implicitly completed under a prior flow (legacy ISVs only)
- `failed` — verification blocked (zero rows, missing key, schema mismatch)

---

## 7. Phase 4 exit criteria (hard gate before Phase 5)

Phase 5 instruction authoring (`agent-authoring-guide.md` section 3) **must not begin** until:
- `phases.4_mcp_verification.status ∈ {"confirmed", "grandfathered"}`
- Every allowlisted table has `requiredKeysOk: true` OR has a documented adjustment in `developerFeedback`
- At least one candidate KQL per table has `queryValid: true`

`scripts/Package-Agent.ps1` enforces this gate before Phase 6 packaging runs.

---

## 7B. Custom MCP Tools track — per-tool callout

This section applies only when `config/progress.json` has `agentTrack == "custom-mcp-tools"`. The Security Copilot track is unchanged.

**Key difference from the Security Copilot track:** in the Custom MCP Tools track, Phase 4 outputs are not consumed by an instructions document — they are consumed by **per-tool templated KQL** declared in `config/mcp-tools/<slug>/tools.json` (Phase 5B). So Phase 4 validation must be done **per candidate tool**, not just per table.

### What changes in Phase 4

| Stage | Security Copilot track | Custom MCP Tools track |
|---|---|---|
| Schema discovery (section 4) | Per-table — feeds instructions narrative | Per-table — same MCP calls, results also feed every tool that references that table |
| Candidate KQL validation (section 5) | Per-table — at least one KQL per allowlisted table | **Per-candidate-tool** — every candidate tool from the use-case-brief gets at least one templated KQL run with sample arguments |
| Persisted artifact | `phases.4_mcp_verification.tables[]` only | `phases.4_mcp_verification.tables[]` **plus** a Phase 5B preflight artifact `config/mcp-tools/<slug>/validated-tool-queries.json` (see K1 in `knowledge/custom-mcp-tools-guide.md` section 5) |
| Exit criteria | Every allowlisted table has `queryValid: true` | Every **candidate tool** in `config/use-case-brief.md` "Custom MCP Tools" section has at least one validated rendered KQL pass |

### Per-tool validation flow

For each candidate tool listed in `use-case-brief.md`:

1. Take its KQL question (one-sentence) and the parameter list (Q4 in section D2 ideation).
2. Draft the templated KQL with `{{placeholders}}` matching the parameter list. Always include `{{workspaceId}}` (rule K4).
3. Substitute sample argument values (developer-supplied or defaults) to render an executable KQL body.
4. Run the rendered KQL via Sentinel MCP `query_lake` against the lab workspace.
5. Confirm: row shape is non-empty (or expected-empty for negative-control tools), columns referenced in `project`/`summarize` actually exist (cross-check with `search_tables` output), and the rendered query parses.
6. Surface to developer in chat: tool name, templated KQL, sample args used, rendered KQL, row count, sample row. Ask confirm/adjust.
7. On confirmation, the validated entry is staged for Phase 5B step 0 to persist into `validated-tool-queries.json`. Phase 4 itself does **not** write that file — Phase 5B does, after the developer has confirmed the full candidate tool list.

### Joins across allowlisted tables

If a candidate tool references built-in tables (`SigninLogs`, `SecurityAlert`, `DeviceLogonEvents`) alongside the ISV `_CL` table, run the rendered KQL through `query_lake` end-to-end during Phase 4 — do not validate the legs independently. A join that works in isolation but fails on `joinkey` cardinality is a Phase 4 finding, not a Phase 5B finding.

### Exit gate for Custom MCP Tools track

Add to the section 7 exit criteria when `agentTrack == "custom-mcp-tools"`:
- Every candidate tool in `use-case-brief.md` "Custom MCP Tools" section has at least one `queryValid: true` rendered KQL pass logged in chat.
- Developer has explicitly confirmed the candidate tool list (collection-level approval) before Phase 5B begins.

The Phase 5B static validator (`scripts/Test-McpToolsManifest.ps1`, per K6) cross-checks that every tool in `tools.json` traces back to a validated entry in `validated-tool-queries.json`. A tool with no Phase 4 lineage is a hard fail.

---

## 8. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `list_sentinel_workspaces` returns empty | Wrong tenant / no Sentinel role | `az login --tenant <id>`; verify "Microsoft Sentinel Reader" role on the workspace |
| `search_tables <Name>` returns 0 rows | Table not yet ingested (DCR propagation lag) or name typo | Wait 10 min after Phase 3 ingestion; verify exact `_CL` casing |
| `query_lake` returns `429 Too Many Requests` | Hit lake query throttle | Backoff 30s; reduce `take` size |
| `query_lake` returns rows but `TimeGenerated` is older than expected | Stale sample data | Re-run `scripts/Invoke-AttackScenarioIngestion.ps1` |
| MCP server stuck "Starting" in VS Code | Stale auth token | Sign out + back in to VS Code's Azure account |

---

## 9. References

- [Microsoft Sentinel MCP server — overview](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-server)
- [Logs Ingestion API (Phase 3 reference)](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview)
- Repo: `knowledge/agent-authoring-guide.md` section 3 — Phase 5 instruction authoring (consumes Phase 4 outputs)
- Repo: `.github/skills/sentinel-data-connector-agent-builder/SKILL.md` — agent capability surface (Phase 4 cowork tone)
