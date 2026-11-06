# PolySwarm-Enrich-Ip

Reports which PolySwarm-analyzed artifacts have been observed contacting an IP address
incident entity, and posts the result as a comment on the incident.

Two variants, both built and committed:

- `Playbooks/PolySwarm-Enrich-Ip/incident-trigger/azuredeploy.json`, incident-triggered,
  named `PolySwarm-Enrich-IP-IncidentTriggered`.
- `Playbooks/PolySwarm-Enrich-Ip/entity-trigger/azuredeploy.json`, entity-triggered, named
  `PolySwarm-Enrich-IP-EntityTriggered`.

Both read the API key from Key Vault, matching the file hash and URL playbooks.

## Summary

An automation rule runs this playbook when an incident is created. It extracts every
`Ip` entity from the incident and runs two lookups per address: a bare-host URL search
for an engine-count verdict, and the PolySwarm IOC search for associated sample hashes
(up to `SampleHashCount` listed). The verdict comes from detection counts, never
PolyScore: no engine coverage is unknown, no malicious engine is benign, every engine
malicious is malicious, and anything between is suspicious. A 204 (not found) on either
lookup is handled without failing the run, and the association line still posts. An association is
a pivot lead, not by itself evidence the address is malicious; common infrastructure
(public DNS resolvers, CDNs) is contacted by a large volume of both malicious and
benign software, so a long association list is expected and not itself a verdict.

## Prerequisites

- An Azure subscription with Microsoft Sentinel enabled on a Log Analytics workspace.
- Permission to deploy Logic Apps and API connections, and to assign RBAC roles.
- A PolySwarm API key with access to the community you intend to query.

## Parameters

| Parameter | Notes |
| --- | --- |
| `PlaybookName` | Defaults to `PolySwarm-Enrich-IP-IncidentTriggered`. |
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

Rendered from a live response in a test workspace on 20 October 2026, for a public DNS resolver (sample hashes shortened here):

PolySwarm IP enrichment
IP: 8.8.8.8
Verdict (engine detection counts): Benign (0 malicious of 3 engines)
PolyScore (reference only, not used for the verdict): 0.3346
PolySwarm report: https://polyswarm.network/scan/results/file/838c4c2...
Association, a pivot lead: Associated artifacts: 50+ (first page only, more available)
Sample: 6e09c2c6..., f1d0250f..., a9d6c8ac..., (ten in all)

Interpretation: association means these artifacts were observed contacting this
address during analysis. It is a pivot lead, not a verdict; the verdict line comes from
engine detection counts on the bare address. Shared infrastructure and public services
accumulate large association counts without being malicious (a query for 8.8.8.8 fills
a page), so weigh the count against how specific the address is before acting.

## Troubleshooting

See `README.md`, "Troubleshooting", for symptoms shared across every playbook.
