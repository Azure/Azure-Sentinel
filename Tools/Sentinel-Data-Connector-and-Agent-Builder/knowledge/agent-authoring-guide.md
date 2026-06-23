# Sentinel Platform Agent Authoring Guide

This guide teaches ISVs how to author production-quality `AgentManifest.yaml` files for Security Copilot agents that run against Sentinel data lake / analytics tier. It captures the structural patterns and instruction-engineering disciplines that distinguish a brittle agent from a deterministic, defensible one.

Use this guide during Phase 5 (Agent Building) and as a checklist when reviewing an ISV's draft manifest.

---

## 1. Manifest Anatomy

Every Sentinel platform agent manifest has three top-level blocks. Each has a specific purpose — do not collapse or reorder.

### 1.1 `Descriptor`

Defines identity, scope, and the runtime context the agent will execute under.

| Field | Purpose | Notes |
|---|---|---|
| `Name` | Internal logical name (no spaces) | Must match `AgentDefinitions.Name` |
| `DisplayName` | Surfaced in Defender portal | Human-readable |
| `Description` | One-sentence value statement | Verb-led: "Correlates X with Y to do Z" |
| `CatalogScope` | `Workspace` or `UserWorkspace` | `Workspace` = visible to all workspace users; `UserWorkspace` = user-private |
| `Enabled` | `true` for shipping agents | |
| `Prerequisites` | Other skillsets the agent depends on | Always include `MCP.Sentinel` if the agent calls Sentinel MCP tools (`query_lake`, `search_tables`, `list_sentinel_workspaces`) |
| `Settings` | Workspace-context inputs the runtime must pass to KQL skills | Standard set: `TenantId`, `SubscriptionId`, `ResourceGroupName`, `WorkspaceName` — required when the agent owns its own KQL skills |
| `SupportedAuthTypes` | `None` for built-in identity flow | |

**Decision rule:** if your agent defines its own `Format: KQL` skills, declare `TenantId`/`SubscriptionId`/`ResourceGroupName`/`WorkspaceName` in `Descriptor.Settings` so they can be templated as `{{TenantId}}` etc. inside KQL skills. If the agent only uses MCP child skills, those settings can be omitted.

### 1.2 `SkillGroups`

A list of skill collections. Two formats matter:

**`Format: Agent`** — the orchestrator. There is exactly **one** orchestrator skill per agent. It carries:
- `Settings.Instructions` — the prompt (covered in section 3)
- `ChildSkills` — the list of tools the orchestrator may call. ChildSkills can include:
  - Built-in MCP tools (`query_lake`, `search_tables`, `list_sentinel_workspaces`, etc.)
  - KQL skills defined in this same manifest (under a `Format: KQL` group)
  - Other agent skills

**`Format: KQL`** — parameterized templated queries. Use these when you need *deterministic, well-scoped* queries that the orchestrator can call by name rather than letting the LLM author free-form KQL. Each KQL skill has:
- `Inputs` — parameters with `Required` / `DefaultValue`
- `Settings.Target: Sentinel`
- `Settings.Template` — KQL with `{{placeholder}}` substitution
- `Settings.TenantId`/`SubscriptionId`/`ResourceGroupName`/`WorkspaceName` — wired from Descriptor settings

**When to define your own KQL skills vs rely on MCP `query_lake`:**

| Use own KQL skill | Use MCP `query_lake` |
|---|---|
| Query is complex / multi-table joined / has business logic | Query is simple lookup or schema discovery |
| You want output shape (column names, sections) guaranteed | You want flexibility / exploration |
| Same query is called for every invocation | Query varies based on what the LLM observed in earlier results |
| You want to enforce a row cap or time window in code | You want LLM to choose lookback adaptively |

A common pattern is to define **2 KQL skills**: one "list" skill (broad enumeration of entities) and one "investigate" skill (deep dive on a specific entity), then let the orchestrator choose between them.

### 1.3 `AgentDefinitions`

Runtime registration:
- `Triggers` — typically a single `DefaultTrigger` with `DefaultPollPeriodSeconds: 0` (on-demand) and `ProcessSkill: <SkillGroup>.<OrchestratorSkillName>`
- `RequiredSkillsets` — must include the agent's own skill group plus any prerequisites (`MCP.Sentinel`, etc.)
- `PreviewState: Private` until ready for catalog
- `PublisherSource: Custom`

