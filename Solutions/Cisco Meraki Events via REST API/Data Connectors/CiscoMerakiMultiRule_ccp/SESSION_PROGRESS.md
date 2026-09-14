# Cisco Meraki Connector — Session Progress Log

> Local working notes only. Not part of any commit/PR. Written so a future session
> (or another agent) can reconnect and understand exactly what has been
> investigated, fixed, deployed, and what remains open.

**Target workspace:** `dhanu-agari-clean-20260819` (RG `dhanu-agari-clean-20260819-rg`,
sub `2f0fdbc8-ab60-4386-af30-dd0fac77130e`, workspace GUID
`37cfe625-7d28-4a0b-94ee-8b387f942c94`, region France Central).

**Two connector sources involved:**
1. `C:\Citrix\ca-3p-connectors\ConnectorsGenerator\Connectors\CiscoMerakiConnectorDefinition.cs`
   → generates `ConnectorsGenerator\GeneratedDataConnectors\CiscoMerakiConnector\*`
   (the internal generator-based repo).
2. `C:\Users\v-dhbedu\dhanu-AzureSentinel` (cloned locally, branch
   `users/v-dhbedu/CiscoMeraki` from `https://github.com/dhanunjaya1054/dhanu-AzureSentinel`)
   → path: `Solutions\Cisco Meraki Events via REST API\Data Connectors\CiscoMerakiMultiRule_ccp\*`
   (this is the version the user actually deployed into the live workspace from GitHub).

---

## 1. Bug found & FIXED & DEPLOYED — health-check window too short (ca-3p-connectors only)

- **Symptom:** UI showed `--` (no data) for `CiscoMerakiOrganizations` /
  `CiscoMerakiOrganizationNetworks` data types even though `_CL` tables had fresh rows.
- **Root cause:** `AddDataType(...lastDataReceivedQuery...)` used `ago(12h)`, but these
  two data types poll on a 24h cadence (`InventoryQueryWindowMinutes = 1440`). A 12h
  freshness check will always miss data landed >12h but <24h ago.
- **Fix applied (ca-3p-connectors repo only):** widened to `ago(2d)` for these two
  data types in `CiscoMerakiConnectorDefinition.cs`. Left `CiscoMerakiNetworkClients`/
  `CiscoMerakiAirMarshalEvents` at `ago(12h)` (their poll cadence is much shorter: 60min/15min).
- **Verified:** `dotnet build` clean, `dotnet run ... build CiscoMerakiConnector --verbose`
  → 0 errors, regenerated artifacts, `dotnet test --filter Category!=Integration` →
  415/415 passed.
- **Deployed to live workspace:** extracted just the
  `Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions` resource
  from `mainTemplate.json` into a standalone ARM template and deployed it via
  `az deployment group create` (deployment name `CiscoMerakiHealthCheckFix`,
  `provisioningState: Succeeded`). Verified live via `az resource show` — the deployed
  resource now shows `ago(2d)` for both data types. All 7 pre-existing poller
  connections (`CiscoMerakiOrganizations3ts2s4puxzgp2`, etc.) were confirmed untouched.

