# Deployment

Step by step deployment for the PolySwarm solution for Microsoft Sentinel. Read
`README.md` first for prerequisites, entitlements and the Key Vault setup this guide
assumes. See `docs/permissions.md` for the full reference of every role and API
permission named below.

Deploy only the components you have the PolySwarm entitlement for. Every playbook and
connector deploys independently, except that every sandbox-detonating playbook depends
on the shared sandbox results infrastructure being deployed first.

See `README.md`, "Navigating Microsoft Sentinel", for which portal each step below
uses. In short: the Microsoft Defender portal (`security.microsoft.com`) is given
first for anything Sentinel-specific (Content Hub, data connectors, analytics,
automation); the Azure portal is named explicitly for the handful of steps that are
Azure resource operations rather than a Sentinel screen (deploying Logic Apps, Key
Vault, and Azure RBAC role assignments).

## Required network egress

If your organization restricts outbound traffic from Azure, allow these hosts on
port 443 for the Logic Apps and data connectors in this solution:

- `api.polyswarm.network`, for lookups, hunt results, the curated feed and sandbox
  task calls.
- `ps-storage-prodv2-artifact-index.s3.us-east-2.amazonaws.com`, an Amazon S3 host in
  the us-east-2 region. The sandbox playbooks PUT the file or URL bytes to a
  pre-signed address on this host. Allow the host only; the signed query string
  changes on every upload.

Calls to Azure services (Key Vault, Microsoft Sentinel, Azure Monitor) and, for the
Defender file playbook, Microsoft Defender for Endpoint follow your normal Azure
egress rules.

## 1. Prepare Key Vault

1. Create an Azure Key Vault in the same tenant as your Sentinel workspace, or identify
   an existing one you are permitted to add secrets and role assignments to. The vault
   must have `enabledForTemplateDeployment` set to `true`.
2. Add your PolySwarm API key as a secret, for example `PolySwarmApiKey`.
3. Note the vault's name and the secret's name; every playbook below asks for these as
   `KeyVaultName` and `KeyVaultSecretName` deployment parameters.

## 2. Deploy the sandbox results infrastructure (if deploying any sandbox playbook)

Deploy `Data Connectors/PolySwarmSandboxResults/azuredeploy.json` once, before any
sandbox-detonating playbook. It takes two parameters:

- `log_analytics_workspace_name` (required): the Log Analytics workspace backing your
  Sentinel instance.
- `log_analytics_workspace_location` (optional, defaults to the resource group's
  location).

It creates a Data Collection Endpoint (`polyswarm-dce`), the `PolySwarmSandbox_CL`
table (17 columns) on your workspace, and a Data Collection Rule
(`polyswarm-dcr-sandbox-results`) with input stream `Custom-PolySwarmSandboxResults`.
Record its four outputs; every sandbox-detonating playbook needs them as deployment
parameters:

| Output | Feeds playbook parameter |
| --- | --- |
| `dceLogsIngestionEndpoint` | `DceLogsIngestionEndpoint` |
| `dcrImmutableId` | `DcrImmutableId` |
| `dcrResourceId` | `DcrResourceId`, used as the scope for each playbook's own Monitoring Metrics Publisher role assignment |
| `streamName` | `StreamName`, value `Custom-PolySwarmSandboxResults` |

Skip this step if you are deploying enrichment playbooks, the check quota playbook, or
the data connectors only; none of those write to `PolySwarmSandbox_CL`.

## 3. Deploy the solution content

Deploy from Content Hub once the solution is published: Microsoft Defender portal
(`security.microsoft.com`) > Microsoft Sentinel > Content management > Content hub,
or, on a workspace still using the classic Azure-portal Sentinel experience, your
Sentinel workspace > Content Hub in the Azure portal. For a pre-release install,
deploy the packaged ARM templates in `Package/` instead, from either portal's "Deploy
a custom template" page. Choose which optional pieces to deploy:

- The custom connector (`custom-connector/polyswarm-connector-swagger.json`), if your
  team wants to build its own playbooks and automation rules against the PolySwarm
  API directly. Covers lookup operations plus the sandbox submission/status
  operations; it does not include a file-upload operation (the presigned-URL upload
  step is a different host than the rest of the API, which a single Swagger document
  cannot express).
