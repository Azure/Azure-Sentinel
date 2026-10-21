# PolySwarm-Sandbox-StorageBlob

For every File entity on a Microsoft Sentinel incident, reads the matching blob from a
fixed Azure Storage container and detonates it in the PolySwarm sandbox (CAPE or
Triage), polling until complete or timeout and commenting verdict, score, malware
family, MITRE ATT&CK techniques and a report link back to the incident. Never creates
an incident.

File: `Playbooks/PolySwarm-Sandbox-StorageBlob/azuredeploy.json`, incident-triggered
only (no entity-triggered variant).

Defaults to your **private** PolySwarm community; refuses to submit to the public
community unless `AllowPublicCommunity` is explicitly set to `true`.

## Summary

Same three-step submission, poll, verdict-derivation and `PolySwarmSandbox_CL` write
as `PolySwarm-Sandbox-Url` (see that playbook's readme for the shared mechanics). The
artifact source differs: this playbook reads the incident's File entity for a file
name, then fetches the blob's content from a fixed `StorageAccountName`/`ContainerName`
pair (deployment parameters) using the Azure Blob Storage connector's "get blob
content by path" operation, expecting an upstream process (for example a SOAR
evidence-capture step) to have already placed the file there.

This differs from the blob-triggered detonation playbooks published by other vendors,
which it is modeled on: those trigger directly off a blob-added event and, having no
incident, write to a custom Log Analytics table for an analytics rule to pick up.
This playbook is Microsoft Sentinel incident-triggered instead, so it always has an
incident to comment on and detonates the exact blob a File entity on the incident
names.

Verified live in a test workspace on 20 October 2026: the playbook read the File
entity from the incident, fetched the blob from the container and submitted it.

## No result (HTTP 204)

PolySwarm answers HTTP 204 with an empty body when it has nothing for a request (not found). The status poll checks for 204 explicitly, ends the loop with a NOT_FOUND state and never reads the empty body. The incident gets a comment saying PolySwarm returned no result and no verdict is available, and the PolySwarmSandbox_CL row, where one is written, carries the verdict unknown. Task creation returns 200.

All polling loops are bounded twice: a count limit and a timeout (TimeoutMinutes, default 15 minutes).

## Prerequisites

- A Microsoft Sentinel workspace, and permission to deploy Logic Apps and assign RBAC
  roles.
- A PolySwarm API key with the sandbox detonation entitlement, stored as a secret in
  an Azure Key Vault.
- A private PolySwarm community to detonate in.
- An Azure Storage account and container that already holds the files referenced by
  incident File entities.
- The shared sandbox results infrastructure
  (`Data Connectors/PolySwarmSandboxResults/azuredeploy.json`) deployed first.

## Parameters

Same shape as `PolySwarm-Sandbox-Url` (see that playbook's readme for the full table),
plus two storage-specific parameters:

| Parameter | Notes |
| --- | --- |
| `StorageAccountName` | The storage account holding the blobs to detonate. No default; required. |
| `ContainerName` | The container within that account. No default; required. |

All other parameters (`PlaybookName` default
`PolySwarm-Sandbox-StorageBlob-IncidentTriggered`, `Community`,
`AllowPublicCommunity`, `Provider`, `VmSlug`, `NetworkEnabled`, `TimeoutMinutes`,
`KeyVaultName`, `KeyVaultSecretName`, `PolySwarmApiBaseUrl`,
`MaliciousScoreThreshold`, `SuspiciousScoreThreshold`, `DceLogsIngestionEndpoint`,
`DcrImmutableId`, `StreamName`, `DcrResourceId`, `create_role_assignment`) are
identical in name, type and default to `PolySwarm-Sandbox-Url`.

## Post-deployment steps

1. Assign the **Microsoft Sentinel Responder** role on the resource group (or
   workspace) to this playbook's managed identity.
2. Assign the **Key Vault Secrets User** role on the Key Vault (`KeyVaultName`) to
   the same managed identity.
3. Assign the **Storage Blob Data Reader** role on the storage account
   (`StorageAccountName`) to the same managed identity.
4. **Monitoring Metrics Publisher** on the Data Collection Rule (`DcrResourceId`) is
   assigned automatically when `create_role_assignment` is `true` (default);
   otherwise assign it manually.
5. Authorize the Microsoft Sentinel, Azure Key Vault and Azure Blob Storage API
   connections if they show as unauthorized.
6. Attach the playbook to an automation rule so it runs on incidents with a File
   entity, or run it manually.

## What the comment looks like

Same format as `PolySwarm-Sandbox-Url`: derived verdict (not a PolySwarm verdict
field), score, malware family, MITRE ATT&CK techniques, best-effort report link.

Rendered from a live response in a test workspace on 20 October 2026, for the EICAR test file uploaded to a blob container. EICAR is on
PolySwarm's known-good list, so it is not detonated and has no sandbox score:

PolySwarm sandbox detonation
Artifact: eicar.com.txt
Verdict: known good (no sandbox score)
This artifact matched PolySwarm's known-good allowlist and was not detonated.
SHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
Task id: 32724744069168160

A file that is detonated gets the same lines as `PolySwarm-Sandbox-Url`: derived
verdict and score, provider, MITRE ATT&CK techniques, community and report link.

## Troubleshooting

See `README.md`, "Troubleshooting", plus `Playbooks/PolySwarm-Sandbox-Url/readme.md`
for sandbox-specific symptoms (report link, community echoing). Specific to this
playbook: if a blob is not found, confirm `StorageAccountName`/`ContainerName` point
to where the upstream process actually places files, and confirm the incident's File
entity file name matches the blob name exactly.
