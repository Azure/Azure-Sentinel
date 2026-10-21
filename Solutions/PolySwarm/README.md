# PolySwarm for Microsoft Sentinel

PolySwarm's solution for the Microsoft Sentinel Content Hub. It brings multi-engine
malware verdicts, sandbox detonation and threat intelligence from PolySwarm into
Microsoft Sentinel, so an analyst can enrich, detonate and hunt against PolySwarm data
without hand-building Logic Apps against the PolySwarm API.

## Status

Version 3.0.0. Both data connectors, the analytics rules, the workbook and every
playbook except two have been installed and run in a live Microsoft Sentinel
workspace.

Two playbooks ship as **preview**: the Defender for Endpoint file detonation playbook
and the Outlook attachment detonation playbook. Both deploy cleanly and pass every
local check, but they have not yet been run against a live Defender for Endpoint
tenant or Exchange Online mailbox. If you try either one, please tell us how it went
at support@polyswarm.io.

## What the solution does

- **Enrichment.** Incident and entity-triggered playbooks look up a file hash, URL, IP
  address or domain against PolySwarm and post the verdict, PolyScore, the names of the
  engines that agreed, malware family and (where available) sandbox and MITRE ATT&CK
  detail as a comment on the incident.
- **Threat intelligence.** Two data connectors bring PolySwarm indicators into
  Microsoft Sentinel's native `ThreatIntelIndicators` table: one from your own
  PolySwarm hunting results, one from the PolySwarm curated feed. Because the
  indicators are native, Microsoft's own built-in indicator matching rules run against
  them automatically, alongside the analytics rules this solution ships.
- **Sandbox detonation.** An analyst can submit a URL, an email attachment, a file in
  Azure Storage, or a file retrieved directly from an endpoint through Microsoft
  Defender for Endpoint, to the PolySwarm sandbox, and get a score-derived verdict,
  malware family, MITRE ATT&CK techniques and a best-effort report link back on the
  incident. Each detonating playbook writes its own result to a dedicated table, so an
  analytics rule can turn a malicious detonation into an incident.
- **Hunting.** Hunting queries join PolySwarm indicators against your own log tables.
- **Status.** A small PolySwarm status workbook shows what has arrived from each
  connector and each rule. It reads only tables in your workspace, never calls
  PolySwarm and needs no credential. A tile that says nothing has arrived yet is normal
  on a new install.

## Coverage by indicator type

- Answered: MD5, SHA-1, SHA-256, URL, domain and IP address.
- Not supported: email addresses. PolySwarm has no endpoint that answers them.

File hashes are scored from the PolyScore. URLs, domains and IP addresses are judged
from detection counts, because the URL PolyScore is a constant. A result
with no engine coverage is reported as unknown, never as benign, and an
artifact PolySwarm has no record of is a normal "not found". Domains and
IP addresses answer as a bare host through the URL lookup.

## Components

| Component | What it is |
| --- | --- |
| Enrichment playbooks | Incident and entity-triggered playbooks for file hash, URL, IP address and domain. |
| Sandbox playbooks | Detonate a URL, an Outlook attachment (preview), or an Azure Storage blob, from a Microsoft Sentinel incident. |
| Defender for Endpoint file detonation playbook (preview) | Retrieves a file from an onboarded device by SHA-256 and detonates it, with both incident- and entity-triggered variants. |
| Check quota playbook | Reads remaining PolySwarm API and sandbox usage and comments on the incident when a configured warning threshold is crossed. |
| Hunting data connector | Codeless Connector Framework (CCF) connector that polls your PolySwarm live hunt results into the native `ThreatIntelIndicators` table. |
| Curated feed data connector | CCF connector that polls the PolySwarm curated indicator feed into the native `ThreatIntelIndicators` table, for accounts without hunts configured. |
| Sandbox results infrastructure | Shared Data Collection Endpoint, table and Data Collection Rule that every sandbox-detonating playbook writes one row to, via the Logs Ingestion API, once a detonation reaches a terminal state. Not a data connector the customer configures with an API key; see "Sandbox results: how the data actually gets there" below. |
| Status workbook | `Workbooks/PolySwarmStatus.json`. Connector and rule status read from your own workspace tables, with an explicit message on every tile that has nothing to show yet. |
| Analytics rules | Three rules that correlate PolySwarm indicators with your own log sources and raise incidents from malicious sandbox detonations. |
| Hunting queries | Four saved queries joining PolySwarm indicators against your log tables (hash, IP, URL, domain). |