- The enrichment playbooks: `PolySwarm-Enrich-FileHash`, `PolySwarm-Enrich-Url`,
  `PolySwarm-Enrich-Ip`, `PolySwarm-Enrich-Domain`, each with an
  `incident-trigger/azuredeploy.json` (incident-triggered) and `entity-trigger/azuredeploy.json`
  (entity-triggered) template.
- The sandbox playbooks, if your account has the sandbox detonation entitlement:
  `PolySwarm-Sandbox-Url` (`azuredeploy.json` incident-triggered,
  `entity-trigger/azuredeploy.json` entity-triggered), `PolySwarm-Sandbox-OutlookAttachment`
  (incident-triggered only), `PolySwarm-Sandbox-StorageBlob` (incident-triggered only).
- The Defender for Endpoint file detonation playbook,
  `PolySwarm-Sandbox-DefenderFile` (`azuredeploy.json` incident-triggered,
  `entity-trigger/azuredeploy.json` entity-triggered), if you have Defender for
  Endpoint Plan 2.
- The check quota playbook, `PolySwarm-CheckQuota` (incident-triggered).
- The hunting data connector (`PolySwarmHunting_CCF`), if your account has the live
  hunting entitlement.
- The curated feed data connector (`PolySwarmFeed_CCF`), if your account has the
  TAXII entitlement.
- The analytics rules and hunting queries.

## 4. Grant managed identity role assignments

Every playbook authenticates as its own system-assigned managed identity. Each needs
specific roles assigned after deployment; nothing works until this step is done.

Role assignments are Azure RBAC, done in the Azure portal; the Defender portal's
Microsoft Sentinel experience has no Access control (IAM) pane of its own.

### Every enrichment, sandbox and check quota playbook

1. Open the resource group (or the Sentinel workspace) in the Azure portal, go to
   **Access control (IAM)** > **Add role assignment**.
2. Assign **Microsoft Sentinel Responder** to the playbook's managed identity. This
   lets the playbook read incident entities and post comments; it does not grant it
   any other Sentinel permission.
3. Go to your Key Vault's **Access control (IAM)** (or access policies, depending on
   your vault's permission model) and grant the same managed identity
   **Key Vault Secrets User**, scoped to the vault or to the PolySwarm secret alone.
   This is read-only: the identity can retrieve the secret value but cannot manage the
   vault.
4. Authorize the Microsoft Sentinel and Azure Key Vault API connections in the portal
   if they show as unauthorized.

Applies to all four enrichment playbooks (both trigger variants), all three sandbox
playbooks, and the check quota playbook.

### Every sandbox-detonating playbook, additionally

1. The **Monitoring Metrics Publisher** role on the Data Collection Rule
   (`DcrResourceId`, from step 2 above) is assigned automatically at deployment when
   `create_role_assignment` is `true` (the default) and the deploying principal can
   grant RBAC roles on that DCR. If deployed with `create_role_assignment=false`,
   grant it manually the same way as the Key Vault role, scoped to the DCR resource
   instead.

Applies to `PolySwarm-Sandbox-Url`, `PolySwarm-Sandbox-OutlookAttachment`,
`PolySwarm-Sandbox-StorageBlob`, and `PolySwarm-Sandbox-DefenderFile` (both trigger
variants).

### PolySwarm-Sandbox-StorageBlob playbook, additionally

Assign the managed identity **Storage Blob Data Reader** on the storage account named
by the `StorageAccountName` parameter. This playbook reads a fixed
`StorageAccountName`/`ContainerName` and the incident's File entity file name; it does
not write to storage.

### PolySwarm-Sandbox-OutlookAttachment playbook, additionally

Authorize the Office 365 Outlook API connection with a mailbox that has permission to
read the mail message referenced by the incident's Mail entity. This is a connector
authorization (sign-in), not an Azure RBAC role assignment.

### PolySwarm-Sandbox-DefenderFile playbook, additionally

This playbook calls the Microsoft Defender for Endpoint API to find, retrieve and
finalize a file from an onboarded device, so it needs application permissions on top
of the Sentinel, Key Vault and DCR roles above.

