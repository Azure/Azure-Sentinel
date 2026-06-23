# Agent Instructions Lint Guide

**Audience:** the Sentinel Data Connector and Agent Builder itself, when drafting or reviewing a Security Copilot agent instructions `.md` in Phase 5A.

**Purpose:** a single, input-agnostic checklist of recurring failure modes observed when ISV-authored instructions are pasted into Security Copilot (SCC). Every Phase 5A draft MUST pass this lint **before** the validator is run, and again **after** the validator returns green, before the user is told the file is paste-ready.

This guide is the source of truth for what "paste-ready" means at the prose level. The `Test-AgentInstructions.ps1` validator only checks KQL syntax + workspace authorization; it cannot catch any of the rules below. The agent definition in `.github/copilot-instructions.md` references this file by name — do not duplicate the checklist there.

---

## How to use this guide

For every Phase 5A draft (whether first cut or a revision):

1. Walk through each section below in order, against the literal `.md` you are about to save.
2. For each rule, find a concrete fragment of the `.md` that satisfies it. If you cannot point to one, the rule fails — fix the `.md` before moving on.
3. Record the lint outcome in `progress.json.phases.5_agent_build.lintResult` as:
   ```json
   {
     "pass": true,
     "checkedAt": "<ISO-8601>",
     "rulesChecked": ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11"],
     "failures": []
   }
   ```
   On `pass: false`, list each failing rule ID with a one-line `reason` and the offending excerpt.
4. The KQL validator runs **after** L1–L11 all pass.

---

## Lint rules

### L1 — Trust-the-binding (input handling)

The primary input is supplied to the SCC agent as a **bound input parameter**, not free-text in chat. The agent must trust the value it receives and proceed. Failing this rule is the single most common reason SCC refuses to run an otherwise-valid invocation (e.g., the agent prompts "please provide a valid IPv4" when the user already bound `src_ip = 10.10.0.42`).

**Required in section 1 of the `.md`:**
- One sentence that explicitly says the input is bound and should be trusted.
- An echo-back line (e.g., `> Investigating <input>: <value>`) the agent must emit at the start of every response.
- A single, narrow "ask again" condition: only when the value is **genuinely absent / empty string** OR is **the wrong kind entirely** (e.g., a UPN supplied where an IPv4 is expected).

**Forbidden phrasings** (any of these triggers SCC to refuse valid inputs):
- "If the input is missing **or is not a valid `<type>`**, stop and ask…"
- "Reject … external IPs / public IPs / non-internal hosts" without naming what counts as internal.
- "Validate the input matches `<regex>` before proceeding."
- "Only accept …" used as a gate (vs. "the expected form is …" used as guidance).
- Any check that requires the LLM to perform CIDR math, geo lookups, DNS resolution, or domain-suffix policy enforcement on the bound value.

**Permitted qualifiers** must be expressed positively and exhaustively. If the agent only meaningfully investigates RFC1918 hosts, name the acceptable ranges (`10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16`) and say they are all acceptable — never leave the LLM to infer the policy.

**KQL-side corollary:** if the input is an IP, the KQL must compare as `string` (`==`), not as `ipv4`, because the bound value is a string.

### L2 — Single primary input

Exactly one input drives the investigation. Helper / optional parameters are allowed only if they have safe defaults baked into the `.md` and the agent can run end-to-end without them. Any text that says "if you also have <X>, the agent will…" is a smell — drop the optional or make it the primary.

### L3 — Mandatory `ago(24h)` time window

Every `kql` (or `kusto`) fenced block must contain `| where TimeGenerated > ago(24h)` as the first filter after the table name. Reject `ago(7d)`, `ago(30d)`, and any literal `datetime(...)` range. Reject queries that summarize without a time bound.

### L4 — Allowlist closure

`## 10. Terminology Guards` must include `**Allowlisted tables (closed set):**` listing every table that appears in any `kql` block in this `.md`, and nothing else. The list uses the **lab-name** (e.g., `SigninLogs_CL`) — not the production rename target. Every `kql` block must reference only allowlisted tables. No `union *`, no `search *`, no `database(...)`.

### L5 — Schema-discipline preamble per table section

Every `## 3.`–`## 7.` section (one per allowlisted table) must open with an `IMPORTANT:` bullet list that includes, verbatim:

- `Do NOT assume the existence of any specific columns, schema, table names, or field names.`
- `Use only columns that exist in the query result.`

…followed by a `Safe fields:` line listing the columns the sample KQL actually references, then a fenced `kql` block labelled `Sample KQL Query (replace {{Placeholder}}):`, then a `Guidance:` paragraph. No tables-of-tables, no metadata blocks.

### L6 — Shadow-rename note for native-shadow tables only

If `progress.json.phases.5_agent_build.allowlistedTables[].kind == "native-shadow"` for a given table, that table's `IMPORTANT:` block must contain exactly one short sentence noting the production rename (e.g., `In production, this table is named SigninLogs without the _CL suffix.`). No more, no less. Do NOT add this note to `custom-cl` tables. Do NOT use the word "shadow" anywhere in the `.md`.

### L7 — Deterministic scoring rubric

`## 8. Scoring Rubric (deterministic — apply in order)` must be a top-down markdown table with mutually-exclusive rules, each referencing scenario IDs from `progress.json.phases.5_agent_build.scenarios[]`. The first matching row wins. No "the agent should consider…" language; rules must be evaluable as boolean expressions over the prior queries' results.

### L8 — Empty-state phrasing in response structure

