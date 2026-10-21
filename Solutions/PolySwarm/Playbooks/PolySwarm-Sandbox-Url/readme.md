# PolySwarm-Sandbox-Url

Detonates every URL entity on a Microsoft Sentinel incident in the PolySwarm sandbox
(CAPE or Triage), polls until the task completes or times out, and writes verdict,
score, malware family, MITRE ATT&CK techniques and a report link back to the incident
as a comment. Never creates an incident.

Two variants, both built and committed:

- `Playbooks/PolySwarm-Sandbox-Url/incident-trigger/azuredeploy.json`, incident-triggered, named
  `PolySwarm-Sandbox-Url-IncidentTriggered`.
- `Playbooks/PolySwarm-Sandbox-Url/entity-trigger/azuredeploy.json`, entity-triggered,
  bound to a single Url entity.

Defaults to your **private** PolySwarm community; refuses to submit to the public
community unless `AllowPublicCommunity` is explicitly set to `true`. See `README.md`,
"Public vs private community".

## Summary

1. Reads the PolySwarm API key from Azure Key Vault through the playbook's managed
   identity.
2. For each Url entity: creates a sandbox task (`POST /sandbox/sandboxtask/instance`),
   uploads the URL string itself as the artifact bytes to the returned presigned
   upload URL (the sandbox VM performs the actual fetch; the client never fetches the
   URL), finalizes the task, then polls
   `GET /sandbox/sandboxtask?sandbox_task_id=...&community=...` until the task leaves
   `PENDING`/`STARTED`/`COLLECTING_DATA` or `TimeoutMinutes` elapses.
3. Derives a verdict from the task's score (see `README.md`, "Sandbox verdict"):
   `KNOWN_GOOD` becomes known good; no score becomes unknown; otherwise compared
   against `MaliciousScoreThreshold` and `SuspiciousScoreThreshold`.
4. Posts a comment with the verdict, score, malware family, MITRE ATT&CK techniques,
   and a best-effort report link.
5. Writes one row to `PolySwarmSandbox_CL` via the Logs Ingestion API for every
   detonation attempt, including timeouts, so the table reflects submissions that
   never reached a clean terminal state as well as ones that did.

This playbook is Microsoft Sentinel incident-triggered rather than triggered directly
off a bare URL feed, unlike some reference vendor playbooks it is modeled on, so it
always has an incident to comment on and never needs a separate analytics rule just to
surface a URL-only detonation.

## Private and internal URLs are refused

Before anything is sent to PolySwarm, the playbook parses the host out of the URL (lowercased, trailing dot removed) and refuses to submit it when the URL points at a private or internal address. The incident gets a comment saying the URL was not submitted because it points at a private or internal address and that submitting it would disclose internal host names to a third party. Nothing is sent to PolySwarm, and the API key is not even read from Key Vault.

Refused:

- Any scheme other than http or https.
- localhost and anything ending in .localhost.
- Single-label host names (no dot), for example intranet.
- Host names ending in .local, .internal, .lan, .corp, .home, .home.arpa or .intranet.
- IPv4 literals in 0.0.0.0/8, 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16, 172.16.0.0/12, 192.168.0.0/16, 192.0.0.0/24, 198.18.0.0/15, and 224.0.0.0 and above.
- Numeric hosts written any other way (short, hexadecimal, leading zeros, or out of range), because they are ambiguous.
- Any IPv6 literal (the host contains a colon or brackets). This is deliberately conservative.

Limit: DNS names that resolve to private addresses are not detected, because Logic Apps has no resolver. A public-looking name that points at an internal address is still submitted.

## No result (HTTP 204)

PolySwarm answers HTTP 204 with an empty body when it has nothing for a request (not found). The status poll checks for 204 explicitly, ends the loop with a NOT_FOUND state and never reads the empty body. The incident gets a comment saying PolySwarm returned no result and no verdict is available, and the PolySwarmSandbox_CL row, where one is written, carries the verdict unknown. Task creation returns 200.

All polling loops are bounded twice: a count limit and a timeout (TimeoutMinutes, default 15 minutes).

## Prerequisites

- A Microsoft Sentinel workspace, and permission to deploy Logic Apps and assign RBAC
  roles.
- A PolySwarm API key with the sandbox detonation entitlement, stored as a secret in
  an Azure Key Vault.
- A private PolySwarm community to detonate in (ask PolySwarm Customer Success if you
  do not have one yet).
