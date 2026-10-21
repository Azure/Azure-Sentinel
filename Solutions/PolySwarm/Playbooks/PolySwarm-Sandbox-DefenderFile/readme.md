# PolySwarm-Sandbox-DefenderFile

**Preview.** This playbook deploys and passes every local check, but it has not yet
been run against a live Defender for Endpoint tenant. If you try it, please tell us how it
went at support@polyswarm.io.

Starting from a Microsoft Sentinel incident with a FileHash entity, runs a Microsoft
Defender for Endpoint advanced hunting query to find where the SHA-256 was last seen,
pulls the file off that device with Defender live response (`GetFile`), and submits
it to the PolySwarm sandbox (private community by default) for detonation. Comments
the verdict, score, malware family, MITRE ATT&CK techniques and report link back on
the incident. Never creates an incident.

Two variants, both built and committed:

- `Playbooks/PolySwarm-Sandbox-DefenderFile/incident-trigger/azuredeploy.json`, incident-triggered,
  iterates every FileHash entity on the incident.
- `Playbooks/PolySwarm-Sandbox-DefenderFile/entity-trigger/azuredeploy.json`,
  entity-triggered, bound to a single FileHash entity.

`Playbooks/PolySwarm-Sandbox-DefenderFile/grant-defender-permissions.sh` is a
companion Azure CLI script, run once per deployed playbook instance, that grants the
Defender for Endpoint application permissions (see "Post-deployment steps" below).

## Summary

1. Community guard: refuses to submit if the community resolves to the public
   community unless `AllowPublicCommunity=true`. `Community` has no default
   value on purpose.
2. Hash-algorithm guard: skips any FileHash entity that is not SHA-256 (Defender's
   `DeviceFileEvents`/`DeviceProcessEvents` are indexed on SHA-256 only), with a
   comment.
3. **Hash-value guard**: independently of what the entity claims its Algorithm is,
   the trimmed, lowercased Value itself must be exactly 64 characters of `0-9a-f`.
   Anything else (including a value that carries KQL syntax) is rejected with an
   incident comment before any Key Vault read, hunting query, or Defender call runs.
   See "Security fix: hash value validation" below.
4. Reads the PolySwarm API key from Key Vault.
5. Runs a Defender advanced hunting query (`DeviceFileEvents` union
   `DeviceProcessEvents`, most recent sighting) to find the device id and folder path
   for the hash. The query is built only from the validated hash from step 3 (never
   the raw entity value), with single quotes doubled as defense in depth, and now
   also projects `SHA256` (native on the `DeviceFileEvents` leg, `InitiatingProcessSHA256`
   projected as `SHA256` on the `DeviceProcessEvents` leg).
6. **Hash-match guard**: before retrieving anything, the selected sighting's `SHA256`
   (lowercased) must equal the validated input hash from step 3. A mismatch stops
   with an incident comment rather than retrieving a file for a different hash.
7. **Denied-path guard**: the sighting's full path (`FolderPath` + `FileName`) is
   checked, case-insensitively, against `DeniedPathFragments` (credential and secret
   stores by default). A match stops with an incident comment before the approval
   email is even sent.
8. **Analyst approval**: if `RequireAnalystApproval` is true (default), sends an
   Office 365 Outlook approval email to `ApproverEmail` naming the incident, hash,
   device and full path, and waits up to `ApprovalTimeoutHours` (default 4) for an
   Approve/Reject response. Anything other than an explicit Approve within the
   window stops with an incident comment; no file is retrieved.
9. Starts Defender live response `GetFile`, polls the resulting machine action, then
   fetches the download link.
10. Checks the file size (HTTP HEAD, `Content-Length`) against `MaxFileSizeBytes`
    (default 100 MB, chosen as the Logic Apps no-chunking-guaranteed ceiling) before
    downloading; above that, the comment states the file is too large to submit and
    must be retrieved directly from the Microsoft Defender portal, rather than
    attempting a transfer likely to fail. The comment does not include the Defender
    live response download link: that link is a short-lived, unauthenticated way to
    pull the file's bytes, and handing it out inside an incident comment is not
    something this playbook does.