1. Run `Playbooks/PolySwarm-Sandbox-DefenderFile/grant-defender-permissions.sh
   <resource-group> <playbook-name>` (Azure CLI, signed in as a Global Administrator
   or Privileged Role Administrator; Owner/Contributor on the subscription is not
   enough for application-permission grants). It grants the playbook's managed
   identity, on the WindowsDefenderATP application:
   - `Machine.LiveResponse`, to run the live response `GetFile` action.
   - `Machine.ReadWrite.All`, to poll the machine action and get the download link.
     **Not `Machine.Read.All`**: Microsoft's current API reference for both the
     machine-action poll and the download-link call lists `Machine.ReadWrite.All` as
     the required permission. Deploying with only `Machine.Read.All` lets live
     response start but the poll/download-link calls 403, hanging silently until the
     playbook's own timeout.
   - `AdvancedQuery.Read.All`, to run the advanced hunting query that locates the
     device and folder path for a given SHA-256.
2. Separately confirm, in the Microsoft Defender portal (`security.microsoft.com`)
   under Settings > Endpoints > Advanced features, that **Live response** and **Live
   response for servers** are turned on; the script cannot check this setting.
3. Separately grant **Monitoring Metrics Publisher** on the sandbox results Data
   Collection Rule (the script does not do this; it is an Azure RBAC role assignment,
   not a WindowsDefenderATP application permission), unless
   `create_role_assignment=true` handled it at deployment.
4. If `RequireAnalystApproval` is `true` (the default), authorize the Office 365
   Outlook API connection this playbook deploys with a mailbox that can send mail to
   `ApproverEmail`. This is a connector authorization (sign-in), the same delegated
   model as the Outlook attachment playbook, not a WindowsDefenderATP application
   permission and not covered by `grant-defender-permissions.sh`. The playbook sends
   an approval email naming the incident, hash, device and full path before every
   Defender live response `GetFile` call, and only proceeds on an explicit Approve
   within `ApprovalTimeoutHours` (default 4).

This playbook skips any FileHash entity that is not SHA-256, since Defender's
`DeviceFileEvents`/`DeviceProcessEvents` are indexed on SHA-256 only. Independently of
that check, it also validates the entity's `Value` itself is a well-formed SHA-256
(64 hex characters) before running any Defender call, and requires the hunting
query's own `SHA256` result to match that validated value before retrieving anything;
see the playbook `readme.md`, "Security fix: hash value validation, approval gate,
and path deny list".

### PolySwarm-CheckQuota playbook

