# Custom Connector Builder Guide

**When this guide fires:** Phase 0 step 3 returned **No match** in `Azure/Azure-Sentinel/Solutions/` for the ISV's company name. The ISV does not have a published Sentinel connector and we will build one from scratch using the **Sentinel Custom Connector Builder Agent** (`@sentinel /create-connector`) inside GitHub Copilot Chat in VS Code.

**Authoritative reference:** https://learn.microsoft.com/en-us/azure/sentinel/create-custom-connector-builder-agent

---

## Automation model — Hybrid

The agent automates **everything it can backend** (web search, prereq checks, file inspection, ARM deploy, role assignment, sample-data ingestion) and only stops for the developer at four explicit **approval gates**:

| Gate | Where | Why developer is needed |
|---|---|---|
| 1. API doc selection | Step 1 | Pick which doc URL to feed `@sentinel` |
| 2. Send `@sentinel` prompt | Step 2 | Chat participants can't call each other; the developer pastes one prompt into Copilot Chat |
| 3. Test Connector click | Step 4 | The Test Connector pane requires VS Code UI interaction with live API auth |
| 4. Approve deploy + role assignment | Step 5 | Final go/no-go before resources are created in the Azure subscription |

Everything else — searching for docs, reading the generated workspace files, parsing the schema, running `az deployment group create` against the generated ARM template, assigning Monitoring Metrics Publisher to the DCR, and ingesting sample data — runs without prompting the developer.

---

## What the builder produces

`@sentinel /create-connector` is an agent inside the **Microsoft Sentinel VS Code extension**. Given an ISV's API documentation URL, it autonomously generates a complete **Codeless Connector Framework (CCF)** connector in the user's local workspace folder:

1. **Polling configuration** (REST API endpoint, auth, paging, schedule)
2. **Data Collection Rule (DCR) mappings** (transform from API payload → Sentinel columns)
3. **Connector definition** (the JSON that surfaces the connector in the Sentinel UI)
4. **Schema and table references** (the custom `*_CL` table the connector writes to)

Once deployed, the connector ingests data into a **custom table** (typically named `<Vendor><Product>_CL`). For Phase 3 routing this becomes a **`connectorType: custom-table`** path (Branch A).

---

## Prerequisites — verify before invoking the agent

Walk the developer through each item. Stop and resolve any failure before proceeding.

| Prereq | How to verify |
|---|---|
| Microsoft Sentinel workspace exists & accessible | Phase 2 must be complete (data lake onboarded). Re-check `config/progress.json.workspace`. |
| VS Code installed with GitHub Copilot Chat | `code --version` and confirm Copilot Chat extension is enabled. |
| **Microsoft Sentinel VS Code extension** installed | Marketplace: `ms-security.ms-sentinel`. Reload VS Code if just installed. |
| Sentinel **Contributor** role on the workspace | `az role assignment list --assignee <upn> --scope <workspaceResourceId> -o table` — must include `Microsoft Sentinel Contributor` (or `Contributor`). |
| Copilot Chat model = **Claude Sonnet 4.5 or later** | In Copilot Chat model picker, confirm Claude Sonnet 4.5+ is selected. The builder agent is only validated on Claude Sonnet 4.5+. |
| Empty local folder open in VS Code | All generated files land in the open workspace folder. Use a fresh folder per ISV (e.g., `~/sentinel-connectors/<Company>`). |

---

## Step 1 — Find or collect the ISV API documentation  *(backend; ends at approval gate 1)*

The agent needs the URL of the ISV's REST API documentation (preferably an OpenAPI/Swagger spec, but any HTML reference page that describes endpoints + auth is acceptable). The agent runs the search itself and only stops to ask the developer which result to use.

**a. Search publicly first.** Use `web_search` with these queries (in this order — stop on first hit that returns real API docs):

1. `<Company> API documentation site:<vendor-domain>`
2. `<Company> developer portal REST API`
3. `<Company> OpenAPI swagger`
4. `<Company> SIEM integration API` (security vendors often expose a SIEM-specific API)
5. `<Company> webhook events API reference`

**b. Present results to the developer** as a numbered list:

```
I found these candidate API documentation pages for <Company>:

  1. <title> — <url>
  2. <title> — <url>
  3. <title> — <url>

Which one should I pass to @sentinel? Or do you have an internal/private API doc URL to use instead?
You can also pass multiple — paste any additional URLs.
```

**c. If the search returned nothing usable** (vendor docs gated, no public REST API surface), ask the developer:

> "I couldn't find public API documentation for <Company>. Please paste the URL to your API reference (an OpenAPI/Swagger JSON URL works best, but any HTML reference page is fine). If your docs are behind login, paste an exported OpenAPI spec into a file in this folder and give me the path."

**d. Validate every URL — must use `scripts/validate-urls.sh`. No manual `curl`, no exceptions.**

URL validation is now enforced through a single script so it cannot be silently skipped or faked in reasoning. Run it on **every** candidate URL (including any URL the developer pastes) before saving anything to `progress.json` or showing the URL to the developer:

```bash
scripts/validate-urls.sh "<url1>" "<url2>" ...
```

The script prints one JSON line per URL with `status`, `finalUrl`, `pass`, and `reason`, and **exits non-zero if any URL fails**. It performs HEAD-with-redirect-follow, falls back to GET on 405/403, and only marks a URL `pass:true` when the final status is `200` AND the final host matches the input host (catches login-wall and off-host marketing redirects).