11. Downloads the file and submits it to PolySwarm **as-is, still gzip-compressed**
    (see "Gzip: submitted as-is" below), through the same three-step sandbox upload
    flow the other sandbox playbooks use.
12. Polls to completion, derives a verdict from the score (see `README.md`, "Sandbox
    verdict"), comments on the incident, and writes a row to `PolySwarmSandbox_CL`
    (`Source: DefenderFile`) via the Logs Ingestion API.
13. Every failure path (invalid hash value, hash not found, hash mismatch, denied
    path, approval rejected or timed out, device offline/unresponsive, live response
    not started, file too large, PolySwarm create/upload/finalize failure, sandbox
    timeout) posts its own incident comment.

## Security fix: hash value validation, approval gate, and path deny list

An earlier version of both templates in this folder validated only the FileHash
entity's `Algorithm` field (that it said `sha256`), then concatenated the entity's
`Value` field straight into the Defender advanced hunting KQL query
(`Build_hunting_query`) as a string literal. Since `Algorithm` and `Value` are two
independent entity fields, a `Value` that did not actually look like a SHA-256 hash
(for example, one carrying its own KQL syntax) reached the query unchecked. The query
result drove which device and path Defender live response `GetFile` retrieved a file
from, with no check that the file it returned had anything to do with the hash that
was supposedly being looked up. This could be used to make the playbook retrieve an
arbitrary file from an arbitrary onboarded device and submit it to the PolySwarm
sandbox.

Both templates now:

1. Validate the trimmed, lowercased `Value` is exactly 64 hex characters (`Compose_validated_hash`
   plus `If_hash_value_is_valid`, implemented as a length check and 16 nested
   `replace()` calls, one per hex character, since Logic Apps has no regex function)
   before doing anything else with it, including reading the PolySwarm key from Key
   Vault.
2. Use only that validated value downstream, never the raw entity value, and double
   any single quote in it (defense in depth; the gate above should make this
   unreachable) when building the KQL query.
3. Require the hunting query's own `SHA256` result field (now projected on both legs
   of the query) to match the validated input hash before doing anything with the
   sighting.
4. Reject a retrieval whose full file path matches an entry in `DeniedPathFragments`,
   a deny list of credential and secret store paths, before the approval step.
5. Require analyst approval (Office 365 Outlook approval email, `RequireAnalystApproval`
   default `true`) before retrieving any file, addressing the residual risk that a
   correctly-hashed but sensitive file's real hash gets placed on an incident on
   purpose.

None of these checks can be switched off. Together they are what make it safe to pull
a file off a device.

## No result (HTTP 204)

PolySwarm answers HTTP 204 with an empty body when it has nothing for a request (not found). The status poll checks for 204 explicitly, ends the loop with a NOT_FOUND state and never reads the empty body. The incident gets a comment saying PolySwarm returned no result and no verdict is available, and the PolySwarmSandbox_CL row, where one is written, carries the verdict unknown. Task creation returns 200.

All polling loops are bounded twice: a count limit and a timeout (TimeoutMinutes, default 15 minutes; the analyst approval wait is bounded at ApprovalTimeoutHours, default 4 hours).

## Gzip: submitted as-is, both providers unpack it

Defender live response `GetFile` results are gzip-compressed. Logic Apps has no
built-in decompression action and no `require()` in its Execute JavaScript Code
action, so an earlier version of this playbook failed loudly rather than guess at
decompression. Testing (one gzipped EICAR file, submitted once to each provider,
private community) confirmed both **CAPE** and **Triage** automatically unpack a
gzip archive and analyze the inner file: CAPE's `report.dropped[]` and Triage's
`report.static.signatures[]` both correctly YARA-flagged the nested EICAR file, and
the extracted file's SHA-256 matched the well-known EICAR hash in both cases. The
playbook now submits the gzip bytes straight through, `artifact_name` set to the
original file name plus `.gz`. This removed an earlier `Microsoft.Logic/integrationAccounts`
resource and Execute JavaScript Code action that existed only for a decompression
step that turned out to be unnecessary.

