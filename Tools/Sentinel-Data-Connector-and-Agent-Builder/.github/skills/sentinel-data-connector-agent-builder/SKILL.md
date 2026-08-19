# Sentinel Data Connector and Agent Builder

## Skill Description

Interactive ISV developer cowork for building two kinds of Sentinel-MCP-powered artifacts: (a) **Security Copilot agents** that analysts chat with in `securitycopilot.microsoft.com`, or (b) **Custom MCP tool collections** that the ISV's own product agent (or a customer's custom agent) calls programmatically alongside Microsoft's built-in Sentinel MCP collections. Phase 1 begins with a track-selection question; from there each track shares Phases 0/2/3/4 (data lake onboarding, sample-data ingestion, MCP verification) and diverges at Phase 5/6. Capabilities span use-case ideation, data lake onboarding, data ingestion, MCP verification, agent instruction authoring, custom MCP tool authoring + publication, and final packaging or deployment-guide generation.

## Capabilities

### Use Case Ideation
- **Phase 1 begins with a track-selection question (mandatory).** Ask the developer whether they are building (a) a Security Copilot agent that an analyst chats with, or (b) a Custom MCP tool collection consumed programmatically by their product's own agent (or a customer's custom agent) alongside Microsoft's built-in Sentinel MCP collections. Persist the choice as `agentTrack: "security-copilot" | "custom-mcp-tools"` in `config/progress.json` (root field, schemaVersion=2).
- For the **Security Copilot** track: continue with the existing 6-question ideation (scenario, primary entity, signals, scope, verdict rubric, success criteria) → `config/use-case-brief.md`.
- For the **Custom MCP Tools** track: run the 5-question tool ideation (consumer audience, candidate tool scenarios, KQL question per tool, parameters/placeholders, built-in-table joins) → `config/use-case-brief.md` "Custom MCP Tools" section with `collectionName` + candidate tool list.
- Helps ISVs discover their security use case aligned with six agentic frameworks
- Produces structured use-case briefs
- Maps ISV product signals to investigation scenarios or tool candidates

### Data Lake Onboarding Automation
- Validates Azure permissions and tenant configuration
- Creates Log Analytics workspaces via az cli
- Enables Microsoft Sentinel on workspace
- Guides manual Defender portal data lake onboarding steps
- Validates completion via API

### Data Ingestion Pipeline

Logseeder-style **DCE/DCR + Logs Ingestion API** framework that emits correlated sample
records satisfying the locked Phase 0/1 detection scenarios. The agent operates the
pipeline through four parameterised verbs:

**1. `generate_baseline`** — emit the full Phase 0 use-case-driven dataset
- Reads: `config/use-case-brief.md`, `config/isv-schema.json`, `config/entities.json`,
  `schemas/<Table>.json`, `scenarios/<scenario>.json`
- Deploys (if missing): 1 DCE + N per-table DCRs + N `*_CL` tables in the workspace
- Synthesises records honoring correlation rules (UPN, PathId, CorrelationId, DeviceName)
  and per-scenario timing windows (e.g. SigninLogs ≤24h, SecurityAlert ≤7d, IOEs ±10m)
- POSTs to `{DCE}/dataCollectionRules/{immutableId}/streams/Custom-<Table>` (api 2023-01-01)
- Runs `Validate-Ingestion.ps1 -ScenarioPath scenarios/<scenario>.json` and asserts every
  `scenarioCoverage[]` entry meets `expectedMinHits`
- Entrypoint: `scripts/Invoke-AttackScenarioIngestion.ps1` (calls `Invoke-SampleDataIngestion.ps1`)

**2. `extend_scenario`** — add records to an existing scenario without redeploying tables
- Developer prompts (e.g. *"add 10 kerberoasting events"*, *"generate benign-only baseline"*)
  are translated into a delta over the scenario JSON (`extensions[]` block)
- Engine reuses deployed DCRs; only the record count / filter changes
- Re-runs the scenario-coverage validator to confirm no regression

**3. `add_table`** — onboard a new custom table mid-flight
- Inputs: table name, source-of-truth schema (URL or inline)
- Generates `schemas/<Table>.json`, appends a DCR ARM under `templates/`, redeploys the
  one new DCR, registers the table in `scenarios/<scenario>.json` table list
- Classifies the table (see rule below). If classified **1P native**, appends the name
  to the native-mirror rename list consumed by `scripts/Package-Agent.ps1`; otherwise
  leaves the rename list untouched so `_CL` is preserved through packaging.

**4. `validate_coverage`** — re-run only the detection-scenario KQL assertions
- `scripts/Validate-Ingestion.ps1 -ScenarioPath <path>` executes every `kqlAssertion`
  against Log Analytics, returns pass/fail per scenario, exits non-zero on any miss

