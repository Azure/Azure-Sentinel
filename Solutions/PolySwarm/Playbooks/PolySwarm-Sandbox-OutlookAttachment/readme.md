# PolySwarm-Sandbox-OutlookAttachment

**Preview.** This playbook deploys and passes every local check, but it has not yet
been run against a live Exchange Online mailbox. If you try it, please tell us how it
went at support@polyswarm.io.

For every MailMessage entity on a Microsoft Sentinel incident, retrieves the message's
attachments via the Office 365 Outlook connector and detonates each in the PolySwarm
sandbox (CAPE or Triage), polling until complete or timeout and commenting verdict,
score, malware family, MITRE ATT&CK techniques and a report link back to the incident.
Never creates an incident.

File: `Playbooks/PolySwarm-Sandbox-OutlookAttachment/azuredeploy.json`, incident-triggered
only (no entity-triggered variant).

Defaults to your **private** PolySwarm community; refuses to submit to the public
community unless `AllowPublicCommunity` is explicitly set to `true`.

## Summary

Same three-step submission, poll, verdict-derivation and `PolySwarmSandbox_CL` write
as `PolySwarm-Sandbox-Url` (see that playbook's readme for the shared mechanics), with
one difference in how the artifact is obtained: this playbook reads the incident's
Mail entity, calls the Office 365 Outlook connector's "Get email" and "List
attachments" operations by message id, then detonates each attachment.

This differs from the mailbox-triggered attachment-detonation playbooks published by
other vendors, which it is modeled on: those trigger directly off an Office 365
mailbox ("When a new email arrives") and, having no incident, either send an email or
write to a custom Log Analytics table for an analytics rule to pick up. This playbook
is Microsoft Sentinel incident-triggered instead, so it always has an incident to
comment on and detonates the exact attachment the incident's own Mail entity
references, rather than polling a mailbox independently of any incident.

The step that fetches attachments by the incident's Mail entity is built on the
documented Office 365 Outlook connector operations. It has not yet been run against a
live Exchange Online mailbox, which is why this playbook is in preview.

## No result (HTTP 204)

PolySwarm answers HTTP 204 with an empty body when it has nothing for a request (not found). The status poll checks for 204 explicitly, ends the loop with a NOT_FOUND state and never reads the empty body. The incident gets a comment saying PolySwarm returned no result and no verdict is available, and the PolySwarmSandbox_CL row, where one is written, carries the verdict unknown. Task creation returns 200.

All polling loops are bounded twice: a count limit and a timeout (TimeoutMinutes, default 15 minutes).

## Prerequisites

- A Microsoft Sentinel workspace, and permission to deploy Logic Apps and assign RBAC
  roles.
- A PolySwarm API key with the sandbox detonation entitlement, stored as a secret in
  an Azure Key Vault.
- A private PolySwarm community to detonate in.
- An Office 365 mailbox connection with permission to read the mail message
  referenced by the incident's Mail entity.
- The shared sandbox results infrastructure
  (`Data Connectors/PolySwarmSandboxResults/azuredeploy.json`) deployed first.

## Parameters

Same shape as `PolySwarm-Sandbox-Url`: `PlaybookName` (default
`PolySwarm-Sandbox-OutlookAttachment-IncidentTriggered`), `Community`,
`AllowPublicCommunity` (default `false`), `Provider` (default `triage`), `VmSlug`
(default `windows11-21h2-x64`), `NetworkEnabled` (default `true`), `TimeoutMinutes`
(default `15`), `KeyVaultName`, `KeyVaultSecretName` (default `PolySwarmApiKey`),
`PolySwarmApiBaseUrl`, `MaliciousScoreThreshold` (default `7`),
`SuspiciousScoreThreshold` (default `4`), `DceLogsIngestionEndpoint`,
`DcrImmutableId`, `StreamName` (default `Custom-PolySwarmSandboxResults`),
`DcrResourceId`, `create_role_assignment` (default `true`). See
`Playbooks/PolySwarm-Sandbox-Url/readme.md` for the full parameter table; this
playbook's parameters are identical in name, type and default.

## Post-deployment steps

1. Assign the **Microsoft Sentinel Responder** role on the resource group (or
   workspace) to this playbook's managed identity.
2. Assign the **Key Vault Secrets User** role on the Key Vault (`KeyVaultName`) to
   the same managed identity.
3. **Monitoring Metrics Publisher** on the Data Collection Rule (`DcrResourceId`) is
   assigned automatically when `create_role_assignment` is `true` (default);
   otherwise assign it manually.
4. Authorize the Microsoft Sentinel, Azure Key Vault and Office 365 API connections
   if they show as unauthorized. The Office 365 connection is a mailbox sign-in, not
   an Azure RBAC role.
5. Attach the playbook to an automation rule so it runs on incidents with a Mail
   entity, or run it manually.

## What the comment looks like

Same format as `PolySwarm-Sandbox-Url`: derived verdict (not a PolySwarm verdict
field), score, malware family, MITRE ATT&CK techniques, best-effort report link, one
comment per attachment detonated.

No example comment is shown here yet, because this playbook is still in preview (see
the note at the top of this page).

## Troubleshooting

See `README.md`, "Troubleshooting", plus `Playbooks/PolySwarm-Sandbox-Url/readme.md`
for sandbox-specific symptoms (report link, community echoing). Specific to this
playbook: if attachments are not found or the message cannot be read, confirm the
Office 365 connection has access to the mailbox the incident's Mail entity references,
and confirm the message id addressing works against your tenant's mail entity shape,
since this has not been verified against a live incident.