- The shared sandbox results infrastructure
  (`Data Connectors/PolySwarmSandboxResults/azuredeploy.json`) deployed first; this
  playbook is one of the writers to that table, since PolySwarm's own sandbox task
  list API does not carry verdicts.

## Parameters

| Parameter | Notes |
| --- | --- |
| `PlaybookName` | Defaults to `PolySwarm-Sandbox-Url-IncidentTriggered`. |
| `Community` | Your private PolySwarm community. No default; required. |
| `AllowPublicCommunity` | Boolean, default `false`. Must be explicitly `true` to submit to the public community. |
| `Provider` | Sandbox provider slug. Default `triage`. Also supports `cape`. |
| `VmSlug` | VM slug within the chosen provider. Default `windows11-21h2-x64`. Current provider/VM catalog (re-check `GET /sandbox/provider/list`, it can change): `cape` has one VM, `win-10-build-19041` (FILE and URL); `triage` has three, `android-11-x64` (FILE only), `ubuntu-22.04-amd64` (FILE, URL), `windows11-21h2-x64` (FILE, URL, the default here). |
| `NetworkEnabled` | Boolean, default `true`. Whether the sandbox VM has network access during detonation. |
| `TimeoutMinutes` | Default `15`. How long to poll before giving up and commenting a timeout. |
| `KeyVaultName` | Name of the Azure Key Vault holding the PolySwarm API key. No default; required. |
| `KeyVaultSecretName` | Defaults to `PolySwarmApiKey`. |
| `PolySwarmApiBaseUrl` | Defaults to `https://api.polyswarm.network/v3`. |
| `MaliciousScoreThreshold` | Default `7` (of a 0-10 score). |
| `SuspiciousScoreThreshold` | Default `4`. |
| `DceLogsIngestionEndpoint` | From the sandbox results infrastructure's `dceLogsIngestionEndpoint` output. No default; required. |
| `DcrImmutableId` | From the same infrastructure's `dcrImmutableId` output. No default; required. |
| `StreamName` | Defaults to `Custom-PolySwarmSandboxResults`. |
| `DcrResourceId` | From the same infrastructure's `dcrResourceId` output. Used as the scope for this playbook's own Monitoring Metrics Publisher role assignment. No default; required. |
| `create_role_assignment` | Boolean, default `true`. Whether the template auto-assigns Monitoring Metrics Publisher on `DcrResourceId` to its own managed identity. |

## Post-deployment steps

1. Assign the **Microsoft Sentinel Responder** role on the resource group (or
   workspace) to this playbook's managed identity.
2. Assign the **Key Vault Secrets User** role on the Key Vault (`KeyVaultName`) to the
   same managed identity.
3. **Monitoring Metrics Publisher** on the Data Collection Rule (`DcrResourceId`) is
   assigned automatically at deployment when `create_role_assignment` is `true`
   (default) and the deploying principal can grant RBAC roles there; otherwise set it
   to `false` and assign the role manually.
4. Authorize the Microsoft Sentinel and Azure Key Vault API connections if they show
   as unauthorized.
5. Attach the playbook to an automation rule (or run it manually from an incident) so
   it runs on incidents with a Url entity. Consider gating the automation rule to
   analyst request only, since detonation is metered and takes minutes.

## What the comment looks like

Sandbox verdict language reads "derived from a 0-10 normalized score", not "PolySwarm's
verdict": there is no categorical verdict field from either sandbox provider, for
either FILE or URL artifacts. The comment includes the derived verdict, the raw score,
malware family and MITRE ATT&CK techniques from the task's report, and the
best-effort report link. `KNOWN_GOOD` results have no score at all (`report: null`);
the comment states this plainly rather than treating it as an error.

## Troubleshooting

See `README.md`, "Troubleshooting". Specific to this playbook:

- The report link
  (`https://polyswarm.network/scan/results/file/{sha256}/{instance_id}`) is
  unconfirmed for a pure-sandbox submission; a hash search on a sandbox-only artifact
  returned HTTP 404 in testing, since that artifact never entered the multi-engine
  scan index. Treat the link in the comment as best effort.
- The literal community value `"public"` is accepted at task creation but the server
  rewrites it internally (every subsequent response echoes a resolved community name,
  such as `mainnet1`, not the literal string `"public"`). Do not write logic that
  compares a task's returned `community` field against the literal string `"public"`.
