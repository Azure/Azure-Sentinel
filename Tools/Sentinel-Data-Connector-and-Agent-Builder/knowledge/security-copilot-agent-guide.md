# Building an Agent in Security Copilot

## Overview

After validating agent instructions in Azure AI Foundry (Lab 4), build the production agent in Microsoft Security Copilot. This is the environment where agents run in production and get published to the Security Store.

## Prerequisites

- Labs 1-2 completed (data lake + data ingested)
- Lab 4 completed (instructions validated in AI Foundry)
- **Security Administrator** role — required to create SCU capacity
- **Security Operator** role — sufficient to create and test agents

## Step 1: Create Security Copilot Workspace

### Navigate to Security Copilot
1. Go to **https://securitycopilot.microsoft.com/**
2. Sign in with organizational credentials

### Create SCU Capacity
1. Select Azure **Subscription** and **Resource Group**
2. Add **Capacity name**
3. Select **Prompt evaluation location** and **Capacity region**
4. Select **1-2 SCUs** for testing

> **Cost Note:** SCUs are billed hourly. Delete SCU capacity when not actively testing. Recreate when needed.

### Create Workspace
1. Select the SCU capacity created
2. Complete workspace creation dialog
3. For **Assign roles** → select "No one. Add them later" if any issues

## Step 2: Create the Agent

### Agent Configuration

1. In workspace, click **Build** → **Start from scratch**
2. **Agent display name:** `<ISVName>-Investigation-Agent`
3. **Agent description:** Brief purpose statement
   - Example: *"Investigates identity risk by correlating authentication signals, access telemetry, endpoint activity, and security alerts"*

### Define Instructions

Copy the validated instructions from AI Foundry (Lab 4). These are identical — the same instructions work in both environments.

### Configure Inputs

Define input parameters that users provide when running the agent:

| Input | Description | Required |
|-------|-------------|----------|
| `UserPrincipalName` | User Principal Name to investigate | Yes |

**Key rule:** Input key names must exactly match what's referenced in instructions (no spaces, case-sensitive).

### Add Tools (Sentinel MCP Skills)

Add the following tools:
- **List Sentinel Workspaces** — `list_sentinel_workspaces`
- **Semantic search on table catalog** — `search_tables`
- **Execute KQL query** — `query_lake`
- **Your agent skill** — The agent itself (for recursive reasoning)

### Publish Agent

Select scope:
- **Myself** — For testing
- **Everyone in my workspace** — For team access

## Step 3: Set Up and Run Agent

1. Navigate to **Agents** in workspace
2. Find your agent → click **Setup**
3. Complete sign-in and finish setup
4. Click **Run** → **One time**
5. Provide input (e.g., `UserPrincipalName: u1291@contoso.onmicrosoft.com`)

## Step 4: Validate Results

Verify the agent run produces:
- ✅ Queries against all relevant tables
- ✅ 24h time filter applied consistently
- ✅ Cross-correlation between identity, access, endpoint signals
- ✅ Structured summary with actionable insights
- ✅ Sentinel appears under **Plugins** section in run view

## Agent Manifest Structure

After building, you can export the `AgentManifest.yaml` from the **Build** tab. This is needed for publishing (Lab 6).

```yaml
Descriptor:
  Name: <ISVName>-Investigation-Agent
  Description: <purpose statement>
  DisplayName: <ISVName>-Investigation-Agent
  CatalogScope: UserWorkspace
  Enabled: true
  Prerequisites:
    - MCP.Sentinel
SkillGroups:
  - Format: Agent
    Skills:
      - Name: <agent-skill-name>
        Inputs:
          - Name: UserPrincipalName
            Description: User Principal Name to investigate
            Required: true
        Settings:
          Instructions: <your validated instructions>
        ChildSkills:
          - list_sentinel_workspaces
          - search_tables
          - query_lake
AgentDefinitions:
  - Name: <ISVName>-Investigation-Agent
    Product: <ISV Product Name>      # MUST be actual ISV name, NOT "Custom"
    Publisher: <ISV Company Name>     # MUST be actual ISV name, NOT "Custom"
    RequiredSkillsets:
      - MCP.Sentinel
      - <agent-skill-name>
    PreviewState: Private
```

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| Agent doesn't query tables | Verify tools are added (list_sentinel_workspaces, search_tables, query_lake) |
| Sentinel not showing in Plugins | Add `MCP.Sentinel` to RequiredSkillsets |
| Empty results | Confirm KQL jobs are running and data exists |
| SCU overspend | Delete capacity after testing session |
| Workspace creation fails | Try "No one" for contributor assignment |