**Table allowlist is per use case, not global.** Each scenario JSON declares the tables
the agent's KQL is allowed to reference for that investigation. There is no fixed,
repo-wide list of permitted tables — `add_table` (and equivalent edits to
`scenarios/<scenario>.json`) extends the per-use-case allowlist whenever the
investigation needs more signals.

**Table classification rule (1P native vs custom `_CL`).** For every table the agent
considers ingesting or querying, decide whether the workspace name carries `_CL`
permanently or only as a lab artifact:

1. **Check `https://github.com/Azure/Azure-Sentinel/tree/master/Solutions` first.** If
   the table is referenced from any Solution under `<Solution>/Data Connectors/`,
   `<Solution>/Parsers/`, `<Solution>/Workbooks/`, or `<Solution>/Analytic Rules/`,
   the table is a **custom ISV table**. Its canonical workspace name already includes
   `_CL` (e.g. an alerts table delivered by a Content Hub data connector). `_CL` is
   permanent and is **preserved** through packaging.
2. **Otherwise, check `https://learn.microsoft.com/azure/azure-monitor/reference/tables/<name>`.**
   If the page describes a Microsoft 1P service that writes to the table directly via
   diagnostic settings or a built-in pipeline (Entra ID, Defender for Identity,
   Defender for Endpoint, Defender for Cloud, Activity Logs, etc.) — and the table is
   **not** also defined inside `Azure/Azure-Sentinel/Solutions` — the table is a
   **1P native table**. In production the canonical name has no `_CL`. We may ingest
   it as `<Name>_CL` in lab; `scripts/Package-Agent.ps1` strips `_CL` at publish.
3. **If still ambiguous, default to custom `_CL`.** Preserving the suffix is the safer
   choice; surface the ambiguity to the developer before flipping a table into the
   native-mirror rename list.

The agent must cite the exact Solution path or Learn URL it used to classify any new
table when calling `add_table`. The `Package-Agent.ps1` validator asserts:
(a) every name on the native-mirror rename list has `_CL` stripped in the packaged
manifest, (b) every other `_CL` table appearing in the source is still present in
the output unchanged.

Knowledge reference: `knowledge/data-ingestion-guide.md`.

### Phase 4 MCP Verification (cowork)
- Connects to Sentinel MCP server (`https://sentinel.microsoft.com/mcp`) live from VS Code per `knowledge/mcp-verification-guide.md`
- For each allowlisted table: resolves canonical name (`_CL` vs native) via `search_tables`, fetches schema + freshness, validates required keys, dry-runs candidate KQL via `query_lake`, captures `queryValid` / `entityRowCount` / `broadRowCount` distinctly
- Surfaces findings conversationally to the ISV developer in ONE consolidated checkpoint per pass (not per-table interrogation)
- Persists results to `config/progress.json.phases.4_mcp_verification`; Phase 5 instruction authoring is hard-gated on `status ∈ {"confirmed","grandfathered"}`

### Agent Building
- Generates agent instructions in the **Security Copilot prescriptive template format** — numbered sections (UserPrincipalName Input, Global Query Rule MANDATORY, one numbered Query section per allowlisted table with IMPORTANT / Safe Fields / Sample KQL using `{{UserPrincipalName}}` placeholder, Correlation, Insights, Summary, Sample Automation Flow short version)
- Builds KQL queries for investigation scenarios
- Creates correlation logic across data sources
- Validates instructions in AI Foundry via `scripts/Test-AgentInstructions.ps1` (offline schema + KQL discipline check)

### Phase 5 Security Copilot Validation Gate (mandatory before packaging)
Production validation of the built agent against real Security Copilot — required entry condition for Phase 6.

**Operate as a coworker, not a script launcher.** When the developer finishes Phase 4 (instructions generated) and asks how to test the agent, do **not** open with *"run this PowerShell script."* Walk them through the Security Copilot experience the way a teammate would. The PowerShell helper exists for sidecar bookkeeping only — never present it as step 1.

**Step 1 — Detect SCU capacity inline.** Use the `bash` tool to run Azure Resource Graph yourself:
```bash
az graph query -q "Resources | where type =~ 'microsoft.securitycopilot/capacities' | project name, resourceGroup, location, subscriptionId, id" --output json
```
- If at least one capacity is returned, summarise it conversationally: *"I found your Security Copilot capacity **`<name>`** in **`<location>`** (resource group `<rg>`). You're good to build the agent."* Record the capacity id, resource group, and region into `phases.5_agent_build.securityCopilotValidation` in `config/progress.json`.
- If zero capacities are returned, say so plainly and link the developer to `https://securitycopilot.microsoft.com/` to provision one (Security Administrator role required; 1–2 SCUs are enough for testing; billed hourly so delete after the session). Offer to re-detect when they're done. Do not move forward until a capacity exists.