---

## 2. Inputs: keep them sharp

A good agent has **one primary input** that names the entity to investigate. Examples of well-shaped inputs:
- A user identifier (UPN, SID, DN, display name) — describe accepted formats and partial-matching behavior
- A host or device identifier (hostname, FQDN, asset ID)
- An incident or alert ID
- A file hash, URL, or other IOC

**Anti-patterns to avoid:**
- Multiple required inputs that force the user to gather context before running the agent. Prefer one required input plus optional refinements.
- Free-text "query" inputs — that's just re-implementing chat. The agent should *narrow* the question, not re-pose it.
- Inputs without examples in the description.

A high-quality input description includes: accepted formats, an example, and whether partial matching is supported.

---

## 3. Instructions: the prompt engineering core

The `Instructions` field is where weak agents fail and strong agents shine. Every production-grade Sentinel agent prompt should contain the following blocks, **in this order**.

### 3.0 Output format — COPY/PASTE-READY for Security Copilot (MANDATORY)

The generated file at `config/agent-instructions/<use-case-slug>.md` is **pasted verbatim** into the Security Copilot Agent Builder "Instructions" pane (per [Security Copilot Lab — Step 2: Define Agent Instructions](https://github.com/suchandanreddy/Microsoft-Sentinel-Labs/blob/main/05-Building-an-Agent-in-Security-Copilot.md#step-2-define-agent-instructions)). Security Copilot is the consumer — not the ISV developer, not the agent, not the static validator. The file must read as a direct, prescriptive prompt **to the Security Copilot LLM**.

**Format rules** (apply to every use case):

1. **Top-level numbered sections only.** Use `## 1. <Title>`, `## 2. <Title>`, … in this fixed order:
   - `## 1. <Input> Input` (e.g. "UserPrincipalName Input", "HostName Input", "SubmissionId Input")
   - `## 2. Global Query Rule (MANDATORY)` — the 24h / 7d / 30d window from section 3.3
   - `## 3. Query Data Lake for <Table_1>` (the primary / gating table)
   - `## 4. Query Data Lake <Table_2> Table`
   - … one section per allowlisted table from section 3.5, in execution order
   - `## <N>. Fallback scan (no <input> supplied)` — only if the agent supports discovery mode (section 3.11)
   - `## <N+1>. Correlation & Reasoning` — section 3.7
   - `## <N+2>. Scoring Rubric (deterministic — first match wins)` — section 3.8
   - `## <N+3>. Surface Key Insights` — short bullet list
   - `## <N+4>. Provide Summary Findings — Output Structure` — section 3.9 numbered sections + the closing RISK SUMMARY from section 3.12
   - `## Sample Automation Flow (Short Version)` — section 3.13, **rename to "Short Version"**; never use "TL;DR for the LLM"

2. **Each per-table section MUST contain**, in this order:
   - An `IMPORTANT:` bullet block stating "Do NOT assume the existence of any specific columns" (section 3.4)
   - A safe-fields list (only columns that exist in the table per Sentinel MCP `search_tables`)
   - One fenced ` ```kql ` block titled `Sample KQL Query (replace ` `` `{{<PlaceholderName>}}` `` `):`
   - The query MUST include `| where TimeGenerated > ago(<window>)` from section 3.2
   - A short `Guidance:` paragraph (3–6 lines max) covering field normalization (e.g. "strip the domain") and any vendor-specific filter triplet

3. **Placeholders use `{{DoubleBrace}}` form.** The static validator (`scripts/Test-AgentInstructions.ps1`) substitutes them at runtime via `-Substitutions @{ <Name>='<value>' }`. Never hardcode subject identifiers in the sample KQL.

4. **WHAT TO EXCLUDE — these belong in the journey, not the file** (the agent collects them via SKILL.md, but they must **never** appear in the generated `<slug>.md`):

| Excluded content | Why | Where it lives instead |
|---|---|---|
| "Built using `knowledge/<...>.md` section <N>" header lines | Internal-engineering breadcrumb | Git commit message |
| Validation script invocation hints (`./scripts/Test-AgentInstructions.ps1 …`) | Belongs to the agent journey | SKILL.md Phase 5 |
| Runtime-validation pointers (`./scripts/Test-AgentInSecurityCopilot.ps1`) | Optional CI sidecar | `knowledge/security-copilot-agent-guide.md` |
| Schema-classification taxonomy ("1P native vs custom `_CL`", Solutions vs Learn URL classification) | Authoring concern | This authoring guide (section 3.5) |
| Conditional `_CL` rename mechanics ("packager strips `_CL` from these names only") | Build-time concern | `scripts/Package-Agent.ps1` |
| Scenario JSON path references (`scenarios/<slug>.json`) | Developer artifact | Phase 0 brief + SKILL.md |
| "Phase 5 of the Sentinel Data Connector and Agent Builder flow" framing | agent concept | `config/progress.json` |
| Phrases like "TL;DR for the LLM", "for the LLM", "SCU budget" | Agent commentary | Drop entirely |
| Reasoning about why a table is included | Authoring decision, not runtime instruction | Phase 0 use-case brief |

5. **Tone:** prescriptive imperative ("Run this query first.", "Always include all three.", "Never use 7 days."). Address the LLM directly. No first-person ("I will…"), no advisory voice ("we recommend…"), no historical narration ("this was added in Phase 3…").

6. **Length budget:** target ~200–300 lines for a 4-table use case. If it exceeds 400 lines, you are leaking journey content — re-check the excluded-content table above.

The agent that generates this file (the Sentinel Data Connector and Agent Builder) reads section 3.1–section 3.13 below to gather the **content**; section 3.0 governs the **form** of the artifact it writes.

### 3.1 Role and intent (1–2 sentences)

State who the agent is and the single thing it does. Keep it grounded — "You are X. Your job is Y."

### 3.2 Input handling rules

- What to do when the input is provided (use it consistently throughout)
- What to do when it's missing or ambiguous (discovery mode? ask back? refuse?)
- Any normalization (e.g., "strip the domain from a UPN before querying field X")

### 3.3 Global Query Rule (MANDATORY)

Every Sentinel agent must enforce a **fixed time window** and a **summarize-don't-dump** rule. Without these the agent will burn tokens and trip rate limits on the first noisy environment.

> Every query MUST filter to the last `<N>` `<unit>`:
> `| where TimeGenerated > ago(<N><unit>)`
>
> To avoid oversized responses: summarize and limit outputs (do not return raw event dumps).

Pick the time window deliberately based on the agent's purpose: real-time triage = 24h; investigation = 7d; posture / hunting = 30d. Document the choice once and require it everywhere.

### 3.4 Schema discipline

The single most common failure mode is the LLM hallucinating column names. Guard against it explicitly:

> IMPORTANT:
> - Do NOT assume the existence of any specific columns.
> - Do NOT assume schema, table names, or hostname/identity field names.
> - Use only columns that exist in the query result.
> - Prefer the following safe fields when available: `<allowlisted columns>`

If a child KQL skill exists, point the orchestrator at it instead of free-form KQL — that's the strongest protection.

### 3.5 Allowlisted tables

State the **per-use-case** closed set of tables the agent may query. Forbid everything else.

In the generated `<slug>.md` file, the allowlist appears **only implicitly** — as one `## <N>. Query Data Lake for <Table>` section per allowed table (section 3.0 rule #1). Do **not** emit a separate "Allowlisted tables" section or the section 3.5 prose; Security Copilot does not need the meta-narrative.

The classification rules below are **authoring concerns for the agent and ISV developer**. They drive the journey (which tables get a section, which lose `_CL` at package time) — they do **not** appear in the generated instructions file.

**Table classification rule** (use this whenever a new candidate table appears):

1. **Check `https://github.com/Azure/Azure-Sentinel/tree/master/Solutions` first.** If the table is referenced from any Solution's `Data Connectors/`, `Parsers/`, `Workbooks/`, or `Analytic Rules/` directory, it is a **custom ISV table**. Its canonical workspace name already includes `_CL` and `_CL` is permanent.
2. **Else, check `https://learn.microsoft.com/azure/azure-monitor/reference/tables/<name>`.** If the page describes a Microsoft 1P service writing to the table directly via diagnostic settings or a built-in pipeline (Entra ID, Defender for Identity, Defender for Endpoint, Defender for Cloud, Activity Logs, etc.) **and** the table is not also defined under `Azure/Azure-Sentinel/Solutions`, it is a **1P native table**. The canonical production name has no `_CL`; the `_CL` form (if any) exists only as a lab mirror.
3. **If still ambiguous, default to custom `_CL`.** Preserving the suffix is the safer choice; surface the ambiguity to the developer before flipping the table into the native-mirror rename list used by `scripts/Package-Agent.ps1`.

Cite the exact Solution path or Learn URL whenever you classify a table — **in the developer chat, not in `<slug>.md`**.

### 3.6 Per-table query playbook

For each allowlisted table, give the orchestrator:
- The table's **purpose** in this investigation (one sentence)
- A **sample KQL** with `{{placeholder}}` substitution
- Any **field-specific normalization** (e.g., "AccountName has no domain — strip the domain from the UPN")
- The **summarization shape** (which fields to count/distinct/makeset)

Sample KQL is not optional. The LLM will use it as a template even when not strictly required.

### 3.7 Cross-table correlation

State explicitly:
- Which fields join across tables (hostnames, user identifiers, IPs, timestamps)
- The **let-binding pattern** for building reusable sets (e.g., `let CvHosts = ... | distinct HostName;`)
- That the agent should use the Sentinel MCP correlation capability, not invent its own

### 3.8 Scoring / classification rubric

Where the agent has to make a judgment call (severity, exploitability, confidence), **define the rubric in the prompt** so output is reproducible across runs:

> Assign qualitative assessment per host:
> - Low: Only one source observed, sparse evidence
> - Medium: One corroborating source in same time window
> - High: Multiple corroborating sources in same time window

Or with mappings:

> Mapping guide: `<field>=0` → Highly exploitable, low values → Moderately exploitable, higher values → Minimally exploitable.

### 3.9 Output structure

Specify the shape of the response. Two patterns work well:

**Numbered section pattern:** every output has the same N sections, each with a fixed header (e.g., `1_Status`, `2_Findings`, `3_Recommendations`). The LLM emits the sections in order; empty sections still get a "no results" line. This makes downstream parsing trivial.

**Summary findings + observations + next actions:** an investigation-style report with a short summary, bullet observations, and recommended pivots.

For each section, supply the exact phrasing for the "result exists" case and the "empty" case:

> - If results exist: `[Name] IS classified as ...`
> - If empty: `[Name] is not classified as ...`

### 3.10 Terminology guards

If your domain has a precise vocabulary, lock it:

> IMPORTANT: Never use the word "cost" when presenting results. Always describe ease-of-exploitation using the relationship exploitability levels (Highly / Moderately / Minimally exploitable).

This is the single biggest lever for making agent output feel professional and product-grade.

### 3.11 Empty / fallback handling

What does the agent do when the primary lookup returns nothing? Don't let it shrug.

> If the investigate tool returns completely empty results:
> 1. Call the list tool to enumerate known entities.
> 2. Scan for the closest match to what the user asked.
> 3. If exactly one plausible match: re-call the investigate tool with the exact name.
> 4. If multiple plausible matches: present them and ask the user to disambiguate.
> 5. If none: tell the user the entity was not found in the environment.

### 3.12 Final risk summary / prioritization

End with a forced summary section that prioritizes the most urgent findings — this is what the user reads first.

> End every response with a RISK SUMMARY that highlights the most critical findings. Prioritize <highest-severity category> first, then <next>, then <next>.

### 3.13 Sample Automation Flow (Short Version)

End the generated `<slug>.md` with a `## Sample Automation Flow (Short Version)` section: a numbered list (5–7 steps) that re-states the orchestration. The Security Copilot LLM uses this as a planning anchor when context is under pressure.

> **Naming rule:** the section header MUST be exactly `## Sample Automation Flow (Short Version)`. Never use "TL;DR for the LLM", "Quick reference", or any agent jargon.

Each step is a single line: "Query **<Table>** for <signal>." or "Correlate signals across <Table_1>, <Table_2>, … and surface actionable security insights."

---

## 4. KQL Skill design rules

When you define a `Format: KQL` skill instead of letting the LLM author KQL:

- **Bind every input to a `let` at the top of the template.** This makes the query readable and prevents injection-style accidents.
- **Always filter by `TimeGenerated > ago(<window>)`** — match the global window declared in Instructions.
- **`take` or `top` cap on every query** — even a `take 500` is better than uncapped.
- **`union` multiple sub-queries with a `Section` extension column** — lets you return a multi-section result from a single skill call (the "investigate_identity" multi-section pattern).
- **`distinct` and `summarize` aggressively** — the agent should never see raw rows, only summaries.
- **No tenant-specific identifiers in the template** — those come from `{{TenantId}}` etc.
- **Default time lookback should match the agent's global window** — if the prompt says 24h, the KQL `let _lookback = ago(24h);`.

---

## 5. ChildSkills: the orchestrator's toolbox

Pick child skills deliberately. A typical Sentinel investigation agent's `ChildSkills` looks like:

```yaml
ChildSkills:
  - <list_skill>          # broad enumeration when the input doesn't resolve
  - <investigate_skill>   # the main deep-dive query (your own KQL skill)
  - search_tables         # MCP — only when schema discovery is genuinely needed
  - query_lake            # MCP — only as an escape hatch for follow-up queries
  - list_sentinel_workspaces
```

**Rule of thumb:** the more deterministic your own KQL skills are, the fewer MCP tools the orchestrator needs. A well-designed agent with two own-KQL skills and one MCP tool will outperform an agent with five MCP tools and free-form KQL every time.

---

## 6. Authoring checklist

Before submitting a manifest:

**Descriptor**
- [ ] `Name`, `DisplayName`, `Description` set; description is verb-led and one sentence
- [ ] `CatalogScope` chosen deliberately (`Workspace` vs `UserWorkspace`)
- [ ] `Prerequisites` includes `MCP.Sentinel` if MCP tools are used
- [ ] `Settings` declares `TenantId`/`SubscriptionId`/`ResourceGroupName`/`WorkspaceName` if own KQL skills exist

**Inputs**
- [ ] Single primary required input
- [ ] Description includes accepted formats + an example
- [ ] Partial-matching behavior documented if applicable

**Instructions**
- [ ] Role and intent (1–2 sentences)
- [ ] Input handling rules (provided / missing / discovery mode)
- [ ] Global Query Rule with explicit time window
- [ ] Schema discipline ("do not assume columns")
- [ ] Allowlisted tables ("use only these")
- [ ] Per-table sample KQL with placeholders
- [ ] Cross-table correlation guidance (join keys + MCP tool)
- [ ] Scoring/classification rubric (if applicable)
- [ ] Output structure with empty-vs-populated phrasing
- [ ] Terminology guards (if domain has precise vocabulary)
- [ ] Empty/fallback handling path
- [ ] Final risk summary with prioritization
- [ ] Sample Automation Flow paragraph

**KQL skills**
- [ ] All inputs bound via `let` at the top
- [ ] `TimeGenerated > ago(<window>)` filter on every sub-query
- [ ] `take`/`top` cap present
- [ ] `Section` extend column when returning multi-section unions
- [ ] No raw row dumps — `summarize`/`distinct` enforced

**ChildSkills**
- [ ] Lean: prefer own KQL skills over MCP free-form when output shape matters
- [ ] Each MCP tool listed has a clear reason to be there

**AgentDefinitions**
- [ ] `Triggers.DefaultTrigger.ProcessSkill` matches `<SkillGroup>.<OrchestratorName>`
- [ ] `RequiredSkillsets` includes own skillset + prerequisites
- [ ] `PreviewState: Private` for first publish

---

## 7. Common failure modes (and how to prevent them)

| Failure | Symptom | Fix |
|---|---|---|
| LLM invents column names | Queries fail with `Failed to resolve column reference` | Add schema-discipline block (section 3.4) and prefer own KQL skills |
| Agent dumps raw events | Token limits hit; response truncated | Add summarize-don't-dump rule (section 3.3); add `take`/`summarize` in KQL |
| Lookback drifts (90d, 365d, "all time") | Slow queries, capacity issues | Pin a single `ago()` window in the prompt and in every KQL skill |
| Output formatting varies between runs | Hard to consume programmatically | Pin numbered sections with fixed headers (section 3.9) |
| Vocabulary inconsistent ("score"/"cost"/"risk" used interchangeably) | Looks unprofessional | Add terminology guards (section 3.10) |
| Empty input returns "no data" with no recovery | Frustrating UX | Add fallback handling (section 3.11) |
| Agent leaks into unrelated tables | Unpredictable, hard to support | Allowlist tables in section 3.5; never use "explore the data lake" framings |
| Orchestrator chooses wrong tool | Inconsistent behavior | Make ChildSkills minimal and name them precisely; let descriptions disambiguate |

---

## 8. Quick reference: minimal manifest skeleton

```yaml
Descriptor:
  Name: <AgentName>
  DisplayName: <Human Readable Name>
  Description: <verb-led one-sentence summary>
  CatalogScope: Workspace
  Enabled: true
  Prerequisites:
    - MCP.Sentinel
  Settings:
    - Name: TenantId
      Required: true
    - Name: SubscriptionId
      Required: true
    - Name: ResourceGroupName
      Required: true
    - Name: WorkspaceName
      Required: true

SkillGroups:
  - Format: Agent
    Skills:
      - Name: <AgentName>
        DisplayName: <Human Readable Name>
        Description: <same as Descriptor>
        Inputs:
          - Name: <primary_entity>
            Description: <accepted formats + example>
            Required: true
        Settings:
          Instructions: |
            # Role
            You are <X>. Your job is <Y>.

            # Input handling
            <rules>

            # Global Query Rule (MANDATORY)
            Every query MUST filter to the last <N><unit>:
            | where TimeGenerated > ago(<N><unit>)
            Summarize outputs; do not dump raw events.

            # Schema discipline
            Do NOT assume columns/tables/field names. Use only fields present in the query result.
            Prefer safe fields: <allowlist>

            # Allowed tables
            <closed list>

            # Per-table playbook
            <table_1>: <purpose>
            Sample KQL:
            <kql>

            # Correlation
            Use the Sentinel MCP correlation tool. Join on <fields>.

            # Scoring rubric
            <Low/Medium/High criteria>

            # Output structure
            Section 1_<Name>: <empty vs populated phrasing>
            Section 2_<Name>: ...

            # Terminology guards
            Never use <forbidden term>; use <approved term>.

            # Empty / fallback handling
            <recovery path>

            # Final summary
            End with a RISK SUMMARY prioritizing <highest> first.

            # Sample Automation Flow
            <3-5 sentence orchestration summary>
        ChildSkills:
          - <own_kql_skill_1>
          - <own_kql_skill_2>
          - search_tables
          - query_lake
          - list_sentinel_workspaces

  - Format: KQL
    Skills:
      - Name: <own_kql_skill_1>
        ...
      - Name: <own_kql_skill_2>
        ...

AgentDefinitions:
  - Name: <AgentName>
    DisplayName: <Human Readable Name>
    Description: <same as Descriptor>
    Product: <ProductName>
    Publisher: <PublisherName>
    Settings:
      - Name: <primary_entity>
        Required: true
    Triggers:
      - Name: DefaultTrigger
        DefaultPollPeriodSeconds: 0
        ProcessSkill: <AgentName>.<AgentName>
    RequiredSkillsets:
      - <AgentName>
      - MCP.Sentinel
    PreviewState: Private
    PublisherSource: Custom
    AgentSingleInstanceConstraint: None
```

---

## 9. How the agent uses this guide

When an ISV reaches Phase 5 (Agent Building):

1. Confirm the **single primary input** the agent should accept.
2. Confirm the **closed set of tables** the agent will query.
3. Walk the ISV through section 3 (Instructions blocks) one at a time — most ISVs miss schema discipline, scoring rubric, and terminology guards.
4. Recommend defining at least one own `Format: KQL` skill if the agent has a recurring deterministic query — this is the single biggest reliability lever.
5. Run the section 6 checklist before they publish.
6. If the manifest fails at runtime, the section 7 table is the first place to diagnose.