## Permissions correction

An earlier design assumed `Machine.Read.All` was sufficient for the machine-action
poll and download-link calls. Microsoft's current API reference for both actually
requires `Machine.ReadWrite.All`. Deploying with only `Machine.Read.All` lets live
response start, but the poll and download-link calls return 403, and the playbook
hangs silently until its own timeout rather than failing with a clear error. See
`docs/permissions.md`.

## Prerequisites

- Microsoft Defender for Endpoint Plan 2, with **Live response** and **Live response
  for servers** enabled under Settings > Endpoints > Advanced features.
- A Microsoft Sentinel workspace onboarded to Microsoft Defender XDR as the primary
  workspace.
- A PolySwarm API key with sandbox access to a private community, stored as a secret
  in an Azure Key Vault this subscription can reach.
- The shared sandbox results infrastructure
  (`Data Connectors/PolySwarmSandboxResults/azuredeploy.json`) deployed first.

## Parameters

| Parameter | Notes |
| --- | --- |
| `PlaybookName` | Defaults to `PolySwarm-Sandbox-DefenderFile`. |
| `Community` | Your private PolySwarm community. No default; required. |
| `AllowPublicCommunity` | Boolean, default `false`. |
| `Provider` | Default `triage`. |
| `VmSlug` | Default `windows11-21h2-x64`. |
| `NetworkEnabled` | Boolean, default `true`. |
| `TimeoutMinutes` | Default `15`, applies to the PolySwarm sandbox poll. |
| `KeyVaultName` | No default; required. |
| `KeyVaultSecretName` | Default `PolySwarmApiKey`. |
| `DefenderApiBaseUrl` | Default `https://api.securitycenter.microsoft.com`, the classic MDE host tied to the WindowsDefenderATP app-role grant. Kept consistent across all four Defender calls so the managed-identity token audience matches the grant; Microsoft's current doc examples also show `api.security.microsoft.com`, but switching hosts means re-checking the audience and the grant together, not just the URL. |
| `PolySwarmApiBaseUrl` | Default `https://api.polyswarm.network/v3`. |
| `MaxFileSizeBytes` | Default `104857600` (100 MB), measured on the gzip-compressed bytes. Over this limit, the file is left on the device for retrieval from the Microsoft Defender portal instead of being downloaded and submitted; no download link is posted to the incident. |
| `MaliciousScoreThreshold` | Default `7`. |
| `SuspiciousScoreThreshold` | Default `4`. |
| `DceLogsIngestionEndpoint` | No default; required. |
| `DcrImmutableId` | No default; required. |
| `StreamName` | Default `Custom-PolySwarmSandboxResults`. |
| `DcrResourceId` | No default; required. |
| `create_role_assignment` | Boolean, default `true`. |
| `RequireAnalystApproval` | Boolean, default `true`. Sends an Office 365 Outlook approval email to `ApproverEmail` before Defender live response `GetFile` runs; only an explicit Approve within `ApprovalTimeoutHours` lets retrieval proceed. |
| `ApproverEmail` | No default; required when `RequireAnalystApproval` is `true`. Where the approval email is sent. |
| `ApprovalTimeoutHours` | Default `4`. How long to wait for the approval response before treating it as a timeout. |
| `DeniedPathFragments` | Array, defaults to common credential and secret store paths (browser profile directories, Windows Credentials/Protect/Vault, `System32\config`, `NTDS`, `.kdbx`, `id_rsa`). Case-insensitive substring match against the retrieved file's full path; a match stops the playbook before retrieval. |

## Post-deployment steps

1. Grant this playbook's managed identity **Key Vault Secrets User** on the Key Vault
   named in `KeyVaultName`.
2. Run `grant-defender-permissions.sh <resource-group> <playbook-name>` (in this
   folder) against the resource group, to grant `Machine.LiveResponse`,
   `Machine.ReadWrite.All` (not `Machine.Read.All`, see "Permissions correction"
   above) and `AdvancedQuery.Read.All` on the WindowsDefenderATP API to the managed
   identity. Requires signing in as a Global Administrator or Privileged Role
   Administrator; Owner/Contributor on the subscription is not enough for
   application-permission grants.