**Step 2 — Walk the developer through building the agent in the Security Copilot portal.** Speak the steps inline; do not redirect them to a runbook URL as the primary path. Reference the exact file in their workspace so they can copy from VS Code into the portal:

1. Open **https://securitycopilot.microsoft.com/** → **Build** → **+ Create** → **Start from scratch**.
2. **Name**: use the agent display name from `scenarios/<advisor>.json` → `agentDisplayName`.
3. **Description**: copy the `summary` field from the same `scenarios/<advisor>.json`.
4. **Inputs**: add a single input `userPrincipalName` (string, required) — match the placeholder used in the instructions file.
5. **Instructions**: open `config/agent-instructions/<advisor>.md` in VS Code and paste it verbatim into the Instructions box. Do not trim numbered sections.
6. **Tools / Plugins**: enable the built-in **Microsoft Sentinel** plugin and confirm `list_sentinel_workspaces`, `search_tables`, `query_lake` are bound.
7. **Workspace binding**: bind to the workspace recorded in `phases.2_data_lake_onboarding.workspaceName` of `config/progress.json`.
8. **Publish scope**: `Me` (private) until all test scenarios pass.

**Step 3 — Run the test scenarios in the agent's test pane.** Surface the prompts and expected verdicts directly from `scenarios/<advisor>.json` → `scenarioCoverage[]`. Walk through them one at a time, ask the developer to paste the agent's verdict back into chat, and you record each `scenariosPassed[].result` (`pass` / `fail`) into `config/progress.json`. The verdict rubric for each scenario comes from `scenarios/<advisor>.json` → `verdictRubric`.

**Step 4 — When every scenario passes**, flip `phases.5_agent_build.securityCopilotValidation.status` to `"validated"`, stamp `validatedAt` (ISO-8601 UTC) and `validatedBy` (signed-in `az ad signed-in-user show` UPN), and tell the developer Phase 6 packaging is now unblocked.

**Fallback — only if the developer explicitly asks for a non-interactive checklist or CI runner**, mention `scripts/Test-AgentInSecurityCopilot.ps1` (same ARG detection + writes a sidecar `.out/security-copilot-validation.json` template they can fill in offline). It is never the recommended path.

Phase 6 packaging (`scripts/Package-Agent.ps1`) is **hard-blocked** until `securityCopilotValidation.status == "validated"` and every `scenariosPassed[].result == "pass"`.

Knowledge reference: `knowledge/security-copilot-agent-guide.md` section  "Phase 5 validation gate".

### Custom MCP Tools Authoring & Deployment (Phase 5B + 6B — `agentTrack == "custom-mcp-tools"`)

When the developer selected the Custom MCP Tools track in Phase 1, Phases 5A (Security Copilot instruction authoring) and 6A (`Package-Agent.ps1`) are replaced by Phases 5B and 6B. Operate as a coworker, not a script launcher — the chat is the primary interface; scripts are sidecars.

**Phase 5B — Cowork tool authoring + publication.** Inputs: validated KQL bodies from Phase 4 MCP verification, `config/use-case-brief.md` candidate tool list, `config/isv-schema.json`, `config/progress.json.phase2.workspace`.

