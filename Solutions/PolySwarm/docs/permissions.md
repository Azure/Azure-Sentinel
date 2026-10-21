# Permissions reference

Every Azure role and API permission a component of this solution needs, and why. Grant
only what is listed here; every entry is the least-privilege option for what that
component does. See `docs/deployment.md` for when to assign each one during
deployment.

Every playbook authenticates as its own system-assigned managed identity. None of
them use a shared identity, a client secret, or a user's own credentials, with the
sole exception of the Office 365 Outlook connector authorization, which is a mailbox
sign-in by design (Logic Apps connector model, not this solution's choice).

## Azure RBAC roles

| Component | Role | Scope | Why this role and not a broader one |
| --- | --- | --- | --- |
| Every enrichment playbook (file hash, URL, IP, domain; both incident and entity trigger) | Microsoft Sentinel Responder | Resource group or Sentinel workspace | Lets the playbook read incident entities and add comments. Does not grant it the ability to change analytics rules, automation rules or workspace configuration, which **Microsoft Sentinel Contributor** would. |
| Every playbook that reads the PolySwarm API key from Key Vault | Key Vault Secrets User | The Key Vault, or the individual secret if the vault uses access-policy scoping | Read-only access to secret values. Does not grant the ability to create, delete or manage secrets, keys or certificates, which **Key Vault Administrator** or **Key Vault Secrets Officer** would. |
| Every sandbox playbook (URL, Outlook attachment, Storage blob, Defender file; both trigger variants where applicable) | Microsoft Sentinel Responder | Resource group or Sentinel workspace | Same as enrichment playbooks: reads entities, posts comments. |
| Every sandbox playbook | Key Vault Secrets User | The Key Vault | Reads the PolySwarm API key, same as enrichment playbooks. |
| Every sandbox playbook | Monitoring Metrics Publisher (role id `3913510d-42f4-4e42-8a64-420c390055eb`) | The sandbox results Data Collection Rule (`DcrResourceId`, output by `Data Connectors/PolySwarmSandboxResults/azuredeploy.json`) | Lets the playbook's managed identity POST rows to `PolySwarmSandbox_CL` via the Logs Ingestion API. Each playbook template can create this assignment for itself at deployment time (`create_role_assignment` parameter, default `true`), since the DCR's resource id is known but the managed identity's principal id does not exist until the playbook itself is deployed. |
| PolySwarm-Sandbox-StorageBlob playbook | Storage Blob Data Reader | The storage account named by the `StorageAccountName` parameter | Read-only access to blob content. Does not grant write access, which the playbook never needs. |
| PolySwarm-CheckQuota playbook | Microsoft Sentinel Responder, Key Vault Secrets User | Resource group/workspace, Key Vault | Same as enrichment playbooks. No DCR role needed; this playbook does not write to `PolySwarmSandbox_CL`. |
| Hunting data connector (`PolySwarmHunting_CCF`) | None | N/A | The CCF poller writes to native `ThreatIntelIndicators` through Sentinel's own managed CCF infrastructure; the connector definition and DCR carry no separate `Microsoft.Authorization/roleAssignments` resource. Authentication to PolySwarm is the API key entered in the connector's configuration pane (`ApiKeyName: ""`, sent as a bare `Authorization: <key>` header), not an Azure role. |
| Curated feed data connector (`PolySwarmFeed_CCF`) | None | N/A | Same as the hunting connector; also writes to native `ThreatIntelIndicators` with no separate role assignment. Authenticates to the PolySwarm TAXII server with HTTP Basic auth (account number and Team API key entered in the connector's configuration pane), not an Azure role. |

## API permissions (not Azure RBAC)

| Component | Permission | Grant type | Why |
| --- | --- | --- | --- |
| PolySwarm-Sandbox-DefenderFile playbook (both trigger variants) | `Machine.LiveResponse` | Application permission on the WindowsDefenderATP API, tenant admin consent required, granted by `grant-defender-permissions.sh` | Runs the live response `GetFile` action that retrieves the file's bytes from the device. |
| PolySwarm-Sandbox-DefenderFile playbook | `Machine.ReadWrite.All` | Application permission on the WindowsDefenderATP API, tenant admin consent required | Polls the machine action and fetches the live response download link. **Corrected from an earlier draft that specified `Machine.Read.All`**: Microsoft's current API reference for both the machine-action poll and the download-link call lists `Machine.ReadWrite.All` as the required permission. Granting only `Machine.Read.All` lets live response start, but the poll and download-link calls return 403, and the playbook hangs silently until its own timeout rather than failing fast. |
| PolySwarm-Sandbox-DefenderFile playbook | `AdvancedQuery.Read.All` | Application permission on the WindowsDefenderATP API, tenant admin consent required | Runs the advanced hunting query against `DeviceFileEvents` and `DeviceProcessEvents` that finds which device and folder path last had the file, given only a SHA-256 from the incident. Note: Microsoft's advanced hunting API carries an active deprecation warning (retiring in favor of the Graph security API's `runHuntingQuery`, no end date published yet); this is the single biggest platform-risk item in this playbook. |
| PolySwarm-Sandbox-OutlookAttachment playbook | Office 365 Outlook connector authorization (mailbox sign-in) | Connector-level authorization, not an Entra application permission | Reads the mail message and lists/fetches its attachments by message id, addressed from the incident's Mail entity. This is a delegated mailbox connection, the standard Logic Apps Office 365 connector model; it is not a Graph app-role grant the way the Defender permissions are. |
| PolySwarm-Sandbox-DefenderFile playbook (both trigger variants) | Office 365 Outlook connector authorization (mailbox sign-in) | Connector-level authorization, not an Entra application permission | Only used when `RequireAnalystApproval` is `true` (default). Sends the "Send approval email" action to `ApproverEmail`, naming the incident, hash, device and full path, and waits for an Approve/Reject response before Defender live response `GetFile` runs. Same delegated mailbox model as the Outlook attachment playbook; the approval email is sent from whichever mailbox authorizes this connection, not from the managed identity. |

Grant only the three Defender for Endpoint permissions above to the file detonation
playbook's managed identity; do not grant broader Defender for Endpoint permissions
such as `Alert.ReadWrite.All`, which this solution never uses.

`grant-defender-permissions.sh` (in `Playbooks/PolySwarm-Sandbox-DefenderFile/`)
resolves the playbook's managed identity, resolves each app role id from the
WindowsDefenderATP service principal's own `appRoles` list rather than a hardcoded
GUID, and is safe to re-run (existing assignments are detected and skipped). It does
not grant the Key Vault or Monitoring Metrics Publisher roles; those are separate
Azure RBAC assignments, granted the same way as every other playbook's.

## PolySwarm-side access

The PolySwarm API key itself is scoped by your PolySwarm account, not by Azure. Which
components work depends on the entitlements on the key's account (sandbox detonation,
private community, live hunting, curated feed/TAXII), listed in `README.md`. Azure
role assignments in this document control what each component can do inside your
Azure tenant; they do not affect what the key can do against the PolySwarm API.