## After you install

Installing the solution does not turn anything on. Everything below ships switched off
or unconnected, and each item has one action that turns it on.

1. **Analytics rules (three templates).** PolySwarm high-confidence hunt hit,
   PolySwarm malicious file observed and PolySwarm sandbox detonation malicious are
   rule templates, not active rules. Turn one on by opening Analytics, then Rule
   templates, selecting it and choosing Create rule.
2. **Data connectors (hunting and curated feed).** Neither collects anything until it
   is configured. Open the connector under Data connectors, enter the credentials and
   settings, and choose Connect.
3. **Incident-triggered playbooks (every enrichment, sandbox and check quota playbook,
   and the Defender for Endpoint file playbook).** None runs until an automation rule
   runs it. Create an automation rule that runs the playbook when an incident is
   created or updated. Grant the playbook's managed identity its roles first
   (`docs/permissions.md`).
4. **Entity-triggered playbooks.** No automation rule applies to these.
   Entity-triggered playbooks run only when someone starts them on one entity. As of
   October 2026 the Microsoft Defender portal has no Run playbook action on an entity, so
   in the Defender portal run the incident-triggered version on the whole incident
   instead (select the incident in the Incidents list, then Run Playbook). Workspaces not
   yet moved to the Defender portal can still run entity playbooks from an entity on the
   incident page in the Azure portal, and any workspace can start one through the
   Microsoft Sentinel API (Entities, Run Playbook).
5. **Sandbox results table.** `PolySwarmSandbox_CL` exists only after you deploy
   `Data Connectors/PolySwarmSandboxResults/azuredeploy.json`. Deploy it once, before
   any sandbox playbook. The sandbox detonation rule has nothing to read until a
   playbook has written a row.
6. **Hunting queries (four).** These are saved queries and run only when an analyst
   runs them from Hunting.
7. **Custom connector.** It is available to your own playbooks once deployed and does
   nothing by itself.

The PolySwarm status workbook is the place to see which of these has started producing
data. Open it from Workbooks, then Templates.

## How much data the curated feed adds