1. **Step 0 — Bridge artifact.** Render each candidate tool's templated `queryFormat` with sample args, run it via Sentinel MCP `query_lake` inline, and write `config/mcp-tools/<slug>/validated-tool-queries.json` (per-tool, not per-table). This is the input to `tools.json`. (Per plan section K1.)
2. **Step 1 — Draft `tools.json`.** Write `config/mcp-tools/<slug>/tools.json` — an array of Kqs payloads with `title`, `description`, `queryFormat` (KQL with `{{placeholders}}`), `arguments` (JSON schema), `defaultArgumentValues`. **Every tool MUST include `workspaceId` (string) in `arguments.properties` AND `arguments.required`, with `defaultArgumentValues.workspaceId` set to `progress.json.phase2.workspace.customerId`.** (Per plan section K4.)
3. **Step 2 — Static validation.** Run `scripts/Test-McpToolsManifest.ps1 -ManifestPath config/mcp-tools/<slug>/tools.json -JsonOutput`. Validator asserts: unique tool names; every `{{placeholder}}` declared in `arguments.properties`; no undeclared placeholders; `required` args used in template; K4 workspaceId rule; banned terms "headless client" / "headless_client" absent. Optional `-Render` mode dumps rendered KQL for visual review. (Per plan section K6 / section K9.)
4. **Step 3 — Publish (publisher identity = developer's `az login`).** Acquire token via `az account get-access-token --resource 4500ebfb-89b6-4b14-a480-7f749797bfcd`. Inline `curl -X PUT` the collection envelope to `https://api.securityplatform.microsoft.com/aiprimitives/mcpToolCollections/<name>?api-version=2025-03-01-preview`, then PUT each tool to `…/{name}/tools/{toolName}?api-version=2025-03-01-preview`. After each PUT, poll `GET …/tools` (max 6 × 5s) until tool name appears — read-after-write race per plan section K5.
5. **Step 4 — MCP lifecycle validation (consumer surface).** POST JSON-RPC to `https://sentinel.microsoft.com/mcp/custom/<name>/` using the developer's bearer: `initialize` → `notifications/initialized` → `tools/list` (assert every published tool name + capture `inputSchema`) → `tools/call` once per tool with sample args. (Per plan section K3.) Poll `tools/list` similarly (eventual consistency) before `tools/call`.
6. **Step 4b (optional) — Consumer-SP smoke test.** If the developer has already created the consuming agent's service principal (Phase 6B artifact), offer to acquire a token via `ClientSecretCredential` (client_credentials flow, scope `.../.default`) and repeat `tools/list`/`tools/call` to prove the runtime path. Skippable — the publisher-identity validation in Step 4 is sufficient for the gate.
7. **Step 5 — Progress + gate.** Update `config/progress.json.phases.5_agent_build.customMcpTools` per-tool with `manifestHash`, `publishedHash`, `publishedAt`, `validatedHash`, `validatedAt` (sha256 over the tool's normalized JSON). Hard-gate Phase 6B entry: for every tool, `manifestHash == publishedHash == validatedHash` AND `validatedAt >= publishedAt`. Stale validations force re-publish. (Per plan section K7.)

**Phase 6B — Deployment guide + Entra app reg template (consumer-only).** Inputs: `tools.json`, published collection metadata, `progress.json` workspace details.

1. Generate `config/mcp-tools/<slug>/deployment-guide.md` covering: overview, architecture (consuming agent → Entra → `sentinel.microsoft.com/mcp/custom/<name>` + built-in collections → Sentinel Data Lake), Entra app reg walkthrough, wiring custom + built-in MCP collections together (`data-exploration`, `triage`, `security-copilot-agent-creation`, `custom/<name>`), MCP client config snippets (mcp.json / Foundry / VS Code Copilot Chat), per-tool reference (name, params, sample invocation, sample response shape captured in Phase 5B step 4), permissions matrix, update procedure, troubleshooting.
2. Generate `config/mcp-tools/<slug>/entra-app.json` — machine-readable consumer identity spec. **Required permission**: `SentinelPlatform.DelegatedAccess` (`type=Scope`, `adminConsentRequired=true`) on resource app `4500ebfb-89b6-4b14-a480-7f749797bfcd` (Sentinel Platform Services). Plus `Microsoft Sentinel Reader` RBAC on the workspace. (Per plan section K10 — Delegated + admin pre-consent, not an App Role; the consuming agent runs unattended via `ClientSecretCredential` + admin-consented Delegated scope.)
3. **Terminology lint (K9).** Fail Phase 6B if `headless client` / `headless_client` appears in `tools.json`, `deployment-guide.md`, `entra-app.json`, or `progress.json.customMcpTools`. Approved replacement: "the consuming agent" or "a service-principal-based consuming agent".
4. **No zip packager.** Unlike Security Copilot's `Package-Agent.ps1`, the deliverable IS the folder `config/mcp-tools/<slug>/`. Do not create a packaging step. (Per plan section K11.)

**Publisher vs consumer identity (locked, plan section K2).** Phase 5B uses the developer's interactive `az login` (Sentinel Contributor on the resource group hosting the collection). Phase 6B `entra-app.json` describes a separate service principal that the consuming agent will use at runtime — never conflate the two; doing so causes 401/403.

Knowledge reference: `knowledge/custom-mcp-tools-guide.md` (14 sections — track positioning, two-identity split, publisher prereqs, Kqs payload reference, Phase 4→5B bridge, publication recipe, validation runbook, validator spec, terminology rules, deployment-guide template, no-zip note, Foundry interactive note, quick reference, cross-refs).

### Agent Publishing
- Creates package.zip with required structure
- Generates SaaS offer descriptions
- Guides Partner Center submission
- Provides MISA preparation guidance

## Trigger Phrases

- "Help me build a Security Copilot agent"
- "I want to integrate my product with Sentinel"
- "Guide me through data lake onboarding"
- "Help me ideate an agent use case"
- "Create a custom MCP tool"
- "Author a custom MCP tool collection"
- "Publish Kqs tools to Sentinel Platform Services"
- "Build MCP tools my product's agent can call"
- "Generate a deployment guide for my custom MCP tools"
- "How do I publish to Security Store"
- "Set up data ingestion for my product"