Rules tied to the script output:
- A URL is "validated" **only** if `pass:true` in the JSON output of *this turn's* script run. A `pass:true` from a previous turn does not count — re-run before reuse.
- **Never invent, infer, or extrapolate URLs.** Do not guess `/api/getting-started/submissions/` exists just because `/api/getting-started/` does. Only run the script on URLs that came from a `web_search` result or were pasted by the developer.
- If a URL fails (`pass:false`), do **not** substitute another URL silently. Tell the developer: "`<url>` returned `<status>` (`<reason>`) — I can't confirm it exists. Please paste the correct link, or I'll proceed with only the validated URLs: `<list>`." Then re-run the script on whatever they provide.
- Soft-404s (200 + off-host redirect) are caught by the host-mismatch check; trust the script's `pass` field, not the raw status code.

You **must** include the script's JSON output in your reply (or summarize it verbatim per URL — `url`, `status`, `pass`) so the developer can see what was actually validated. Do not write a free-form "I validated these URLs" claim — paste the script output.

**e. Save** only the URLs with `pass:true` to `config/progress.json` as `apiDocUrls: [<url>, ...]`. Also save the script output to `config/progress.json.urlValidation` (array of the JSON lines from the most recent run) so we have a verifiable audit trail. Never persist a URL that is not in the latest `pass:true` set.

**f. Extract connector metadata from the validated docs.** `@sentinel` works best when given the API specifics up front rather than asked to discover them. From the validated doc pages (use `web_fetch` on each `apiDocUrls` entry), extract and save the following to `config/progress.json.connectorMeta`:

| Field | Example | Notes |
|---|---|---|
| `dataType` | `Submissions`, `Alerts`, `AuditLogs` | The logical record type the developer wants to ingest. Confirm with developer if multiple are plausible. |
| `authScheme` | `Authorization: Bearer <token>` (or `Authorization: Token <id>:<secret>`) + any `Accept` header the API requires | Exact header(s) and value format. Quote the docs verbatim — do not paraphrase. |
| `baseUrl` | `https://api.<isv-domain>` | Production REST base. **`curl` validate this one too** — same rules as doc URLs. |
| `primaryEndpoint` | `GET /submissions` | The endpoint the connector will poll. Note pagination model (cursor / page / offset) and incremental key (e.g., `updated_at`). |
| `rateLimit` | `60 requests/minute per IP` | If documented; otherwise mark `unspecified`. |
| `targetTable` | `<Company><DataType>_CL` | Custom Log Analytics table name; must end in `_CL`. |
| `responseEnvelope` | `json-api` / `flat-array` / `wrapped-data` | **Anti-bug field — REQUIRED.** Fetch one real sample response (use the developer's API key — see "Secrets handling" below — against a no-op endpoint, or grab a published response example from the docs page). Classify: **`json-api`** = `{data:[{id,type,attributes:{...},relationships:{...}}], included:[...], links:{...}}` (per the [JSON:API spec](https://jsonapi.org/)); **`wrapped-data`** = `{data:[{...flat...}], next_cursor:"..."}` or `{results:[...], meta:{...}}`; **`flat-array`** = `[{...},{...}]` at the root. If `json-api`, `@sentinel` MUST declare `attributes`/`relationships` as `dynamic` stream columns and read fields via `attributes.<field>` / `relationships.<rel>.data.id` — see Requirements block below. |
| `timeFilterParam` | `filter[updated_at]` / `since` / `start_time` | **Anti-bug field — REQUIRED.** The exact query-param name for incremental polling, **verified from a docs example** (not guessed). Many JSON:API-style services use bracket syntax (`filter[updated_at]`) — bracket-notation params must also be marked `urlEncodeBrackets: true` in `connectorMeta` so the prompt requests `filter%5Bupdated_at%5D` encoding. Wrong param name = filter silently dropped, every poll re-fetches the entire dataset (a common cause of unbounded re-ingestion). |
| `paginationTerminator` | `next-link-absent` / `empty-data-array` / `total-count-exceeded` | **Anti-bug field — REQUIRED.** How the poller knows pagination is done. `next-link-absent` = stop when `links.next` is null (JSON:API). `empty-data-array` = stop when `data.length == 0`. `total-count-exceeded` = stop when `offset > meta.total`. Offset pagination without a terminator combined with a broken time filter = unbounded re-paging across every poll cycle. |
| `pollCadenceMin` | `15` (default), `5` (only if API has documented sub-minute freshness AND developer accepts cost) | **Anti-bug field — REQUIRED.** Default to **15 minutes**, not 5. Shorter cadence compounds 3x faster when the filter is broken. Only drop below 15 if the API has documented sub-minute freshness AND the developer explicitly accepts the cost profile. |
| `expectedDailyVolume` | `~300 records/day` (small tenant) … `~50,000 records/day` (enterprise) | **Anti-bug field — REQUIRED for the cost-burn check (Step 6.5).** Order-of-magnitude estimate from docs, the developer's dashboard, or a one-shot `curl` against the API. Phase 6.5 will alert if observed ingestion exceeds 2× this number in the first hour. |

If any field cannot be found in the validated docs, **do not invent a value** — ask the developer or mark `unknown` and surface the gap before composing the prompt. Never guess auth schemes, rate limits, response envelopes, or filter param names from your training data. **The six anti-bug fields above are non-optional** — if any is `unknown`, the prompt must explicitly call that out so `@sentinel` asks the developer, rather than guessing and shipping a poller that silently over-ingests.

**Secrets handling — API key input rule (applies to every step that needs the developer's API credential):**

When the agent itself needs the developer's API key (e.g., to fetch a sample response in step 1.f to classify `responseEnvelope`, or to run the cost-burn check in Step 6.5 against the live API), **always** prompt for it via the `ask_user` tool with a single-line prompt — do NOT ask the developer to paste the key into a free-form chat message. The `ask_user` input is a structured textbox; tell the developer in the prompt text that:

- The key is consumed in-process only.
- The key is **never** written to `config/progress.json`, any session-state file, or any committed artifact.
- The key is **never** echoed back into the chat transcript (the agent must redact it as `<api-key-redacted>` in any follow-up message that references the value).
- The developer should rotate the key if it has ever been pasted into a free-form chat message (in this session or any previous one).

For the VS Code-native **Test Connector** pane (Step 4) the input is already a `type: "password"` textbox driven by the Sentinel extension — no additional handling required there.

---

## Step 2 — Hand off to the @sentinel agent  *(approval gate 2 — one message in the same chat)*

`@sentinel` is a separate Copilot Chat **participant** that shares this conversation. Chat participants cannot call each other programmatically today, so the developer must send the prompt themselves — but they do **not** open a new window, switch workspaces, or lose chat history. They send one message starting with `@sentinel` in this same chat tab and come back when generation finishes.

**Pre-flight (backend, all in one turn before composing the prompt):**

1. **Verify extension + role + model**: extension check uses the **filesystem path** (works without `code` on PATH): `ls -d ~/.vscode/extensions/ms-security.ms-sentinel-* 2>/dev/null | head -1`, with `code --list-extensions 2>/dev/null | grep ms-security.ms-sentinel` as fallback. Only prompt the developer to install if both return empty. `az role assignment list` shows **Microsoft Sentinel Contributor** on the workspace; Copilot Chat is in **Agent mode** with **Claude Sonnet 4.5+** (callout, not blocker).
2. **Create the connector folder** `connectors/<isv-slug>/` inside this repo (kebab-cased company name from Phase 0). Use `mkdir -p connectors/<isv-slug>`. This folder is the **only** place `@sentinel` should write — keeps the repo source tree clean and gives the agent a known glob root for Step 3.
3. **`connectors/<isv-slug>/` is already inside the open agent workspace — do NOT ask the developer to "Add Folder to Workspace" or change their workspace context.** VS Code resolves the relative path from the workspace root, and the `@sentinel` prompt pins `connectors/<isv-slug>/` explicitly, so files land there regardless of which file the developer last clicked. Tell them once (verbatim, single line): "I've created `connectors/<isv-slug>/` inside your open workspace — `@sentinel` will generate files there because the prompt pins that path." No `ready` reply needed; proceed directly to composing the prompt.
4. **Persist** `connectorBuildFolder: "connectors/<isv-slug>/"` and `connectorBuildFolderReadyAt` to `config/progress.json`.

**Pre-composition URL re-check (mandatory — must use the script).** Even though Step 1.d already validated each URL, **re-run `scripts/validate-urls.sh` on every URL going into the prompt — every entry in `apiDocUrls` AND `connectorMeta.baseUrl` — in this same turn, immediately before composing the prompt:**

```bash
scripts/validate-urls.sh "<doc-url-1>" "<doc-url-2>" "<connectorMeta.baseUrl>"
```

Then act on the script output:
- If the script exits **non-zero**, you may NOT compose the prompt yet. For each URL with `pass:false`: drop it from the prompt, never substitute a guessed URL, and tell the developer which URL failed and why (paste the JSON line).
- If **all** doc URLs fail, return to Step 1 and re-collect — do **not** proceed to compose the prompt.
- If `connectorMeta.baseUrl` fails, do **not** proceed — ask the developer for the correct base URL and re-run the script.
- If only some doc URLs fail, ask the developer whether to proceed with the remaining `pass:true` set or pause for replacements.

Paste the script's JSON output into your reply before the prompt block, so the developer can see exactly which URLs were validated this turn. Do not write a free-form "URLs re-validated" claim.

**Never include in the prompt:** URLs that did not come back as `pass:true` from `validate-urls.sh` *in this turn*; URLs that were not retrieved from `web_search` results or pasted by the developer; URLs constructed by appending path segments to a known-good base; or URLs from your training data.

**Compose the prompt with full connector metadata** — the prompt is **not** intentionally minimal. `@sentinel` produces better, less-iterative output when given exact auth, base URL, endpoint, pagination, rate limit, and target table up front. **Pin the output path** to `connectors/<isv-slug>/` so files don't scatter into the repo root. Use this template, filling each field from `progress.json.connectorMeta`:

```
@sentinel /create-connector Create a connector for <Company> to ingest <DataType> data into Microsoft Sentinel.

Generate all files inside the `connectors/<isv-slug>/` workspace folder (do not write to the repo root).

Here are the API docs:
<validated-url-1>
<validated-url-2>

Authentication: <exact-auth-header(s)-quoted-from-docs>.
Base URL: <validated-baseUrl>
Primary endpoint: <method> <path> (paginate <pagination-model>, poll incrementally by `<incremental-key>`).
Response envelope: <json-api | flat-array | wrapped-data>.
Pagination terminator: <next-link-absent | empty-data-array | total-count-exceeded>.
Rate limit: <rate-limit-or-"unspecified">.
Target table: <Company><DataType>_CL (custom table).
Publisher: <Company> (use this exact value when prompted for the Content Hub publisher — do not ask).

Requirements (must be enforced in the generated files — do not skip any):

1. **Response envelope shape.** If the response envelope is `json-api` (records under `data[]` with `attributes{}` and `relationships{}` sub-objects):
   - The DCR `streamDeclarations` MUST declare `attributes` and `relationships` as columns of type `dynamic` (not flattened top-level fields).
   - The DCR `transformKql` MUST project values from `attributes.<field>` and `relationships.<rel>.data.id` — not from non-existent top-level fields.
   - `TimeGenerated` MUST use `coalesce(todatetime(tostring(attributes.<timestamp-field>)), now())` so events keep their source timestamp instead of defaulting to ingest time.
   - For `flat-array` or `wrapped-data` envelopes, declare flat top-level columns matching the actual payload keys.

2. **Time-window filter — exact param name.** Use **`<timeFilterParam>` exactly as written in the docs** (e.g., `filter[updated_at]` — note any `_at` suffix, snake_case vs camelCase, bracket notation). Wrong param names are silently dropped by most APIs, causing every poll to re-fetch the full unfiltered list. If `urlEncodeBrackets` is true for this API, request URL-encoded brackets (`filter%5Bupdated_at%5D`) in the CCF `queryParametersTemplate`.

3. **Pagination terminator.** Honor `<paginationTerminator>` in `paging.pagingTypeTemplate`:
   - `next-link-absent` → stop when `links.next` is null/missing.
   - `empty-data-array` → stop when `data[]` is empty.
   - `total-count-exceeded` → stop when `offset + pageSize >= total`.
   Without an explicit terminator, offset pagination loops forever and compounds any filter bug.

4. **Poll cadence.** Set `pollingFrequency` / `queryWindowInMin` to `<pollCadenceMin>` (default **15 minutes**, never less than 5). Shorter cadences multiply the blast radius of any filter or pagination bug — a 5-minute poll over 24 h is 288 polls; combined with a dropped filter that's 288× the daily record volume.

5. **Sort for early termination.** If the API supports a `sort` parameter, request newest-first (e.g., `sort=-<incremental-key>`) so the poller can stop at the first record older than `_QueryWindowStartTime` instead of paging to the end.

6. **Target table naming.** `<Company><DataType>_CL`. Do NOT add `_Raw_CL` or other suffixes unless the developer specifically asks for a raw-tier table.
```

If a metadata field is `unknown`, **omit that line** rather than writing `unknown` into the prompt — `@sentinel` will then ask the developer interactively for that field. The Requirements block stays in the prompt unconditionally — even if a few fields are `unknown`, the rules still apply.

**Tell the developer, verbatim:**

> 📋 Copy the block below and send it as your **next message in this same chat** — no need to open a new chat window or switch workspaces. `@sentinel` is a chat participant that shares this conversation; when it finishes generating files into `connectors/<isv-slug>/`, just reply `done` (or `generated` / `finished`) and I'll pick back up automatically.
>
> ```
> <full prompt block built above>
> ```
>
> Tips:
> - When `@sentinel` asks to evaluate or write files, click **Allow responses once**, or click **Bypass Approvals** in the chat to auto-approve all subsequent file writes.
> - **Do not edit the generated files while the build is running** — error squiggles during generation are expected and clear once the build finishes.
> - Generation typically takes a few minutes.

**While the developer runs the prompt, pause this agent's flow.** When their next message contains any of `done`, `generated`, `finished`, `connector created`, `built`, or pastes back a file list, resume **automatically** — do not ask them to list files (see Step 3).

---

## Step 3 — Inspect the generated artifacts  *(backend; auto-resume, no developer input)*

**`@sentinel` may not honor the pinned `connectors/<isv-slug>/` path.** In practice it often creates its own folder using its own naming convention — common patterns observed:

- `sentinel-connectors/<Company>_CCF/` (most common — `@sentinel`'s default root)
- `<Company>_CCF/` at workspace root
- `<Company>-connector/` at workspace root
- The pinned `connectors/<isv-slug>/` (when `@sentinel` does follow the prompt)

**Search strategy — try in this order, take the first non-empty hit:**

```bash
# 1. Pinned location (best case)
ls connectors/<isv-slug>/DataConnectorDefinition.json 2>/dev/null

# 2. @sentinel's default root
find sentinel-connectors -maxdepth 2 -name DataConnectorDefinition.json 2>/dev/null

# 3. Anywhere in the workspace, top 3 levels (catches *_CCF/, *-connector/, etc.)
find . -maxdepth 3 -name DataConnectorDefinition.json -not -path './.git/*' 2>/dev/null
```

Once found, record the actual location to `config/progress.json.connectorBuildFolderActual` (alongside the pinned `connectorBuildFolder`) and use **that** path for the rest of Phase 0. **Do not move or rename the files** — `@sentinel` may reference them by name in follow-up runs, and the dev can find them where `@sentinel` put them.

> **Tip to surface to the developer when you find a non-pinned location:** "`@sentinel` generated files at `<actual-path>` instead of the pinned `connectors/<isv-slug>/` — that's `@sentinel`'s default behavior. Using `<actual-path>` as the source of truth from here on."

Typical layout (regardless of which root folder `@sentinel` chose):

```
<actual-folder>/
├── DataConnectorDefinition.json     # connector definition (Sentinel UI surface)
├── PollingConfig.json               # REST API polling rules
├── DataCollectionRules/
│   └── <Company>_DCR.json           # DCR transform
├── Tables/
│   └── <Company>Events_CL.json      # custom table schema
└── arm-template.json                # deploy-ready ARM template
```

Read each file and confirm:

1. **`DataConnectorDefinition.json`** — has a sane `title`, `publisher`, `descriptionMarkdown`, and `dataTypes[].name` ending in `_CL`.
2. **`Tables/*.json`** — column list matches the API docs' event schema; types are sensible (`string`, `dynamic`, `datetime`, `int`, `bool`).
3. **`DataCollectionRules/*.json`** — `streams[]`, `transformKql`, and `outputStream` align with the table.
4. **`PollingConfig.json`** — auth method, paging, and schedule match the ISV API.

If anything looks wrong, **compose the exact follow-up `@sentinel` prompt for the developer** to paste in this same chat — do not tell them generically to "iterate". Use the **actual folder path** (from `connectorBuildFolderActual`) in the prompt, not the pinned one. Examples:

- `@sentinel rename <actual-folder>/Tables/<Old>_CL.json to <Company>SecurityEvents_CL.json and update references in DataCollectionRules/*.json`
- `@sentinel change polling interval in <actual-folder>/PollingConfig.json from 15m to 5m`
- `@sentinel add a top-level field `riskScore` (int) to <actual-folder>/Tables/<Company>Events_CL.json and the DCR transform`

Do not hand-edit until the build is complete.

---

## Step 3.5 — Pre-deploy static lint  *(backend; gates Step 4)*

Before sending the developer to **Test Connector**, statically verify that `@sentinel` actually honored the Requirements block from Step 2. Every failure here turns into a *specific* follow-up `@sentinel` prompt — not a generic "iterate" — and prevents the developer from burning a deploy + ingestion cycle to discover the same bug at runtime.

**Preferred invocation — `scripts/Test-CcfConnector.ps1`.** The script wraps all five checks below, reads `connectorBuildFolderActual` + `connectorMeta` from `progress.json` (or accepts both inline), emits structured `checks[]` with `name/pass/severity/evidence/fix`, and exits 0/1/2/3:

```pwsh
pwsh scripts/Test-CcfConnector.ps1 -JsonOutput
```

On `pass: false`, take the first failing check's `fix` field and compose the follow-up `@sentinel` prompt for the developer. The inline `bash` checks below remain as the canonical specification of what the script enforces — read them when debugging an unexpected lint result.

Run all checks against the **actual** generated folder (`progress.json.connectorBuildFolderActual`), not the pinned path. Each check maps 1:1 to a Step 2 Requirement:

```bash
ACTUAL=$(jq -r .connectorBuildFolderActual config/progress.json)
DCR=$(ls $ACTUAL/DataCollectionRules/*.json 2>/dev/null | head -1)
POLL="$ACTUAL/PollingConfig.json"
META=$(jq -r .connectorMeta config/progress.json)

ENVELOPE=$(echo "$META" | jq -r .responseEnvelope)
FILTER_PARAM=$(echo "$META" | jq -r .timeFilterParam)
TERMINATOR=$(echo "$META" | jq -r .paginationTerminator)
CADENCE=$(echo "$META" | jq -r .pollCadenceMin)
```

**Check 1 — JSON:API stream shape** (skip if `responseEnvelope != "json-api"`):

```bash
# streamDeclarations must declare attributes + relationships as dynamic
jq -e '.[].properties.streamDeclarations
       | to_entries[].value.columns
       | map(.name) as $cols
       | ($cols | index("attributes")) and ($cols | index("relationships"))' "$DCR" \
  || echo "FAIL: JSON:API stream missing attributes/relationships dynamic columns"

# transformKql must reference attributes.* and not invent top-level fields
grep -E "tostring\(attributes\.|attributes\." "$DCR" >/dev/null \
  || echo "FAIL: transformKql does not read from attributes.* — every row will have null business fields"

# TimeGenerated must coalesce from the source timestamp
grep -E "TimeGenerated\s*=\s*coalesce\(todatetime" "$DCR" >/dev/null \
  || echo "WARN: TimeGenerated does not coalesce from source timestamp — rows will use ingest time"
```

**Check 2 — Exact time-filter param name:**

```bash
grep -F "$FILTER_PARAM" "$POLL" >/dev/null \
  || echo "FAIL: PollingConfig does not use the documented filter param '$FILTER_PARAM' — every poll will re-fetch the full list"
```

**Check 3 — Pagination terminator declared:**

```bash
jq -e --arg t "$TERMINATOR" '.properties.paging
       | (.pagingType // .pagingTypeTemplate // .paginationType)
       | tostring | ascii_downcase | contains($t | gsub("-"; ""))' "$POLL" \
  || echo "FAIL: PollingConfig paging does not declare terminator '$TERMINATOR'"
```

**Check 4 — Poll cadence matches `pollCadenceMin`:**

```bash
ACTUAL_CADENCE=$(jq -r '.properties.pollingFrequency // .properties.queryWindowInMin // empty' "$POLL")
[ "$ACTUAL_CADENCE" = "$CADENCE" ] \
  || echo "FAIL: pollingFrequency=$ACTUAL_CADENCE but connectorMeta.pollCadenceMin=$CADENCE (mismatch multiplies blast radius of any filter bug)"
```

**Check 5 — Sort direction (advisory, not blocking):**

```bash
grep -E "sort.*-" "$POLL" >/dev/null \
  || echo "WARN: no descending sort declared — offset pagination cannot terminate early on first old record"
```

**On any FAIL:** do NOT proceed to Step 4. Compose the exact follow-up `@sentinel` prompt for the developer to paste in this same chat, substituting the actual filenames and the actual offending value. Examples (use the real values, not these placeholders):

- `@sentinel the streamDeclarations in <actual-path>/DataCollectionRules/<file>.json must declare 'attributes' and 'relationships' as dynamic columns because this API returns JSON:API envelope; regenerate the DCR so transformKql reads from attributes.<field> and uses TimeGenerated = coalesce(todatetime(tostring(attributes.<timestamp>)), now())`
- `@sentinel the time filter in <actual-path>/PollingConfig.json uses '<wrong-param>' but the docs require '<correct-param>'; regenerate the queryParametersTemplate with the correct param name`
- `@sentinel the paging block in <actual-path>/PollingConfig.json has no terminator; add 'pagingType: <terminator>' so the poller stops on <stop-condition>`

Persist `phases.0_isv_identification.connectorLintResult: { ranAt, checks: [{name, pass, fix?}], allPass }` to `config/progress.json`. Re-run the lint after each `@sentinel` round-trip until all checks pass, then proceed to Step 4.

---

## Step 4 — Validate the connector against the live API  *(approval gate 3 — VS Code UI click)*

The Test Connector pane is a VS Code UI surface that requires the developer to paste API auth and click Connect — there's no programmatic equivalent today. Tell the developer:

1. Right-click `connectors/<isv-slug>/` in the VS Code Explorer → **Microsoft Sentinel** → **Test Connector**.
2. In the **Test Connector** pane, paste the API auth (token, key, or OAuth client) and click **Connect**.
3. Watch the **Events** tab — confirm rows are returned and the request headers match the API docs.
4. Click **Disconnect** when satisfied.

> **What this proves vs doesn't:** The Test Connector flow validates that the API call succeeds and returns events. It does **not** confirm rows reach the Sentinel table — that is verified after deploy in Step 6.

If `Connect` fails (4xx/5xx), **compose the exact follow-up `@sentinel` prompt** for them inline (e.g., "send this next: `@sentinel polling returned 401, API expects 'Authorization: Bearer <token>' not 'X-Api-Key', regenerate connectors/<isv-slug>/PollingConfig.json`"). Do NOT tell them to "iterate with `@sentinel`" without composing the exact prompt.

---

## Step 5 — Deploy the connector to the workspace  *(backend after approval gate 4)*

Prefer the backend path so the agent can capture deploy outputs reliably and re-use them in Phase 3.

**Auto-discover target context — do NOT ask the developer to type subscription / RG / workspace.** Resolve silently:

1. **Subscription**: `az account show --query id -o tsv` (currently-active sub from the dev's `az login`). If `progress.json.phases.2_data_lake_onboarding.subscriptionId` is already set, prefer that.
2. **Resource group + workspace**: prefer `progress.json.phases.2_data_lake_onboarding.workspace.{resourceGroup,name}` if Phase 2 has already run. Otherwise enumerate `az resource list --resource-type Microsoft.OperationalInsights/workspaces -o json` and filter to Sentinel-onboarded workspaces. **Only ask the developer if more than one candidate exists** — single match = silent auto-pick.

**Approval gate 4** — show the developer the *resolved* context (don't ask them to fill it in):

> Ready to deploy to:
>   • Subscription: `<auto-resolved-sub>`
>   • Resource group: `<auto-resolved-rg>`
>   • Workspace: `<auto-resolved-ws>`
>
> This will create a Data Collection Endpoint, a Data Collection Rule, and the custom table `<Company>Events_CL`. Reply `yes` to proceed or paste a different RG/workspace to override.

On approval, deploy via Azure CLI against the generated ARM template:

```bash
az deployment group create \
  --resource-group <auto-resolved-rg> \
  --template-file <actual-path>/arm-template.json \
  --parameters workspaceName=<auto-resolved-ws> location=<region> \
  --query 'properties.outputs' -o json
```

Parse the deployment outputs and capture:
- `dataCollectionEndpointId` (DCE resource ID)
- `dataCollectionRuleId` (DCR resource ID)
- `customTable` (e.g., `<Company>Events_CL`)
- `immutableId` (DCR immutable ID — needed by ingestion in Phase 3)

**If the developer deployed via the VS Code Deploy button before approval gate 4** (skipping the backend path), do NOT ask them for sub/RG/workspace or deployment IDs. Auto-discover from the same resolved context:

```bash
# Most recently created DCE in the target RG
az resource list -g <auto-resolved-rg> \
  --resource-type Microsoft.Insights/dataCollectionEndpoints \
  --query "sort_by([], &createdTime)[-1].id" -o tsv

# Most recently created DCR in the target RG
az resource list -g <auto-resolved-rg> \
  --resource-type Microsoft.Insights/dataCollectionRules \
  --query "sort_by([], &createdTime)[-1].id" -o tsv

# Confirm the custom table exists
az monitor log-analytics workspace table show \
  -g <auto-resolved-rg> --workspace-name <auto-resolved-ws> \
  --name <Company>Events_CL --query name -o tsv
```

Only fall back to asking the developer if Azure returns ambiguous results (multiple newly-created DCEs in the same RG, etc.). Otherwise persist the IDs silently and continue.

If `<actual-path>/arm-template.json` is missing from the generated set, fall back to the VS Code UI deploy:
- In the chat window, click **Deploy**, choose the workspace, click **Deploy**.
- Right-click `<actual-path>` → **Microsoft Sentinel** → **Deploy Connector** → choose workspace.
- Then run the auto-discovery commands above against `<auto-resolved-rg>` — do **not** ask the developer to paste IDs.

Save these to `config/progress.json` so Phase 3 Branch A can reuse them (no need to re-create DCE/DCR/table — the builder already did it).

---

## Step 6 — Re-enter Phase 0 step 4 to extract the schema

The connector now exists in the user's local folder, not in `Azure/Azure-Sentinel/Solutions`. Treat the generated files as the **connector source of truth** and run the Phase 0 step 4 schema extraction against them:

- **Connector JSON** → `connectors/<isv-slug>/DataConnectorDefinition.json` (read `dataTypes[].name` — this will end in `_CL` so `connectorType: "custom-table"`)
- **Schema** → `connectors/<isv-slug>/Tables/*.json` (column list)
- **Parsers / Analytic Rules / Hunting Queries** — there are **none** at this stage (the builder doesn't generate detections). Phase 5 will author detections from scratch using the use-case brief.

Save to `config/isv-schema.json`:

```json
{
  "connectorType": "custom-table",
  "connectorSource": "custom-built",
  "table": "<Company>Events_CL",
  "columns": [{"name": "...", "type": "..."}],
  "keyColumnsUsedByDetections": [],
  "presentFolders": ["DataConnectorDefinition", "Tables", "DataCollectionRules"],
  "missingFolders": ["Parsers", "Analytic Rules", "Hunting Queries"]
}
```

`keyColumnsUsedByDetections` is empty here because there are no shipped analytic rules — Phase 1 (use-case ideation) will determine which columns matter, and Phase 5 will author the detection KQL.

---

## Step 6.5 — Post-deploy cost-burn check  *(propose to developer; do NOT silently run)*

The Step 3.5 lint catches the *shape* of the most expensive bugs at author time, but the only ground-truth signal that ingestion is sane is **row count vs the developer's expected daily volume**. Surface this proactively about **60 minutes after first deploy** — long enough for ingestion to be steady-state, early enough that a runaway connector hasn't burned a day of Pay-As-You-Go ingestion (~$2.99/GB) yet.

**Tell the developer, verbatim:**

> Your connector has been deployed for ~1 hour. I'd like to run a quick cost-burn check against the live table to confirm ingestion is in the expected range. Reply `yes` to run, or `skip` to defer until later.

**Preferred invocation on `yes` — `scripts/Watch-ConnectorIngestion.ps1`.** The script wraps the query + threshold + projection math below, reads workspace + table + expected-volume from `progress.json` (or accepts them inline), and exits 0/1/2/3:

```pwsh
pwsh scripts/Watch-ConnectorIngestion.ps1 -JsonOutput
```

On `verdict: over-threshold`, the script returns a `diagnosticChecklist[]` of the most likely root causes — surface them to the developer along with the exact `@sentinel` fix prompt for the first failing check from `Test-CcfConnector.ps1`. The inline `bash` block below remains as the canonical specification of what the script computes.

On `yes`, query the workspace and compare against `connectorMeta.expectedDailyVolume`:

```bash
TABLE=$(jq -r .customTable config/progress.json)
WS=$(jq -r .phases.2_data_lake_onboarding.workspace.customerId config/progress.json)
EXPECTED_DAILY=$(jq -r .connectorMeta.expectedDailyVolume config/progress.json)

# Row count in the last hour
ROWS_LAST_HOUR=$(az monitor log-analytics query \
  --workspace "$WS" \
  --analytics-query "$TABLE | where TimeGenerated > ago(1h) | count" \
  --query "tables[0].rows[0][0]" -o tsv)

# Hourly threshold = 2× steady-state hourly average (allows for early-deploy backfill)
HOURLY_THRESHOLD=$(( EXPECTED_DAILY / 24 * 2 ))

echo "Rows ingested in last hour: $ROWS_LAST_HOUR"
echo "Threshold (2× hourly steady-state): $HOURLY_THRESHOLD"
```

Then surface one of these to the developer (calculate the actual values; do not echo the template literally):

- **Within range** (`ROWS_LAST_HOUR <= HOURLY_THRESHOLD`): "Ingestion is within the expected range (`<rows>` rows last hour vs `<threshold>` threshold). At this rate, daily ingest ≈ `<rows × 24>` rows, estimated cost ≈ `$<rows × 24 × avg-row-bytes / 1e9 × 2.99>/day` at $2.99/GB Pay-As-You-Go. Connector looks healthy — moving on."

- **Over threshold** (`ROWS_LAST_HOUR > HOURLY_THRESHOLD`): "⚠️ Ingestion is **`<X×>` over expected baseline** (`<rows>` rows in the last hour vs `<threshold>` threshold). At this rate, daily ingest ≈ `<rows × 24>` rows, estimated cost ≈ `$<projected>/day`. This pattern almost always means one of:
  > 1. **Time-window filter is being dropped by the API** — the documented param name (`<timeFilterParam>`) may be wrong or URL-encoding is off. Every poll is re-fetching the full unfiltered list.
  > 2. **Pagination has no terminator** — offset paging loops forever.
  > 3. **Poll cadence is too aggressive** for the documented volume (currently `<pollCadenceMin>` min).
  >
  > Want me to re-run the Step 3.5 lint and compose the exact `@sentinel` fix prompt? Reply `yes` to investigate now, or `accept` if this is expected one-time backfill."

Persist `phases.0_isv_identification.costBurnCheck: { ranAt, rowsLastHour, hourlyThreshold, expectedDaily, verdict: "within-range" | "over-threshold" | "skipped", estimatedDailyCostUsd }` to `config/progress.json`.

**Forbidden:**
- Silently running the cost-burn query without the developer's `yes` — they may be in the middle of intentional backfill or a load test.
- Treating "over threshold" as automatic failure — surface the diagnostic checklist, let the developer judge.
- Reporting estimated $/day without showing the math (rows × 24 × avg-row-bytes / 1e9 × $2.99) — the developer needs to be able to sanity-check the projection.

---

## Step 7 — Mark Phase 0 complete and route to Phase 1

Update `config/progress.json` with:

```json
{
  "companyName": "<Company>",
  "connectorRepoPath": null,
  "connectorSource": "custom-built",
  "connectorSelected": true,
  "connectorType": "custom-table",
  "customSchema": false,
  "apiDocUrls": ["<url>", "..."],
  "customConnectorBuilt": true,
  "dataCollectionEndpointId": "...",
  "dataCollectionRuleId": "...",
  "customTable": "<Company>Events_CL"
}
```

Note `customSchema: false` — the schema comes from the builder-generated table JSON, not from a developer-defined-from-scratch schema. Set `customSchema: true` only when the developer declines the connector-builder path entirely and wants to hand-author the schema.

Phase 3 routes to **Branch A (Custom table)** with one shortcut: **DCE/DCR/table already exist**, so skip the `az monitor data-collection endpoint create` / `az monitor log-analytics workspace table create` / DCR creation steps and jump straight to **role assignment + sample data ingestion** (steps 5–7 of Branch A).

---

## Failure modes & fallbacks

| Symptom | Cause | Fix |
|---|---|---|
| `@sentinel` not recognized in chat | Sentinel VS Code extension missing or Copilot Chat not in Agent mode | Install `ms-security.ms-sentinel`, reload VS Code, switch chat to Agent mode |
| Build hangs > 10 min on one file | Model is not Claude Sonnet 4.5+ | Switch model in Copilot Chat picker; restart prompt |
| Test Connector returns 401 | Auth header format wrong | Compose the exact follow-up for the dev to send in this same chat: `@sentinel API expects 'Authorization: Bearer <token>' not 'X-Api-Key', regenerate connectors/<isv-slug>/PollingConfig.json` |
| `@sentinel` wrote files to `sentinel-connectors/<X>_CCF/` or `<Company>_CCF/` instead of the pinned `connectors/<isv-slug>/` | **Expected** — `@sentinel` often ignores the pinned path and uses its own default folder | Run the Step 3 search strategy (try `connectors/<isv-slug>/`, then `sentinel-connectors/`, then a top-3-level `find` for `DataConnectorDefinition.json`). Record the actual location to `progress.json.connectorBuildFolderActual` and use it as the source of truth for the rest of Phase 0. Do **not** move/rename — leave the files where `@sentinel` put them. |
| Deploy fails: `Insufficient permissions` | Caller lacks Sentinel Contributor on workspace | Grant role and retry — see Prerequisites |
| API has no public docs and developer can't share | No buildable connector | Fall back: ask developer to define the table schema by hand → set `customSchema: true`, `connectorType: none`, skip the builder agent, proceed to Phase 3 Branch A with developer-provided columns |
| ISV API requires unsupported auth (mTLS, SAML) | CCF doesn't support it | Out of scope for `@sentinel` — escalate to azuresentinelpartner@microsoft.com for a code-based connector |

---

## Quick reference — developer touchpoints (only 4)

The agent runs everything else backend, all in one VS Code Copilot Chat session — no window or workspace switch. Tell the developer up front: "You'll see four prompts from me — pick a doc, send one chat message to `@sentinel`, click Test Connector, approve deploy. I'll handle the rest."

1. **Approval gate 1 (Step 1):** "Looking up <Company>'s public API docs… here are the candidates I found, which should I use?"
2. **Approval gate 2 (Step 2):** "Send the block below as your **next message in this same chat** — `@sentinel /create-connector …`. Reply `done` when generation finishes; I'll auto-detect and pick back up." (The `connectors/<isv-slug>/` folder is auto-created inside the open workspace; no Add-Folder-to-Workspace step is required.)
3. **(Backend, Step 3):** Agent auto-globs `connectors/<isv-slug>/`, reports the schema, composes any follow-up `@sentinel` prompts inline.
4. **Approval gate 3 (Step 4):** "Right-click `connectors/<isv-slug>/` → Microsoft Sentinel → Test Connector. Paste the auth and confirm events flow. Reply `ok` when satisfied."
5. **Approval gate 4 (Step 5):** "Ready to deploy DCE, DCR, and `<Company>Events_CL` to `<sub>/<rg>/<ws>` from `connectors/<isv-slug>/arm-template.json`?"
6. **(Backend, Steps 6–7):** Agent saves schema, updates `progress.json`, assigns role, ingests sample data, and reports completion before handing off to Phase 1.