3. Authorize the Microsoft Sentinel, Key Vault, and Office 365 Outlook API connections
   if they show as unauthorized. The Office 365 Outlook connection is a mailbox
   sign-in (delegated), the standard Logic Apps connector model, not a Graph
   application permission; it needs no separate admin consent step beyond signing in
   once. Only needed if `RequireAnalystApproval` is `true` (the default); the
   approval email is sent from whichever mailbox authorizes this connection.
4. Assign the **Microsoft Sentinel Responder** role on the resource group (or
   workspace) to this playbook's managed identity so it can comment on incidents.
5. **Monitoring Metrics Publisher** on the Data Collection Rule (`DcrResourceId`) is
   assigned automatically when `create_role_assignment` is `true` (default);
   otherwise grant it manually the same way as the Key Vault role, scoped to the DCR
   instead. `grant-defender-permissions.sh` does not do this; it only handles the
   WindowsDefenderATP application permissions.
6. Attach to an automation rule.
7. Separately confirm, in the Defender portal, that Live response and Live response
   for servers are turned on; the grant script cannot check this.
8. If `RequireAnalystApproval` is `true` (default), confirm `ApproverEmail` is set to
   a mailbox someone actually monitors; an unanswered approval email just times out
   after `ApprovalTimeoutHours` and no file is retrieved.

## What the comment looks like

Same verdict-derivation language as the other sandbox playbooks: neither CAPE's nor
Triage's report returns a categorical verdict; this playbook's "Verdict" is a
score-threshold approximation, stated as such. `CompletedAt` on the
`PolySwarmSandbox_CL` row is approximated as the time this playbook observed the
terminal status, since the sandbox task object carries no explicit completion
timestamp among the fields confirmed live.

No example comment is shown here yet, because this playbook is still in preview (see
the note at the top of this page).

## Troubleshooting

See `README.md`, "Troubleshooting". Specific to this playbook:

- A device shown as offline or unresponsive to live response comments that state so,
  with the pending action id, rather than retrying indefinitely.
- A 403 on the machine-action poll or download-link call almost always means
  `Machine.ReadWrite.All` was not granted (only `Machine.LiveResponse` and/or
  `Machine.Read.All`); re-run `grant-defender-permissions.sh`.
- Microsoft's advanced hunting API carries an active deprecation warning in favor of
  the Graph security API's `runHuntingQuery`, with no end date published; this is the
  single biggest platform-risk item in this playbook and worth monitoring.
- A comment saying the hash value is not valid means the FileHash entity's `Value`
  field, trimmed and lowercased, was not exactly 64 hex characters. This is expected
  behavior for a non-SHA-256 value regardless of what `Algorithm` claims; re-run
  against a genuine SHA-256 value.
- A comment saying the located sighting's SHA256 did not match means the Defender
  hunting query returned a row whose own `SHA256` field disagreed with the validated
  input hash; no file is retrieved in that case.
- A comment saying the file path matched a denied path fragment means the retrieved
  file's location matched an entry in `DeniedPathFragments`; adjust that parameter if
  it is too broad for your environment, but do so deliberately.
- If approval requests never arrive, confirm the Office 365 Outlook API connection is
  authorized (step 3 above) and that `ApproverEmail` is correct. A rejected or
  unanswered approval stops the playbook with a comment; it does not retry.

## How the checks are arranged

Logic Apps allows at most eight levels of nested actions, and this playbook has more
checks than that. So the checks run as a sequence: each check that stops the run
(not SHA-256, invalid value, device not found, hash mismatch, protected path,
approval declined or timed out, live response failed, file too large, task not
created) records why in the `stopReason` variable, and each following step runs only
while `stopReason` is empty. The guard tests rebuild the nested form from that
sequence and prove every check still stands between the entity and the file
retrieval.
