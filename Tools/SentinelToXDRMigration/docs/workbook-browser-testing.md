# Microsoft Sentinel workbook browser testing

Use the [validate-sentinel-workbook-browser skill](../../../.github/skills/validate-sentinel-workbook-browser/SKILL.md)
for workbook-specific browser QA. The primary test surface is the Microsoft
Defender portal, `https://security.microsoft.com`, not the Defender for Cloud
blade in the Azure portal. This workflow tests native Sentinel workbooks as
well as applicable migrated content; browser testing does not itself convert,
package, install or deploy a workbook.

## Relationship to existing validation

- [Workbook authoring instructions](../../../.github/instructions/workbook.instructions.md)
  and the existing workbook template/metadata validators remain authoritative
  for static repository validation.
- [Canonical workbook Qualification](../agent-workflows/end-to-end-migration.md#workbook-qualification-and-browser-qa)
  owns the reviewed query/UI plans, private session binding and acceptance
  gates. The [Qualification flow](qualification-flow-readme.md)
  integrates these checks into solution evidence.
- [Optional solution testing](../../../.github/skills/sentinel-solution-optional-testing/SKILL.md)
  owns separately approved mock ingestion and rule testing. A workbook-only
  browser request does not authorize ingestion, alert parity or deployment.
- Azure/Microsoft-Defender-for-Cloud#1068 supplies useful coverage ideas:
  source-bound smoke, data-panel contracts, drill-through/filter/reset,
  honest pending evidence and optional redacted captures. Its Azure-only
  account-menu and iframe assumptions must not be copied into Defender.

## 1. Offline preparation

Identify the exact source file, commit, workbook/template identity, declared
dependencies, parameters, query items, tabs and conditional groups. Hash the
unchanged file from the repository root:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath "Solutions\<solution>\Workbooks\<workbook>.json"
```

Keep the file hash distinct from hashes of normalized or installed
`serializedData`. If an approved metadata read is used to compare an
installed definition, parse and compare like-for-like definitions and record
both hashes. A resource name or matching title does not prove source equality.
Dynamic ARM expressions must not be evaluated or deployed to obtain a test
copy. An unsupported definition stays blocked.

Plan the checks before looking at live results. Record exact expected column
labels, row-count bounds, parameter values, tab transitions, conditional
visibility and intentionally preserved context. Use benign test identifiers
or private expectations; never commit tenant data or customer rows into a
test profile. Offline regression tests prove the harness, not portal behavior.

## 2. Approve the live scope

Use structured confirmation before accessing the tenant. Display:

- exact non-production tenant, subscription and Sentinel workspace;
- exact installed workbook instance and source version under test;
- initial portal URL and any proposed Azure fallback;
- permitted metadata reads, query scope/time window, controls and bounded
  timeout;
- optional screenshots, masking and private evidence retention.

No response means no live work, including in autopilot. For a selected
Qualification run, reuse its locked target unchanged; configuration is not
consent. User sign-in/MFA and directory selection remain manual. Do not
request or publish credentials, private storage state or browser headers.

Read/observe approval does not authorize **Save**, **Save as**, **Edit**,
Content Hub installation, provisioning, ingestion, alert activation or
cleanup. If the workbook is not already installed, report the prerequisite
and route installation through its independently approved workflow.

## 3. Open and verify the Defender surface

1. After approval, navigate to `https://security.microsoft.com`.
2. In Microsoft Sentinel, select **Threat management > Workbooks** and open
   the agreed installed workbook. The actual navigation may vary with
   onboarding, permissions and portal updates; inspect the current DOM rather
   than guessing routes or selectors.
3. Positively verify the visible authenticated tenant, selected workspace and
   installed workbook identity. A portal URL, workbook title, cached login
   or configured target alone is insufficient. If the portal does not expose
   the necessary identity, stop for verification rather than infer it.
4. Locate the unique workbook document/frame and scope every action to it.
   Do not assume the Azure `Workbooks.ReactView` iframe or Azure account menu
   exists in Defender. Distinguish canonical source identity from installed
   instance identity.
5. Check declared data prerequisites and chosen time window. Microsoft Learn
   also requires Azure Data Explorer authentication from Defender when that
   data source is used. An empty grid does not prove a connector is working.

Some visualizations require **Open in Azure**. Ask before following it,
reverify the same target, and report the fallback separately. An Azure pass
does not close a blocked Defender check. Print/PDF is Azure-only and not part
of the default test.

## 4. Coverage and assertions

| Check | Required observation | Insufficient evidence |
|---|---|---|
| Open/render | Correct workbook identity, stable visible sections, no renderer/query errors | Portal loaded or title matched |
| Parameters | Expected selected value and preserved tenant/workspace/time scope | A click or friendly label alone |
| Data panels | Expected columns, bounded rows and agreed values/aggregates after query completion | Tile present or query HTTP 200 |
| Tabs/conditional | Correct active tab and visible/hidden sections for each agreed state | Only default tab tested |
| Filter/dependent refresh | Changed parameter propagates to resulting data; unrelated context preserved | Input value changed without downstream assertion |
| Drill-through | Selected row exports the expected context and opens the correct detail view/data | Navigation occurred |
| Reset | Target filters/context clear to the specified defaults; unrelated filters preserved | Reset button clicked |
| Reload/layout | Approved reload retains intended scope; agreed elements visible within bounds | Screenshot exists |

Wait for stable matching results within the reviewed timeout and recheck
identity and invariants after each action. Do not automatically retry an
ambiguous control or use a different frame. Capture query errors, failed
requests and workbook JavaScript errors privately and project sanitized
error categories, not raw sensitive payloads.

Treat no-data as a distinct outcome requiring the agreed empty-state
expectation. Positive-data tests remain blocked/failed if expected telemetry
is absent. Account for lazy panels, grouping, virtualization and recognized
truncation. Visible rows are not automatically unique backend resources or
complete inventory; accepted truncation must remain a report limitation.

Unobservable hidden parameter state is blocked, not inferred from display
text. Do not alter source queries/defaults/exports or inject probes into a
production workbook. Unsupported controls and assertions remain visible as
blocked/not-run. A manually inspected interaction is not automatically a
machine-verified contract.

## 5. Execute through existing tools

For toolkit-supported selected solution content, use the existing
`workbook-query-plan`, `workbook-query-review`, `workbook-query-execute`,
`workbook-ui-plan`, `workbook-ui-review` and `workbook-ui-execute` commands.
Consult each command's `--help` for its required inputs; the abbreviated
Qualification flow examples are not complete execution contracts.

The reviewed browser configuration must bind the private session hash,
observed identities, exact readiness/guard selectors, allowed navigation and
read-query requests, bounded timeout/viewport, steps and DOM assertions.
Select these from the observed approved page. The runner does not discover
portal selectors or authenticate. Its network guards are not a browser-wide
no-write sandbox; do not run it against an unreviewed portal/session.

The retained CLI entry point is `solution-manager` (also exposed as
`sentinel-xdr-migration`). For a currently eligible, selected workbook, the UI
lifecycle requires explicit local inputs:

```powershell
solution-manager workbook-ui-plan `
  --solution "Solutions\<solution>" --run-id "<run-id>" `
  --workbook "<selected-workbook>" --url "<approved-workbook-url>" `
  --readiness-selectors "<private-selectors.json>" `
  --steps "<private-steps.json>" `
  --background-activity-review "<review-reference>" `
  --browser-config "<private-browser.json>"

solution-manager workbook-ui-review `
  --solution "Solutions\<solution>" --run-id "<run-id>" `
  --plan "<plan.json>" --plan-sha256 "<current-plan-hash>" `
  --actor "<reviewer>" --reference "<approval-reference>" --decision approved

solution-manager workbook-ui-execute `
  --solution "Solutions\<solution>" --run-id "<run-id>" `
  --plan "<plan.json>" --plan-sha256 "<current-plan-hash>" `
  --storage-state "<private-session.json>"
```

Do not put private session files or real lab bindings into source control.
The existing private-session filesystem checks remain in force; a platform
that cannot satisfy them is blocked, not permission to relax permissions.
Only exact HTTPS `security.microsoft.com` and `portal.azure.com` portal hosts
are supported by this adapter. Host lookalikes, credentials, signatures and
malformed ports fail with sanitized errors. The Azure route is still a
separately approved fallback, not an automatic navigation.

Both portals require an observed `workspaceResourceId` when the locked target
contains it; Azure fallback always requires it. Add the exact reviewed
workspace selector to `readinessSelectors.workspace` and a corresponding
`browserConfig.readiness.workspaceResourceId` assertion whose expected value
is the locked ARM resource ID. Missing or mismatched workspace observations
block validation. If also supplied, `workspaceCustomerId` must match its
locked identity. For example, this is the workspace member inside
`browserConfig.readiness`, not a complete configuration:

```json
{
  "workspaceResourceId": {
    "selector": "<reviewed workspace selector>",
    "kind": "attribute",
    "attribute": "<observed identity attribute>",
    "expected": "<exact locked workspaceResourceId>"
  }
}
```

The seven mandatory UI kinds remain unchanged. Optional `data` steps support
exact `text`, ordered `texts`, and integer `count` assertions. For example,
an individual ordered-text assertion in a reviewed data step is:

```json
{"selector":"<unique reviewed result selector>","kind":"texts","expected":["benign row A","benign row B"]}
```

Optional `tabs` steps use a reviewed click selector and assert
`aria-selected="true"` plus the resulting panel. Optional `reset` steps use a
reviewed click/select action, before-action evidence and post-action
assertions proving changed state returned to its baseline, plus resulting
panel assertions. These supplement, not replace, mandatory coverage.
Selectors and expected values must come from the approved workbook and
observed DOM; this guide intentionally supplies no guessed production
bindings or reusable blanket portal/network allowlist.

Example optional reset step (replace placeholders from reviewed observations):

```json
{
  "id": "reset-filter",
  "kind": "reset",
  "action": "select",
  "selector": "<unique reviewed filter selector>",
  "value": "<baseline option>",
  "before": [
    {"selector": "<unique reviewed filter selector>", "kind": "value", "expected": "<changed option>"}
  ],
  "assertions": [
    {"selector": "<unique reviewed filter selector>", "kind": "value", "expected": "<baseline option>"},
    {"selector": "<unique reviewed panel selector>", "kind": "text", "expected": "<baseline panel>"}
  ]
}
```

For standalone Sentinel content or a CLI content scope not supported by the
selected run, use approved Playwright/browser MCP observation without
creating a fake migration or converting the workbook just to test it.
Discover available browser tools; snapshot the page, inspect frames and
unique controls, execute only agreed read/observe interactions and compare
the predetermined expectations. Keep this evidence explicitly
`authenticated-standalone` rather than an accepted toolkit receipt.

The existing `workbook-ui-import` route is only for explicitly reviewed
external captures meeting its complete provenance contract. It does not
launch a browser, and a copied JSON result or self-reported pass must not
bypass that review. A blocked CLI stage remains blocked until its own
contract is satisfied.

## 6. Screenshots and evidence

Screenshots are optional and disabled by default. If requested, use local
conservative redaction with reviewed masks, including parent-page overlays
and the workbook frame. If the available browser tool cannot reliably
isolate/mask that scope, do not capture. Do not relax masking after failure.
Manual masks or unredacted local capture require explicit separate approval.
AI-assisted mask selection must stay within authorized/local inspection,
with user approval before capture; no third-party image upload.

Review the final image before sharing. A navigation, document replacement,
missing mask or capture failure invalidates the image; discard it rather
than publish an exposed fallback. Do not export tokens, cookies, storage
state, account/tenant identifiers, request bodies or customer record values
to PR comments or public evidence.

Keep raw private evidence under the selected ignored run directory, or a
private location explicitly chosen for standalone testing. Publish only
reviewed sanitized projections. Report:

- source revision/hash and separately verified installed-definition binding;
- portal tested and any separately scoped Azure fallback;
- evidence mode and collection time;
- counts and outcomes: passed, failed, blocked, not-run, not-applicable;
- exact tested behavior and sanitized expected/observed assertions;
- no-data, truncation, unsupported controls, masking and coverage limits.

Offline/synthetic success never closes authenticated checks. Smoke success
never proves data contracts. Prior evidence is stale after source, target,
plan or installed instance changes. Browser QA does not establish alert
parity, query semantic equivalence or complete solution Qualification.

## Example chat requests

- "Inspect this Sentinel workbook offline and propose browser checks; do not access Azure."
- "Test this already installed Sentinel workbook in security.microsoft.com in my approved lab. Verify data panels, filter propagation, drill-through and reset; no screenshots or writes."
- "Run the reviewed workbook UI plan for this exact Qualification run. Keep missing browser evidence blocked."
- "Review a local redacted capture and list untested interactions; do not mark it qualified."

The agent must still obtain exact live-scope confirmation for these requests.

## Offline regression validation

Use the toolkit's supported Python 3.11/3.12 environment and existing test
dependencies. From the repository root, run the smallest contract suite:

```powershell
$env:PYTHONPATH = (Resolve-Path "Tools\SentinelToXDRMigration").Path
python -m pytest Tools\SentinelToXDRMigration\tests\test_workbook_browser_contracts.py -q
```

The broader related tests are `test_workbook_browser.py`,
`test_workbook_qualification.py` and `test_qualification_orchestrator.py` in
the same directory. Some existing private-session/evidence checks require
POSIX permissions; the optional browser smoke needs Playwright. Report
platform exclusions and skips explicitly, and run those cases on a supported
platform rather than weakening their contracts. These tests do not sign in
to a tenant or establish actual Defender-portal behavior.

## Official references

- [Visualize Microsoft Sentinel data using workbooks](https://learn.microsoft.com/en-us/azure/sentinel/monitor-your-data)
- [Microsoft Sentinel in the Defender portal](https://learn.microsoft.com/en-us/azure/sentinel/microsoft-sentinel-defender-portal)
- [Manage Azure Monitor workbooks](https://learn.microsoft.com/en-us/azure/azure-monitor/visualize/workbooks-manage)