## SCU Consumption Estimation

Before publishing, measure consumption:
1. Run agent 3-5 times with typical scenarios
2. Record SCU usage shown after each run
3. Average and round up
4. Include in plan description: *"This agent typically consumes X.X SCU per analysis run."*

## References

- [Create and manage Security Copilot workspaces](https://learn.microsoft.com/en-us/copilot/security/manage-workspaces)
- [Build an agent in Security Copilot](https://learn.microsoft.com/id-id/copilot/security/developer/create-agent-dev)
- [Security Copilot](https://securitycopilot.microsoft.com/)
- [Lab 05 — Building an Agent in Security Copilot (step-by-step screenshots)](https://github.com/suchandanreddy/Microsoft-Sentinel-Labs/blob/main/05-Building-an-Agent-in-Security-Copilot.md)

---

# Phase 5 validation gate — running the agent in Security Copilot

This section is a **mandatory pre-Phase-6 gate**. Packaging (`scripts/Package-Agent.ps1`) is blocked until every checkbox below is ticked and `phases.5_agent_build.securityCopilotValidation.status` in `config/progress.json` reads `"validated"`.

## Why a separate Phase 5 sub-phase?

AI Foundry validates the *instructions* (schema fit, KQL discipline, scoring rubric). Security Copilot validates the *deployed agent* against the same telemetry an analyst will hit in production. The two environments are not interchangeable — Security Copilot exposes the Sentinel plugin, SCU billing, and the answer-shaping behaviour the SOC will actually experience.

## Pre-flight — SCU capacity detection

The agent does this inline. There is no PowerShell pre-flight you need to run. When you reach Phase 5 in chat, the agent will:

1. Read the current `az` context (subscription + tenant + signed-in user).
2. Run `az graph query -q "Resources | where type =~ 'microsoft.securitycopilot/capacities' | project name, resourceGroup, location, subscriptionId, id"` against your subscription.
3. If at least one SCU capacity is returned, summarise it in chat (name, region, resource group) and record it in `phases.5_agent_build.securityCopilotValidation` of `config/progress.json`. You can move straight to the build steps below.
4. If zero capacities are returned, the agent will direct you to `https://securitycopilot.microsoft.com/` to provision one (Security Administrator role required; 1–2 SCUs is sufficient for testing; billed hourly — delete after the session) and wait for you to come back before continuing.

There is no clean ARM surface for the Security Copilot workspace itself, so the agent confirms the workspace by asking you to visit `https://securitycopilot.microsoft.com/`. Landing on the home/chat surface = workspace exists. Landing on the onboarding wizard = complete it first.

**Optional CI/offline path.** `scripts/Test-AgentInSecurityCopilot.ps1 -ScenarioPath scenarios/<slug>.json` runs the same ARG query and emits a `.out/security-copilot-validation.json` sidecar with the per-scenario runbook (driven by `scenarioCoverage[]`) pre-stamped for manual fill-in. Use it only if you want to drive validation outside the VS Code chat experience. It is not the recommended path.

## Agent build (one-time)

1. Open Security Copilot → **Build** → **+ Create** → **Start from scratch**.
2. **Name**: `<agentName>` (from `progress.json.phases.5_agent_build.agentName`).
3. **Description**: copy the `summary` field from `scenarios/<slug>.json`.
4. **Inputs**: one input.
   - Name: `<primaryInput.name>` (case-sensitive; must match the `{{<name>}}` placeholder in section 1 of the instructions).
   - Type: `string`
   - Required: yes
   - Description: full natural-language sentence — subject + type + purpose + example. Pulled from `progress.json.phases.5_agent_build.primaryInput.description`.
5. **Instructions**: paste the entire contents of `config/agent-instructions/<slug>.md` verbatim into the Instructions box. Do not trim numbered sections.
6. **Tools / Plugins**: enable the built-in **Microsoft Sentinel** plugin. Required capabilities:
   - `list_sentinel_workspaces`
   - `search_tables`
   - `query_lake` (or `query_sentinel`, whichever your tenant exposes)
   - The agent itself (`<agentName>` — required so the orchestrator can invoke its KQL skills)
7. **Workspace binding**: bind to `<workspaceName>` (customerId from `progress.json.phases.2_data_lake_onboarding.workspaceCustomerId`).
8. **Publish scope**: `Me` (private). Promote to `Workspace` only after every scenario in `scenarios/<slug>.json.scenarioCoverage[]` passes.

## Per-scenario test runbook

For each entry in `scenarios/<slug>.json.scenarioCoverage[]`, run a prompt of the form *"Triage `<primaryInput.name>`: `<entityValue>`. Investigate within the last 24h."* in the agent's test pane. The agent **must** use only the tables listed in the per-use-case allowlist (recorded in `progress.json.phases.5_agent_build.allowlistedTables[]`), apply `| where TimeGenerated > ago(24h)`, and emit a verdict from the closed set defined in section 8 of the instructions (typically `{Critical, High, Medium, Low, Informational, Clean}`).

Field mapping for each row (consume verbatim from `scenarioCoverage[i]`):

| Column            | Source field                            |
|-------------------|-----------------------------------------|
| `Test case`       | `scenarioCoverage[i].name`              |
| `Input`           | `scenarioCoverage[i].entityValue`       |
| `Expected verdict`| `scenarioCoverage[i].expectedVerdict`   |
| `Tables expected` | `scenarioCoverage[i].tables`            |
| `Why`             | `scenarioCoverage[i].rationale`         |

At least one entry MUST have `expectedVerdict: "Clean"` (a negative-control row that exercises the empty-state path in output section 9 of the instructions).

## Per-scenario success criteria (apply to every row)

- [ ] Sentinel plugin appears under the agent's "Plugins used" trace.
- [ ] Every KQL query the agent emits begins with `| where TimeGenerated > ago(24h)` as the first filter.
- [ ] Only the tables in `progress.json.phases.5_agent_build.allowlistedTables[]` are queried. No additional tables.
- [ ] No hallucinated columns. Specifically, the agent never invokes a column outside the per-table allowlist in section 4 of the instructions.
- [ ] The verdict matches the **Expected verdict** column.
- [ ] For the Clean negative-control row, the agent emits the section 9 empty-state phrase (defined in the instructions) and stops at the appropriate output section per the section 10 short-circuit rule.

## Sign-off checklist (transcribe to `config/progress.json`)

- [ ] Every scenario in `scenarios/<slug>.json.scenarioCoverage[]` produced the expected verdict.
- [ ] SCU consumption recorded (run the agent 3–5 times, average the reported SCU usage).
- [ ] Sidecar `.out/security-copilot-validation.json` has every `scenariosPassed[].result` set to `"pass"`.
- [ ] `phases.5_agent_build.securityCopilotValidation.status` set to `"validated"`.
- [ ] `phases.5_agent_build.securityCopilotValidation.validatedAt` set to the ISO-8601 UTC timestamp.
- [ ] `phases.5_agent_build.securityCopilotValidation.validatedBy` set to the operator's UPN.

Once every box is ticked, Phase 6 (`scripts/Package-Agent.ps1`) is unblocked.

## Failure handling

| Symptom | Most likely cause | Fix |
|---|---|---|
| Agent queries a table outside the allowlist | Instructions section 5 allowlist not followed | Re-paste the latest `config/agent-instructions/<slug>.md` (it must contain hard guards in section 10) |
| 24h filter missing on one query | Global rule not enforced | Verify section 2 of the instructions is intact; the keyword `MANDATORY` must be present |
| Verdict for the Clean row is `Low` instead of `Clean` | Rubric mis-applied (scoring on noise) | Check section 8 trigger table: `Clean` must require zero hits across every counter, otherwise it falls through to `Low`/`Medium`. |
| Verdict for positive scenarios is one tier lower than expected | Corroboration counter not computed | Section 7 of the instructions; ensure every counter is computed *before* the rubric is applied |
| Sentinel plugin not listed | Agent does not have Sentinel tool bound | Edit agent → Tools → re-add Microsoft Sentinel built-in plugin |
| SCU usage > 1.5 per run | Agent is fan-querying unnecessary tables | Inspect emitted KQL; ensure section 5 allowlist is honored and section 7 short-circuits when the primary-table query returns 0 rows |

