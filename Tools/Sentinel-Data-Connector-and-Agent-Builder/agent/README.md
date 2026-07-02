# Phase 5 — Build & Test the Agent

Per `knowledge/security-copilot-agent-guide.md`, the recommended flow is:

> **AI Foundry (prototype, no SCU cost) → Security Copilot (production) → Security Store (publish)**

## Artifacts

| File | Purpose |
|---|---|
| [agent-instructions.yaml](agent-instructions.yaml) | Validated instructions used in both Foundry and Security Copilot. |
| [investigation-queries.kql](investigation-queries.kql) | The 6 KQL queries the agent will run, each runnable standalone in Data lake exploration. |

## Step 1 — Smoke-test the queries (5 min)

Open https://security.microsoft.com → **Microsoft Sentinel → Data lake exploration → Query**.
Open [investigation-queries.kql](investigation-queries.kql) and run each block in order against `ContosoSOC`.

Expected results for `AlertId == 'ALERT-001'`:

| Query | Expected |
|---|---|
| Step A — resolve | 1 row (`FIN-LAPTOP-07`, `jdoe@contoso.com`, severity High) |
| Step B — lineage | 6 rows, depth 0→4, `outlook → winword → cmd → powershell → rundll32` + `net.exe` sibling |
| Step C — phish email | 1 row, sender `billing@kx7-renewals[.]com`, ThreatTypes contains `Phish; Malware` |
| Step D — network | 2+ rows: `kx7-cdn-update[.]com:443` and SMB hits on port 445 |
| Step D2 — detections | 3 rows incl. `ReflectiveDLLInjection.A` High |
| Single-pane | Rows tying email subject + C2 URL together |

For `ALERT-002` (benign) → Step A returns 1 row, Step B returns 1 baseline row, Steps C/D/D2 return empty. This is the negative test.

If any block fails: re-check Phase 3 ingestion (`kql-jobs/README.md` validation query).

## Step 2 — Prototype in AI Foundry (free)

1. Go to https://ai.azure.com → open project (or create one in `centralus`).
2. **Create Agent**.
3. **Name:** `Contoso-ScriptExecutionInvestigator-Agent`.
4. **Instructions:** paste the `instructions:` block from [agent-instructions.yaml](agent-instructions.yaml) (the multiline string).
5. **Tools** → search "Sentinel" → add **Microsoft Sentinel Data Exploration** MCP tool. Connect it to the `ContosoSOC` workspace.
6. **Test prompt:**
   ```
   Investigate AlertId: ALERT-001
   ```
7. Verify the agent:
   - calls `list_sentinel_workspaces` once
   - calls `query_lake` ≥4 times (Steps A, B, C, D)
   - returns Markdown with **Verdict: TRUE_POSITIVE**, the lineage chain, the phish subject, and the C2 URL
8. Now test `AlertId: ALERT-002` → expect **Verdict: BENIGN**.

Iterate on instructions in Foundry until both verdicts come back correctly. **Do not skip this** — it's the cheapest place to find prompt issues.

## Step 3 — Build in Security Copilot

1. Go to https://securitycopilot.microsoft.com.
2. Create SCU capacity (1 SCU is enough for testing) in `centralus`, RG `<resource-group>`.
3. **Build → Start from scratch.**
4. Paste the same instructions from [agent-instructions.yaml](agent-instructions.yaml).
5. Inputs: `AlertId` (required), `LookbackMinutes` (optional).
6. Tools: `list_sentinel_workspaces`, `search_tables`, `query_lake`, plus the agent itself.
7. Publish to **Myself**, run with `AlertId: ALERT-001`, then `ALERT-002`.
8. Record SCU consumption per run (~3-5 runs) → expect ~1.5 SCU per the brief.

## Step 4 — Export AgentManifest.yaml

In the Build tab, **Export manifest** → save as `agent/AgentManifest.yaml`. This is the artifact Phase 6 packages.

## Common pitfalls (from KB)

| Symptom | Fix |
|---|---|
| Agent returns no data | Tools missing — verify `query_lake` is attached |
| "Sentinel" not under Plugins | Add `MCP.Sentinel` to `RequiredSkillsets` |
| KQL errors "table not found" | Tables 04/05 fell back to `_KQL_CL` — update queries accordingly |
| SCU bill spikes | Delete capacity between sessions |