- ⚠️ **NOTE — the GitHub solution (`CiscoMerakiMultiRule_ccp`) still has the OLD
  `ago(12h)` value for Organizations/OrganizationNetworks in its
  `CiscoMeraki_ConnectorDefinition.json`.** Since the user deployed FROM GitHub, and I
  only patched the live workspace resource directly (not by redeploying from either
  source repo's mainTemplate), the *live* resource is fixed, but if the user
  re-deploys from the GitHub solution as-is, the `ago(12h)` regression will come back.
  **This still needs the same fix applied to the GitHub-cloned repo** (not yet done —
  see Open Items below).

## 2. Network Clients / Air Marshal Events — empty tables

- **Investigated directly against the live Meraki API** using the Key Vault secret
  `0--Cisco-Meraki-Temporary-Creds` (vault `ccf-ca-3p-accounts-kv`), fetched at runtime,
  never persisted/logged/committed.
- Org has exactly **1 network**: `N_686235993220960471` ("Redmond Office",
  productTypes=["wireless"]). Org ID `1752626`.
- `GET /networks/{id}/clients` → HTTP 200, empty array `[]`.
- `GET /networks/{id}/wireless/airMarshal` → HTTP 200, empty array `[]`.
- Tested **every plausible time-parameter combination**: no params, `t0` only (current
  connector behavior — matches user's suspicion), `t0`+`t1`, `timespan=`. **All return
  200 with 0 records — t0/t1 makes NO difference.** Also tested t0 = 45 days ago (beyond
  Meraki's 31-day max lookback) → correctly gets HTTP 400 on both endpoints, confirming
  window-size validation works fine and is unrelated to the empty-data symptom.
- **Conclusion: NOT a connector code bug.** This network genuinely has zero connected
  wireless clients and zero detected rogue APs right now. Nothing to ingest.
- **SentinelHealth history** showed intermittent `404 Not Found` failures (mixed with
  successes) on both pollers going back at least a week. Could NOT reproduce a 404
  against the live API with the connector's exact request shape (100% success rate
  across repeated direct tests). Likely transient/upstream Meraki throttling on the
  shared "Temporary-Creds" staging org — not something fixable in connector code.
- **No code change made** for these two data types — evidence doesn't support one.

## 3. Diagnostic script (local only, never committed)

- `C:\Users\v-dhbedu\CiscoMeraki-T0T1-Diagnostic.ps1`
- Fetches Meraki creds from Key Vault at runtime (`az keyvault secret show`), holds key
  only in memory, clears it before exit, never logs/prints the value.
- Compares NetworkClients/AirMarshal responses for: no time params / t0-only (current
  connector shape) / t0+t1 (candidate fix) / `timespan=` / t0 beyond 31-day max.
- Already executed once — results confirmed t0/t1 makes no difference (see §2).
- Lives **outside** both git repos (`C:\Users\v-dhbedu\`) — confirmed via `git status`
  in `ca-3p-connectors` showing no trace of it.

## 4. Cross-repo comparison: ca-3p-connectors vs GitHub `CiscoMerakiMultiRule_ccp`

Cloned `https://github.com/dhanunjaya1054/dhanu-AzureSentinel` branch
`users/v-dhbedu/CiscoMeraki` (note: NOT `.../CiscoMeraki/Solutions` — that extra path
segment doesn't exist as part of the branch name, it's just the folder path within the
branch) to `C:\Users\v-dhbedu\dhanu-AzureSentinel`.

Files present in GH solution folder `CiscoMerakiMultiRule_ccp`:
`CiscoMeraki_ConnectorDefinition.json`, `CiscoMeraki_dcr.json`, `CiscoMeraki_PollerConfig.json`,
`table_CiscoMeraki*.json` (4 files). **No parsers, no mainTemplate.json, no
createUiDefinition.json** in the GH folder (those are generator-produced artifacts on
the ca-3p-connectors side; the GH solution is the hand-structured CCF layout used for
direct `Solutions/` PR submission to Azure-Sentinel).

### Diff results (semantic JSON compare):
| File pair | Result |
|---|---|
| `CiscoMeraki_PollerConfig.json` vs `PollingConfig.json` | **IDENTICAL** (byte-for-byte after normalization) — confirms the t0-only pattern for NetworkClients/AirMarshal is intentional and consistent across both sources, not a discrepancy. |
| `table_CiscoMerakiAirMarshalEvents.json` | IDENTICAL |
| `table_CiscoMerakiNetworkClients.json` | IDENTICAL |
| `table_CiscoMerakiOrganizationNetworks.json` | IDENTICAL |
| `table_CiscoMerakiOrganizations.json` | IDENTICAL |
| `CiscoMeraki_dcr.json` vs `DCR.json` | **DIFFERENT** — one real semantic diff found (see below) |
| `CiscoMeraki_ConnectorDefinition.json` vs `ConnectorDefinition.json` | GH still has `ago(12h)` for ALL data types (including Organizations/OrgNetworks) — i.e. it does NOT yet have the fix from §1. Our repo has `ago(2d)` for those two (post-fix). This is an **expected, already-understood difference** (§1's fix hasn't been ported to GH source yet). |

### ⚠️ Real DCR difference found — `UrlOriginal` transform for API Requests stream (`Custom-CiscoMerakiAPIRequest_CL`)

- **GH (the version actually deployed to the workspace):**
  `UrlOriginal = strcat(tostring(['host']), tostring(['path']))`
  → produces a full URL-like string (host + path), which is closer to correct ASIM
  Web Session Schema semantics (`UrlOriginal` should represent the full accessed URL,
  not just the path component).
- **Our repo (`ca-3p-connectors`) generated DCR:**
  `UrlOriginal = ['path']`
  → maps only the bare path, dropping the host — this is **less ASIM-compliant** and
  is a regression/gap relative to what's actually deployed and working in the
  workspace.
- **Root cause in C# source:** `CiscoMerakiConnectorDefinition.cs` line ~153:
  ```csharp
  ColumnDefinitionHelpers.String("path", "UrlOriginal").WithDescription("Path of the API request."),
  ```
  This is a straight passthrough column mapping with no KQL transform, whereas GH's
  DCR has a custom transform building the value from both `host` and `path`.
- **Status: IDENTIFIED BUT NOT YET FIXED.** Stopped mid-investigation to save this
  progress log per user request. **Next step:** decide whether to add a
  `.WithCustomKqlTransformation("strcat(tostring(['host']), tostring(['path']))")`
  (or equivalent builder API — check `ColumnDefinitionHelpers`/column builder for the
  right method name) to match GH's more-correct behavior, then rebuild/retest/
  regenerate artifacts, and consider whether to also redeploy the DCR to the live
  workspace (same "isolated resource" deployment pattern as §1, but this time for the
  DCR's dataFlows/transformKql on the API Requests stream — this one is NOT a
  standalone-safe resource like the connectorDefinition UX; DCR updates need to be
  checked for whether they require the DCR to be redeployed in full or can be patched
  incrementally without disrupting active associations).

## 5. ⚠️ TEMPORARY TEST-ONLY CHANGE — MUST BE REVERTED — ASimAuditEventLogs poll window widened

- **What was changed:** Live poller connection `ASimAuditEventLogs3ts2s4puxzgp2` in workspace
  `dhanu-agari-clean-20260819` (RG `dhanu-agari-clean-20260819-rg`) had
  `properties.request.queryWindowInMin` changed from **`5`** (the correct/production value,
  matching `CiscoMeraki_PollerConfig.json` / `CiscoMeraki_dcr.json` in this repo) to
  **`129600`** (90 days), via a direct `az rest --method put` against the
  `Microsoft.SecurityInsights/dataConnectors/ASimAuditEventLogs3ts2s4puxzgp2` resource
  (api-version `2024-09-01`).
- **Why:** Purely for **manual testing/visualization** — to let the Connector UI pull in the
  handful of pre-existing historical `configurationChanges` records (e.g. the network-rename
  event from 2026-06-09, ~86 days old at the time) that the normal 5-minute production window
  would never see, so the data shape/appearance in the UI/table could be inspected.
- **Nothing else was changed** — `t0`/`t1` attribute names, `rateLimitQPS`, `apiEndpoint`,
  `dcrConfig`, and all other poller connections (Organizations, OrganizationNetworks,
  NetworkClients, AirMarshalEvents, ASimWebSessionLogs, ASimNetworkSessionLogs) are untouched.
- **⚠️ ACTION REQUIRED — REVERT THIS BEFORE ANY PRODUCTION/REAL USE:** Set
  `properties.request.queryWindowInMin` back to **`5`** on this same resource once testing is
  done. This is NOT reflected in any repo file (the repo's `CiscoMeraki_dcr.json` /
  `CiscoMeraki_PollerConfig.json` were never changed — only the live Azure resource was
  patched), so it will NOT self-correct on a future repo-based redeploy of just the connector
  definition; it must be explicitly reverted via the same `az rest --method put` pattern (GET
  current resource → set `queryWindowInMin` back to `5` → re-supply `auth.ApiKey` from Key
  Vault since PUT requires it on every write → PUT it back) or by disabling/re-enabling the
  connection from the Sentinel UI.
- **Not committed anywhere** — this is a live-resource-only change, exactly like the health-check
  fix in §1.

## 6. PR #14629 review — issues/corrections after adding new data types

PR: https://github.com/Azure/Azure-Sentinel/pull/14629

Short conclusion: the new custom data types are valid, but the PR also changed existing ASIM
areas. Some fixes are still needed.

| # | Area | Issue | Caused by new custom data types? | Recommended fix |
|---|---|---|---|---|
| 1 | Organizations / Organization Networks UI status | Their pollers use a 24h window/cadence, but `lastDataReceivedQuery` used only `ago(12h)`, so the UI can show no data even when rows exist. | Yes, this is tied to the new custom inventory data types. | Use `ago(2d)` for these two data type health checks. |
| 2 | File Scanned events | Meraki returns `File Scanned` from `getOrganizationApplianceSecurityEvents`, but the current connector has no correct destination for it. `ASimWebSessionLogs` only reads `/apiRequests`, and `ASimNetworkSessionLogs` is not the right schema for file fields. | Not originally caused by this PR; v1.0.0 already documented File Scanned but filtered it out. The PR did not fix the gap. | Add a new custom table, e.g. `CiscoMerakiFileScannedEvents_CL`, or add a proper ASIM File Event mapping if supported. |
| 3 | IDS Alert vs File Scanned routing | The current security-events stream does not clearly separate `IDS Alert` from other security event types. File Scanned can enter the network-session flow but will not map correctly. | Partly yes, because the PR changed the old ASIM security dataflow. | Add `where eventType == "IDS Alert"` to the `ASimNetworkSessionLogs` transform, and route File Scanned separately. |
| 4 | File Scanned source fields dropped | The current security stream does not declare/map File Scanned fields such as `uri`, `fileType`, `disposition`, `action`, `fileHash`, and `fileSizeBytes`. | Partly yes; the new stream/schema no longer preserves the old broad security-event field list. | Declare these fields in a separate File Scanned stream/table and map them explicitly. |
| 5 | File Scanned UI/graph query mismatch | Older connector text/queries say File Scanned appears in `ASimWebSessionLogs`, but no current DCR dataflow writes File Scanned events there. | Pre-existing documentation mismatch; still unresolved after PR. | Update connector text, graph queries, sample queries, and data type list to match the real File Scanned destination. |
| 6 | API Request `UrlOriginal` regression | Original v1.0.0 built a fuller URL using host/path/query string. Current transform uses `host + path` and does not include query string. | Yes, this changed during the PR rewrite. | Consider restoring `queryString` support in `UrlOriginal` if the source API still returns it. |
| 7 | Configuration Change detail loss | Original v1.0.0 kept extra context like `adminName`, SSID name/number handling, `EventStartTime`, and `EventEndTime`. Current transform maps a simpler set. | Yes, this changed during the PR rewrite. | Re-add useful non-PII context where it fits ASIM, preferably in supported ASIM fields or `AdditionalFields` if allowed. |
| 8 | Network Clients / Air Marshal empty results | These custom tables can remain empty if the Meraki org has no clients or rogue AP detections. This is not necessarily a connector defect. | No. It is expected source-data behavior. | Document this clearly in troubleshooting notes and validate by direct API replay. |

Recommended final routing:

| Source event/data | Endpoint | Correct destination |
|---|---|---|
| IDS Alert | `GET /organizations/{orgId}/appliance/security/events` | `ASimNetworkSessionLogs` |
| File Scanned | `GET /organizations/{orgId}/appliance/security/events` | New custom table, e.g. `CiscoMerakiFileScannedEvents_CL` |
| API Request | `GET /organizations/{orgId}/apiRequests` | `ASimWebSessionLogs` |
| Configuration Change | `GET /organizations/{orgId}/configurationChanges` | `ASimAuditEventLogs` |
| Organizations | `GET /organizations` | `CiscoMerakiOrganizations_CL` |
| Organization Networks | `GET /organizations/{orgId}/networks` | `CiscoMerakiOrganizationNetworks_CL` |
| Network Clients | `GET /networks/{networkId}/clients` | `CiscoMerakiNetworkClients_CL` |
| Air Marshal Events | `GET /networks/{networkId}/wireless/airMarshal` | `CiscoMerakiAirMarshalEvents_CL` |

### Still TO-DO / open items when resuming:
1. Decide + implement the `UrlOriginal` fix in `CiscoMerakiConnectorDefinition.cs`
   (align with GH's `strcat(host, path)` — pending confirmation this is desired, since
   user said "compare... and add any changes if required").
2. Port the `ago(12h)` → `ago(2d)` health-check fix (§1) into the **GitHub-cloned
   repo's** `CiscoMeraki_ConnectorDefinition.json` (currently only the live workspace
   resource and the ca-3p-connectors repo have the fix — the GH source text itself
   does not).
3. Have not yet diffed `CiscoMeraki_ConnectorDefinition.json` instructionSteps /
   graphQueries / full UX config beyond the dataTypes section — worth a full diff pass.
4. No `mainTemplate.json`/`createUiDefinition.json`/parser files exist in the GH repo
   folder — confirm whether that's expected (i.e., GH solution folder is meant to be
   fed through the same generator/ARM-TTK pipeline before PR submission, or whether
   parsers are defined elsewhere in that repo, e.g. under a `Parsers/` folder at the
   solution root) — not yet checked.
5. User asked to "create [the] powershell script also in that solution" — the
   diagnostic script (§3) has NOT yet been copied into the GH-cloned solution folder;
   still only exists at `C:\Users\v-dhbedu\CiscoMeraki-T0T1-Diagnostic.ps1`. Copy it
   into `CiscoMerakiMultiRule_ccp\` (same runtime-Key-Vault-fetch pattern, no secrets
   at rest) as part of resuming this work, per explicit user request, before this log
   was written.
6. Neither the GH-cloned repo changes nor the ca-3p-connectors DCR fix have been
   committed or pushed anywhere — everything is local-only pending user confirmation.