Needs Microsoft Sentinel Responder and Key Vault Secrets User only (see "Every
enrichment, sandbox and check quota playbook" above). It reads PolySwarm's account and
quota endpoint and comments on the incident that triggered it; it does not write to
any Log Analytics table.

## 5. Configure and connect the data connectors

- **Hunting data connector** (`PolySwarmHunting_CCF`): enter your PolySwarm Team API
  key and the community your hunts run in (`public`, or a private community's short
  name). Every hunt in that community comes in; filter by rule or PolyScore in
  Microsoft Sentinel, where each indicator carries both.
- **Curated feed data connector** (`PolySwarmFeed_CCF`): enter your PolySwarm account
  number (the TAXII server's Basic-auth username, not your API key) and Team API key
  (the Basic-auth password), and choose the feed (PolySwarm Trust Group 14-day feed, Ransomware family
  feed, or Freemium feed). Each feed has exactly one collection, and the choice carries
  it, so there is no collection id to type.

Configure each connector from Microsoft Defender portal (`security.microsoft.com`) >
Microsoft Sentinel > Data connectors (or, on the classic Azure-portal experience, your
Sentinel workspace > Data connectors). After configuring a connector, confirm it shows
**Connected** before relying on it.

## 6. Enable analytics rules and hunting queries

Enable the analytics rules you want active from Microsoft Defender portal
(`security.microsoft.com`) > Microsoft Sentinel > **Analytics** (or, on the classic
Azure-portal experience, your Sentinel workspace > Analytics). The sandbox detonation
rule is how a malicious detonation becomes an incident visible in the unified Defender
portal; playbooks themselves never create incidents.

Three analytics rules and four hunting queries ship with the solution (see
`README.md`, "Analytics rules and hunting queries"). Rule 3 (sandbox detonation
malicious) declares its dependency on the hunting connector's id
(`PolySwarmHuntingCCFDefinition`) with `dataType: PolySwarmSandbox_CL`, since that
table is written by the playbooks rather than a dedicated CCF connector. Hunting
queries are under Microsoft Sentinel > **Hunting** in the same portal.

## 7. Attach playbooks to automation rules

Playbooks do not run on their own. Attach each incident-triggered playbook to an
automation rule. No automation rule applies to entity-triggered playbooks.
Entity-triggered playbooks run only when someone starts them on one entity. As of
October 2026 the Microsoft Defender portal has no Run playbook action on an entity, so
in the Defender portal run the incident-triggered version on the whole incident
instead (select the incident in the Incidents list, then Run Playbook). Workspaces not
yet moved to the Defender portal can still run entity playbooks from an entity on the
incident page in the Azure portal, and any workspace can start one through the
Microsoft Sentinel API (Entities, Run Playbook).

1. Microsoft Defender portal (`security.microsoft.com`) > Microsoft Sentinel >
   **Automation** > **Create** > **Automation rule** (or, on the classic Azure-portal
   experience, your Sentinel workspace > Automation).
2. Trigger: **When incident is created** (incident-triggered variants only).
3. Optionally add a condition so the rule only fires on incidents carrying the
   relevant entity type.
4. Action: **Run playbook**, select the PolySwarm playbook.
5. If prompted, grant Sentinel permission to run playbooks in that resource group.

Consider gating sandbox-playbook automation rules to run only on analyst request
rather than automatically on every incident creation, since detonation is metered and
takes minutes rather than seconds.

## 8. Check the status workbook

Open Workbooks, then Templates, and save the PolySwarm status workbook. It reads only
your workspace tables. A tile that says nothing has arrived yet is normal until the
matching connector, rule or playbook has produced data.

## 9. Test

1. Deploy the solution into a workspace and confirm every connector you configured
   shows **Connected**.
2. Confirm at least one indicator with `SourceSystem == "PolySwarm"` appears in
   `ThreatIntelIndicators` (hunting or curated feed connector) within a normal poll
   interval.
3. Create a test incident with a relevant entity (file hash, URL, IP or domain) and
   confirm the automation rule runs the enrichment playbook and a comment appears.
4. Run a sandbox playbook against a real incident and confirm a row appears in
   `PolySwarmSandbox_CL` and the sandbox detonation analytics rule creates an
   incident from a malicious result.
5. For the Defender for Endpoint file detonation playbook, confirm the advanced
   hunting query, live response retrieval, and gzip-compressed submission to
   PolySwarm all complete. This playbook is in preview: it has not yet been run against
   a live Defender for Endpoint tenant.

## What is verified live versus still open

Verified against the live PolySwarm API as of 2026-09-23: the three-step sandbox
submission flow (create, upload to a presigned URL with no PolySwarm auth header,
finalize) for both FILE and URL artifacts, both communities; sandbox status polling
and the `KNOWN_GOOD` terminal state; that both CAPE and Triage report on a 0-10 score
scale; that both sandbox providers unpack a gzip archive and analyze the contents,
which is why the Defender file playbook submits the retrieved bytes as-is; TAXII
discovery, Basic auth, and that each element of a collection's `objects` response is a
full STIX bundle rather than a flat indicator, requiring client-side filtering to
`type == "indicator"`; that `/v3/hunt/live/list` and `/v3/sandbox/sandboxtask/my-tasks`
both accept only a relative `since` window in minutes, not absolute start/end
timestamps; and private-community isolation by account entitlement.

Verified in a live Microsoft Sentinel workspace, 15 to 20 October 2026: both data
connectors connected from the content hub with the key read from Key Vault, with data
arriving in ThreatIntelIndicators; every one of the 15 playbook templates deploying; the four enrichment
playbooks, the URL and storage blob sandbox playbooks and the check quota playbook
running on a real incident and commenting on it, with sandbox rows landing in
PolySwarmSandbox_CL; and every analytics rule, hunting query, workbook query and
connector page query running without error.

Still open, and the reason two playbooks ship as preview: the Office 365 Outlook "list
attachments by message id" call against a real Mail entity, and the Defender for
Endpoint advanced hunting query, live response flow and managed-identity token
audience. Neither has been run against a live Exchange Online mailbox or Defender for
Endpoint tenant.