`## 9. Response Structure` must enumerate the sections of the agent's response and give each section an explicit empty-state phrase (e.g., `If no rows: "No <signal-name> matched in the last 24h."`). Forbid raw row dumps; require summarization + score + correlation. The verdict line must always be present even when all queries return empty.

**Verdict justification rules (enforced):**
- The one-sentence justification on the Verdict line must cite the **specific signals** that drove the verdict — name the table(s), the key event/column values seen (or absent), and the row counts that made the verdict deterministic. The SOC analyst should be able to read the justification and immediately know which raw observations to pivot on.
- **Forbidden phrasings in the verdict line or anywhere in the response section:** `Rubric row N matched`, `row N of the rubric`, `per row N`, `scoring rubric row`, or any other reference to a rubric row number. The SOC analyst does not see the rubric — citing row numbers is meaningless to them.
- Approved shape: `<Verdict> — <specific signals from the queries above that triggered this verdict, in plain prose, naming the tables and column values that fired and any expected corroborating signal that was absent>.`

**Forbidden character in any agent-instructions `.md`:** the section sign `§`. Use the word `section` instead (e.g., `section 3`, `section 9`). The `§` glyph leaks into the agent's runtime response and looks unpolished to the SOC analyst.

### L9 — No meta-content leak

The `.md` is the literal text pasted into SCC's Instructions field. None of the following may appear anywhere in the file:

- Headers/footers like `# Phase 5A`, `_Generated for…_`, `_Last validated…_`, `_See progress.json…_`.
- Markdown tables describing the table allowlist (the allowlist is a bullet in section 10).
- References to `progress.json`, `Test-AgentInstructions`, `Sentinel Data Connector and Agent Builder`, `App Assure`, `lab-05`, or `shadow`.
- Use-case-brief paragraphs (`## Investigation Scenario`, `## Out of Scope`, framework taxonomy).
- Packaging TODOs, dev-vs-prod commentary beyond the single sentence allowed by L6, validator-result footnotes.
- Any "_Note to the developer:_" or `<!-- ... -->` comment.

All of the above belong in `progress.json.phases.5_agent_build` (use the `notes[]` array for free-form items).

### L10 — Voice and second-person discipline

Every `## N.` section reads as direct instructions **to the agent**, in second person ("You are…", "Echo the input back…", "Do not widen…"). No section reads as documentation **about** the agent ("This agent investigates…", "The instructions tell the agent to…"). No first-person plural ("we", "our"). No references to the human author or to the developer running Phase 5.

### L11 — Top-of-section 1 binding placeholder (Test/Preview panel requirement)

The SCC Agent Designer's **Test / Preview panel** substitutes `{{<inputName>}}` tokens that appear in the LLM-visible prose of the instructions before sending the prompt to the model. If the input is referenced **only** inside fenced ` ```kql ` blocks (which the model treats as a KQL template, not as a value already bound), the Test panel never injects the user-supplied value into the model's context and the agent falls through to its "ask the user" path — even when the Inputs panel parameter is filled in and the Description is well-written. This is the single most common reason an SCC agent appears to ignore a bound input.

**Required as the FIRST bullet of `## 1. <InputName> Input`,** verbatim shape:

```
- The bound value for this run is: `{{<inputName>}}`. Use this exact value in every KQL query below.
```

Rules:
- The placeholder name inside `{{ }}` must match the SCC Inputs-panel **Name** field exactly (case-sensitive, same underscores). Cross-check against `progress.json.phases.5_agent_build.primaryInput.name`.
- This bullet appears **before** any other section 1 bullets, including the trust-the-binding sentence from L1 and the echo-back line.
- If the agent has helper / optional inputs (rare — see L2), each one needs its own binding bullet on a new line, in the same shape.
- The bullet's literal text must say "Use this exact value in every KQL query below" — that phrasing is what anchors the model to substitute the value rather than re-prompt. Do not paraphrase to "the agent should use…" or "consider this value…".
- The placeholder must NOT also be wrapped in backticks of a code fence, only in inline backticks — fenced blocks are not substituted.

**Why this works:** at runtime SCC does `instructions.replace("{{src_ip}}", "10.10.0.42")` before the model sees the prompt. With the binding line present, the model sees `The bound value for this run is: 10.10.0.42. Use this exact value…` as plain English at the top of section 1 and treats the input as resolved. Without it, the only `{{src_ip}}` occurrences are inside the KQL samples, which the model reads as "the human will fill this in when they run the query" — so it asks them.

**Lint check:** the regex `^- The bound value for this run is: \x60\{\{[A-Za-z_][A-Za-z0-9_]*\}\}\x60\. Use this exact value in every KQL query below\.$` must match at least one line in section 1, and the captured placeholder name must equal `progress.json.phases.5_agent_build.primaryInput.name`.



The canonical opening (matching paste-ready agents authored from this template) is:

```
# <Agent Display Name>

You are the **<Agent Display Name>**. Given <one-sentence input + intent>, …<one-sentence corroboration list>… Emit a single deterministic verdict from `{<verdicts>}` plus <action>. Ground every claim in KQL across the tables below. Never speculate, paraphrase, or summarize a table you did not query.

## 1. <InputName> Input

- The bound value for this run is: `{{<inputName>}}`. Use this exact value in every KQL query below.
- <Trust-the-binding sentence per L1.>
- Echo the input back on the first line of every response: `> Investigating <input>: <value>`.
- <KQL-comparison note per L1 corollary, if input is IP / string-typed.>
- Only stop and ask if the value is genuinely absent or empty. Do not pivot to free-text search.
- If the user supplies <wrong-kind example>, ask once for a `<InputName>` and stop.
```

Do not deviate from this idiom unless the use case fundamentally requires it.
