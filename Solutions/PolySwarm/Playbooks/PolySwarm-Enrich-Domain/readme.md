# PolySwarm-Enrich-Domain

Reports which PolySwarm-analyzed artifacts have been observed in association with a
domain (DNS resolution) incident entity, and posts the result as a comment on the
incident.

Two variants, both built and committed:

- `Playbooks/PolySwarm-Enrich-Domain/incident-trigger/azuredeploy.json`, incident-triggered,
  named `PolySwarm-Enrich-Domain-IncidentTriggered`.
- `Playbooks/PolySwarm-Enrich-Domain/entity-trigger/azuredeploy.json`, entity-triggered
  (Sentinel entity type `DNSResolution`), named
  `PolySwarm-Enrich-Domain-EntityTriggered`.

Both built to the same shape as the file hash, URL and IP playbooks: read the API key
from Key Vault through their own managed identity.

## Summary

An automation rule runs this playbook when an incident is created. It extracts every
`DnsResolution` (domain) entity from the incident and runs two lookups per domain: a
bare-host URL search for an engine-count verdict, and the PolySwarm IOC search for the
association count and up to `SampleHashCount` sample hashes. The verdict comes from
detection counts, never PolyScore: no engine coverage is unknown, no malicious engine is
benign, every engine malicious is malicious, and anything between is suspicious. A 204
(not found) on either lookup is handled without failing the run, and the association
line still posts. As with the IP playbook, an association is a pivot lead,
not by itself evidence the domain is malicious.

## Prerequisites

- An Azure subscription with Microsoft Sentinel enabled on a Log Analytics workspace.
- Permission to deploy Logic Apps and API connections, and to assign RBAC roles.
- A PolySwarm API key with access to the community you intend to query, stored as a
  secret in an Azure Key Vault.

## Parameters

| Parameter | Notes |
| --- | --- |
| `PlaybookName` | Defaults to `PolySwarm-Enrich-Domain-IncidentTriggered`. |
| `KeyVaultName` | Name of the Azure Key Vault holding the PolySwarm API key. No default; required. |
| `KeyVaultSecretName` | Name of the secret in `KeyVaultName` that holds the PolySwarm API key. Defaults to `PolySwarmApiKey`. |
| `PolySwarmCommunity` | `default` unless you have a private community. |
| `PolySwarmApiBaseUrl` | Leave as-is unless directed otherwise. |
| `SampleHashCount` | Maximum number of associated sample hashes listed in the comment. Default `10`. |

## Post-deployment steps

1. Grant the playbook's managed identity **Key Vault Secrets User** on the Key Vault
   named in `KeyVaultName`.
2. Assign the **Microsoft Sentinel Responder** role to the same managed identity,
   scoped to the resource group or Sentinel workspace.
3. Attach the playbook to an automation rule triggered on incident creation.

## What the comment looks like

Rendered from a live response in a test workspace on 20 October 2026, for example.com (sample hashes shortened here):

PolySwarm Domain enrichment
Domain: example.com
Verdict (engine detection counts): Benign (0 malicious of 6 engines)
PolyScore (reference only, not used for the verdict): 0.3346
PolySwarm report: https://polyswarm.network/scan/results/file/a379a6f...
Association, a pivot lead: Associated artifacts: 50+ (first page only, more available)
Sample: b6c98f71..., dbb9f951..., 13440f95..., (ten in all)

Interpretation: association means these artifacts were observed contacting this
domain during analysis. It is a pivot lead, not a verdict; the verdict line comes from
engine detection counts on the bare domain. Shared infrastructure and CDN-fronted
domains accumulate large association counts without being malicious, so weigh the
count against how specific the domain is before acting.

## Troubleshooting

See `README.md`, "Troubleshooting", for symptoms shared across every playbook.
