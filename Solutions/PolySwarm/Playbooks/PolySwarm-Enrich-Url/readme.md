# PolySwarm-Enrich-Url

Enriches a URL incident entity with PolySwarm's multi-engine verdict, DNS resolution,
ASN and TLS certificate detail, and posts the result as a comment on the incident.

Two variants, both built and committed:

- `Playbooks/PolySwarm-Enrich-Url/incident-trigger/azuredeploy.json`, incident-triggered,
  named `PolySwarm-Enrich-URL-IncidentTriggered`.
- `Playbooks/PolySwarm-Enrich-Url/entity-trigger/azuredeploy.json`, entity-triggered, named
  `PolySwarm-Enrich-URL-EntityTriggered`.

Both read the API key from Key Vault, matching the file hash playbook.

## Summary

An automation rule runs this playbook when an incident is created. It extracts every
`Url` entity from the incident and calls `GET /search/url` per URL, then posts the
verdict, detections and available DNS, ASN and certificate detail as a comment. A URL
PolySwarm has never seen (HTTP 204, empty body) gets an explicit "no result" comment.

The verdict comes from engine detection counts, never PolyScore, which is the same
constant on every URL artifact. No engine coverage (total of 0 or missing) is unknown,
no malicious engine is benign, every engine malicious is malicious, and anything between
is suspicious. PolyScore is shown for reference only. The report link uses the artifact
SHA-256.

## Prerequisites

- An Azure subscription with Microsoft Sentinel enabled on a Log Analytics workspace.
- Permission to deploy Logic Apps and API connections, and to assign RBAC roles.
- A PolySwarm API key with access to the community you intend to query.

## Parameters

| Parameter | Notes |
| --- | --- |
| `PlaybookName` | Defaults to `PolySwarm-Enrich-URL-IncidentTriggered`. |
| `KeyVaultName` | Name of the Azure Key Vault holding the PolySwarm API key. No default; required. |
| `KeyVaultSecretName` | Name of the secret in `KeyVaultName` that holds the PolySwarm API key. Defaults to `PolySwarmApiKey`. |
| `PolySwarmCommunity` | `default` unless you have a private community. |
| `PolySwarmApiBaseUrl` | Leave as-is unless directed otherwise. |

## Post-deployment steps

1. Grant the playbook's managed identity **Key Vault Secrets User** on the Key Vault
   named in `KeyVaultName`.
2. Assign the **Microsoft Sentinel Responder** role to the same managed identity,
   scoped to the resource group or Sentinel workspace.
3. Attach the playbook to an automation rule triggered on incident creation.

## What the comment looks like

Rendered from a live response in a test workspace on 20 October 2026, for the EICAR test URL:

PolySwarm URL enrichment
URL: http://malware.wicar.org/data/eicar.com
Verdict (engine detection counts): Suspicious (PolyScore 0.2321, reference only, not used for the verdict)
Detections: 2 malicious / 2 benign of 4 engines
Malicious engines: Quttera, Notmining
First seen: 2021-12-29T02:19:45 | Last seen: 2022-04-05T20:11:25
PolySwarm report: https://polyswarm.network/scan/results/file/ab302eb...

## Troubleshooting

See `README.md`, "Troubleshooting", for symptoms shared across every playbook.