The PolySwarm Curated Feed is large. In our test workspace (October 2026) the Trust
Group 14-day feed added about **500,000 indicators a day**, roughly **0.5 GB a day** in
the ThreatIntelIndicators table (about 170,000 files a day, each as an MD5, SHA-1 and
SHA-256 indicator). Microsoft Sentinel charges for data it ingests, so check
[Microsoft Sentinel pricing](https://azure.microsoft.com/pricing/details/microsoft-sentinel/)
for that volume before you connect the feed.

The PolySwarm Hunting connector is much smaller: it only brings in files that match
your own hunts.

If the feed volume does not suit you, tell PolySwarm support. We will use that
feedback to decide whether to add a smaller option.

## Required network egress

If you restrict outbound traffic from Azure, allow these hosts on port 443:

- `api.polyswarm.network`, for every lookup, hunt result, feed read and sandbox call.
- `ps-storage-prodv2-artifact-index.s3.us-east-2.amazonaws.com`, an Amazon S3 host in
  the us-east-2 region, which receives the file or URL bytes during a sandbox upload.
  Only the sandbox playbooks use it. PolySwarm returns the full upload address
  (host and a signed query string) when a detonation is created; allow the host only.

## Navigating Microsoft Sentinel

Microsoft Sentinel leaves the Azure portal after 31 March 2027 and becomes available
only from the Microsoft Defender portal (`security.microsoft.com`). This documentation
gives the Defender portal path first for anything Sentinel-specific: Content Hub, data
connectors, analytics rules, automation rules, and incidents. A few steps genuinely
live in the Azure portal regardless of which portal you use for Sentinel itself,
because they are Azure resource operations rather than a Sentinel screen: deploying a
Logic App or a Logic Apps custom connector, managing an Azure Key Vault, and assigning
Azure RBAC roles (Access control (IAM)). Those steps say "Azure portal" explicitly
wherever they come up.

## Prerequisites

- A Microsoft Sentinel workspace, in a resource group you can deploy Logic Apps,
  connectors and role assignments into.
- A PolySwarm API key. Generate one from your PolySwarm account. Keys are never
  committed to this repository; every deployed playbook and connector reads its key
  from Azure Key Vault (or, for the curated feed connector, Azure Key Vault-sourced
  Basic auth credentials) through its managed identity, not from a plain deployment
  parameter. See "Key Vault setup" below.
- Your PolySwarm account must carry the entitlement for each capability you deploy:
  - **Sandbox detonation**, for the sandbox playbooks, the Defender for Endpoint file
    detonation playbook, and the shared sandbox results infrastructure.
  - **Private community**, for detonating in a community that is not visible to other
    PolySwarm users. See "Public vs private community" below; this is the default for
    every sandbox playbook in this solution.
  - **Live hunting**, for the hunting data connector, which turns your own PolySwarm
    hunt results into native Sentinel indicators.
  - **Curated feed / TAXII entitlement** (`taxii`, plus the specific feed's own
    entitlement, for example `taxii_trustgroup`), for the curated feed data connector.
  Contact your PolySwarm representative or support@polyswarm.io to confirm
  which entitlements are on your account.
- For the Defender for Endpoint file detonation playbook only: Microsoft Defender for
  Endpoint Plan 2, with **Live response** and **Live response for servers** enabled in
  the Microsoft Defender portal (`security.microsoft.com`) under Settings > Endpoints >
  Advanced features, and at least one onboarded device.

## Deployment order

1. Confirm the prerequisites above, including which entitlements your PolySwarm
   account carries.
2. Set up Azure Key Vault and store your PolySwarm API key there (see below).
3. If you are deploying any sandbox-detonating playbook (URL, Outlook attachment,
   Storage blob, or Defender file), deploy the shared sandbox results infrastructure
   first: `Data Connectors/PolySwarmSandboxResults/azuredeploy.json`. Every sandbox
   playbook depends on its outputs.
4. Deploy the data connectors, enrichment playbooks, sandbox playbooks, check quota
   playbook, analytics rules and hunting queries you need; each deploys
   independently once its own prerequisites (above) are met.
5. Grant every deployed playbook's and connector's managed identity the roles and API
   permissions it needs. See `docs/permissions.md` for the complete list and
   `docs/deployment.md` for the role assignment steps.
6. Configure each data connector (your API key, the community for the hunting
   connector, the feed for the curated feed connector) and confirm it shows connected.
7. Enable the analytics rules you want active.
8. Attach the incident-triggered playbooks to automation rules. Entity-triggered
   playbooks are started by hand (see "After you install" above).
9. For the Defender for Endpoint file detonation playbook, confirm the workspace is
   onboarded to Microsoft Defender XDR as the primary workspace, run
   `Playbooks/PolySwarm-Sandbox-DefenderFile/grant-defender-permissions.sh`, and
   confirm at least one device is onboarded with live response enabled.
10. Test. See `docs/deployment.md` for the smoke test steps.

New to Microsoft Sentinel? Start with `docs/getting-started.md`, a plain-language
walkthrough with a screenshot for every step. Full step by step instructions for
administrators are in `docs/deployment.md`.

## Key Vault setup

Every playbook in this solution reads the PolySwarm API key from Azure Key Vault
through its own managed identity, using a Key Vault API connection deployed alongside
it. None of them accept the key as a plain deployment parameter.

1. Create an Azure Key Vault in the same tenant as your Sentinel workspace, or use an
   existing one your security team already manages. The vault must have
   `enabledForTemplateDeployment` set to `true`, or its connection resource deploys
   against RBAC only, which is the default and is sufficient here.
2. Store your PolySwarm API key as a secret, for example named `PolySwarmApiKey`.
3. When you deploy a playbook, supply the vault's name as its `KeyVaultName`
   parameter, and, if you used a different secret name, the secret's name as
   `KeyVaultSecretName`. The deployment creates a Key Vault API connection for that
   playbook.
4. After deployment, grant the playbook's managed identity the **Key Vault Secrets
   User** role, scoped to the Key Vault (or to that one secret, if your Key Vault uses
   access policies with per-secret scoping). This is a read-only role: it lets the
   identity retrieve secret values but not manage the vault or other secrets.
5. Authorize the Key Vault API connection in the Azure portal if it shows as
   unauthorized. This is a Logic Apps connection resource, an Azure resource rather
   than a Sentinel-specific screen, so it is managed from the Azure portal even after
   Microsoft Sentinel itself moves fully to the Defender portal.

Every enrichment playbook (file hash, URL, IP, domain, both incident- and
entity-triggered variants), every sandbox playbook, the Defender for Endpoint file
detonation playbook, and the check quota playbook are built this way.

The curated feed data connector reads its credentials differently: the PolySwarm
TAXII server authenticates with HTTP Basic auth (your PolySwarm account number as the
username, your Team API key as the password), not the `Authorization: <key>` header
scheme every other PolySwarm call in this solution uses. You enter both values
directly in the connector's own configuration pane; they are not read from Key Vault
at connector-configuration time, matching how every other CCF connector in this
solution takes its API key.

## Sandbox results: how the data actually gets there

An earlier design polled PolySwarm's sandbox task list API for a `PolySwarmSandbox_CL`
table. Measurement showed that API returns no verdict, malware family, ATT&CK
techniques or completion time for any task, so a poller could not populate the columns
that make the table useful. The table is instead filled directly by whichever
playbook ran the detonation, right after it polls the task to completion, since that
playbook already holds the full result.

`Data Connectors/PolySwarmSandboxResults/azuredeploy.json` deploys the shared, one-time
infrastructure: a Data Collection Endpoint, the `PolySwarmSandbox_CL` table (17
columns: `TimeGenerated, TaskId, ArtifactType, Sha256, Url, FileName, Source, Provider,
Community, Verdict, Score, Family, Techniques, ReportUrl, CreatedAt, CompletedAt,
IncidentArmId`), and a Data Collection Rule. Deploy this once, before any sandbox
playbook. Its outputs (`dceLogsIngestionEndpoint`, `dcrImmutableId`, `dcrResourceId`,
`streamName`) feed the matching deployment parameters on every sandbox-detonating
playbook (URL, Outlook attachment, Storage blob, Defender file).

Each of those playbooks then:

- Posts one row via the Logs Ingestion API
  (`{dceLogsIngestionEndpoint}/dataCollectionRules/{dcrImmutableId}/streams/{streamName}?api-version=2023-01-01`,
  managed identity auth, audience `https://monitor.azure.com`) for every detonation
  attempt, including timeouts, so the table reflects every submission, not only the
  successful ones.
- Needs the **Monitoring Metrics Publisher** role on the Data Collection Rule
  (`dcrResourceId`) to write to it. Each playbook template can create this role
  assignment for itself automatically at deployment (the `create_role_assignment`
  parameter, default `true`), a pattern also used by other published Content Hub
  solutions with a similar sandbox-and-Logs-Ingestion design; set it to `false` and
  grant the role manually if the deploying principal cannot grant RBAC roles.

`Source` records which playbook wrote a given row: `Url`, `OutlookAttachment`,
`StorageBlob` or `DefenderFile`.

## Sandbox verdict

Neither sandbox provider PolySwarm uses (CAPE, Triage) returns a maliciousness verdict
string. Both return a raw score on a 0 to 10 scale. Every sandbox-detonating playbook
derives a verdict from that score with the same rule:

- `KNOWN_GOOD` task status (PolySwarm's allowlist recognized the artifact and skipped
  detonation) becomes **known good**.
- No score at all (a timed-out or failed detonation) becomes **unknown**.
- A score of 7 or higher (`MaliciousScoreThreshold`, a playbook parameter) becomes
  **malicious**.
- A score of 4 or higher but below the malicious threshold
  (`SuspiciousScoreThreshold`) becomes **suspicious**.
- Anything else becomes **benign**.

This is a score-threshold approximation the playbooks apply, not a categorical
verdict either sandbox provider returns. State this plainly in any customer-facing
description of the sandbox playbooks.

The report link included in the comment
(`https://polyswarm.network/scan/results/file/{sha256}/{id}`) is built from the same
pattern the PolySwarm hash-lookup uses. It is confirmed to work for artifacts that
also appear in the multi-engine scan index, but a pure-sandbox-only submission's hash
returned HTTP 404 from that lookup in testing, so whether the link resolves for a
sandbox-only result is unconfirmed. Treat it as best effort until verified against a
live portal check.

## Public vs private community

A PolySwarm community is a boundary around who can see a submission and its result.
The **public community** is visible to other PolySwarm users; a **private community**
is visible only to your organization.

Every sandbox playbook in this solution defaults to your private community and
refuses to submit to the public community unless `AllowPublicCommunity` is explicitly
set to `true`. This is because a file or URL submitted to a public community becomes
visible to everyone else using that community, and Sentinel incidents routinely
contain sensitive attachments and internal URLs that should never leave the
organization by default. Enrichment lookups (which only query artifacts PolySwarm has
already seen; they do not submit anything) are not affected by this default.

Isolation was confirmed live: an account is only ever shown a task belonging to a
community it is entitled to, regardless of what community value is passed on a read.
Passing a different, valid community you are also entitled to does not leak or hide
another community's data; the community parameter on a lookup is a correctness input
(which task you mean), not by itself the security boundary. The boundary is account
entitlement.

## Analytics rules and hunting queries

Three analytics rules ship with the solution, all Scheduled rules:

- **PolySwarm malicious file observed**, severity High. Joins active PolySwarm
  file-hash indicators against your device and security event tables (file and
  process events, security events, common security log) on SHA-256, and raises an
  incident carrying the file hash, host and account. Depends on either the hunting or
  the curated feed data connector, both of which write to the native
  `ThreatIntelIndicators` table.
- **PolySwarm high-confidence hunt hit**, severity Medium. Raises an incident on any
  PolySwarm indicator with a confidence of 90 or higher created in the last hour,
  grouped by malware family. Depends on either the hunting or the curated feed data
  connector. The rule's own severity and MITRE tactic are fixed at rule level, as
  Microsoft Sentinel requires; the malware family and hunt rule name that produced the
  indicator are carried on the incident as columns rather than changing the rule's
  tactic dynamically.
- **PolySwarm sandbox detonation malicious**, severity High. Raises an incident from
  any `PolySwarmSandbox_CL` row with a malicious verdict, covering file and URL
  detonations from every sandbox-detonating playbook. Its `requiredDataConnectors`
  entry points at the hunting connector's id (`PolySwarmHuntingCCFDefinition`) with
  `dataType: PolySwarmSandbox_CL`, since that table is no longer written by a
  dedicated CCF connector; this is how the rule declares a PolySwarm dependency
  without a connector definition of its own to point at. This is how a PolySwarm
  sandbox verdict becomes an incident in the unified Defender portal, since the
  playbooks that submit detonations only post an incident comment and never create an
  incident directly.

Four hunting queries join PolySwarm indicators against your own log tables for hash,
IP address, URL and domain, for an analyst to run interactively.

## User agent

Every call this solution makes to the PolySwarm API carries a `User-Agent` header in
the form `PolySwarm-Microsoft-Sentinel/3.0.0 (<component>)`, for example
`PolySwarm-Microsoft-Sentinel/3.0.0 (HuntingConnector)`. This exists so PolySwarm can
see which customers are running this solution and on which version, which matters for
support and for knowing when an older version is still in the field. It carries no
customer data: no incident content, no entity values, no tenant identifier, only the
solution's own name and version and the calling component's name.

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| A playbook fails with a 403 posting a comment or reading incident entities | Its managed identity is missing the **Microsoft Sentinel Responder** role. See `docs/permissions.md`. |
| A playbook fails reading the PolySwarm API key | Its managed identity is missing the **Key Vault Secrets User** role on the Key Vault holding the secret, or the secret name does not match what the playbook expects. |
| A sandbox playbook fails writing to `PolySwarmSandbox_CL` | Its managed identity is missing **Monitoring Metrics Publisher** on the Data Collection Rule, or the shared `PolySwarmSandboxResults` infrastructure has not been deployed yet. |
| A data connector shows disconnected | The stored PolySwarm API key or, for the curated feed connector, account number/API key pair is invalid, or the account does not carry the entitlement that connector needs. |
| No PolySwarm result, HTTP 401 | The PolySwarm API key is invalid or missing. |
| No PolySwarm result, HTTP 204 with an empty body | PolySwarm has no record of the artifact. This is a normal outcome, not an error. |
| No PolySwarm result, HTTP 429 | The PolySwarm rate limit was reached. Playbooks and connectors retry with backoff; persistent 429s mean sustained traffic is exceeding one of these limits. Confirm your PolySwarm plan's published limit. |
| A sandbox submission fails immediately | Your account has exhausted its sandbox detonation quota, or the requested community does not exist for your account. The comment states which. |
| A sandbox detonation shows verdict "unknown" | The detonation timed out or failed before a score was produced. Check the report link and task id in the comment. |
| The Defender for Endpoint file detonation playbook cannot retrieve a file | The device is offline, or the managed identity is missing one of the required Defender for Endpoint API permissions. Confirm you ran `grant-defender-permissions.sh`, and see `docs/permissions.md`. |
| A playbook never runs | No automation rule is attached to it, or the rule's conditions exclude the incident. |

## Support

PolySwarm Customer Success: support@polyswarm.io

For Microsoft Sentinel and Logic Apps configuration questions not specific to
PolySwarm, see the
[Microsoft Sentinel documentation](https://learn.microsoft.com/azure/sentinel/) or your
internal SIEM team.
