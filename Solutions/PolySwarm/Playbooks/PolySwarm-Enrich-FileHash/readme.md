# PolySwarm-Enrich-FileHash

Enriches a file hash (MD5, SHA-1 or SHA-256) incident entity with PolySwarm's
multi-engine verdict and posts the result as a comment on the incident.

Two variants, both built and committed:

- `Playbooks/PolySwarm-Enrich-FileHash/incident-trigger/azuredeploy.json`, incident-triggered,
  named `PolySwarm-Enrich-FileHash-IncidentTriggered`. Runs on every FileHash entity
  on an incident.
- `Playbooks/PolySwarm-Enrich-FileHash/entity-trigger/azuredeploy.json`, entity-triggered,
  named `PolySwarm-Enrich-FileHash-EntityTriggered`. Runs on a single FileHash entity
  selected from an incident (or from the entity blade directly).

Both take the same parameters, listed below. Add a section here once it lands.

## Summary

An automation rule runs this playbook when an incident is created. It extracts every
`FileHash` entity from the incident, detects the hash type from its length (32 = MD5,
40 = SHA1, 64 = SHA256), and calls two PolySwarm endpoints per hash: the hash lookup
(verdict, PolyScore, the full per-engine assertion list, PolyUnite classification, PE
metadata, permalink) and a best-effort metadata query (classification tags, normalized
family, sandbox scores and MITRE ATT&CK techniques). Both calls' results merge into one
comment; a hash PolySwarm has never seen still gets an explicit comment, and the
comment now distinguishes three "no usable result" cases: a rejected API key, an
unreachable PolySwarm API, and a genuine no-result outcome, rather than one generic
message.

Revision 2: a hash with zero engine detections is reported as Unknown rather than benign, and
HTTP 204 with an empty body is treated as not found on every PolySwarm call. When PolySwarm
holds attribution tags for the hash (`/v3/tags/link`), the comment gains one extra line;
a 204 there is the normal answer and adds nothing.

## Prerequisites

- An Azure subscription with Microsoft Sentinel enabled on a Log Analytics workspace.
- Permission to deploy Logic Apps and API connections, and to assign RBAC roles.
- A PolySwarm API key with access to the community you intend to query, stored as a
  secret in an Azure Key Vault. The Key Vault must have
  `enabledForTemplateDeployment` set to `true`, or the connection resource deploys
  against RBAC only, which is the default and is sufficient.

## Parameters

| Parameter | Notes |
| --- | --- |
| `PlaybookName` | Defaults to `PolySwarm-Enrich-FileHash-IncidentTriggered`. |
| `KeyVaultName` | Name of the Azure Key Vault holding the PolySwarm API key. The vault must exist in the same subscription. No default; required. |
| `KeyVaultSecretName` | Name of the secret in `KeyVaultName` that holds the PolySwarm API key. Defaults to `PolySwarmApiKey`. |
| `PolySwarmCommunity` | `default` unless you have a private community. |
| `PolySwarmApiBaseUrl` | Leave as-is unless directed otherwise. |
| `PolySwarmMaliciousThreshold` | Fallback PolyScore threshold, used only when the API returns no explicit verdict. Default `0.8`; at or above half that reports "Suspicious". A string, because ARM templates have no float parameter type. |

The playbook no longer accepts the API key as a plain deployment parameter. It reads
the key at runtime through its own Key Vault API connection, and every HTTP action
that carries the key marks both inputs and outputs secure, so the key never appears in
run history.

## Post-deployment steps

1. Grant this playbook's system-assigned managed identity the **Key Vault Secrets
   User** role on the Key Vault named in `KeyVaultName`.
2. Assign the **Microsoft Sentinel Responder** role on the resource group (or
   workspace) to the same managed identity. The playbook fails with a 403 reading
   entities or posting comments until this is done.
3. Authorize the Microsoft Sentinel and Key Vault API connections in the Azure portal
   if they show as unauthorized. These are Logic Apps connection resources, managed in
   the Azure portal regardless of which portal you use for Microsoft Sentinel itself.
4. Attach the playbook to an automation rule triggered on incident creation. See
   `docs/deployment.md`.

## What the comment looks like

Rendered from a live response for a LockBit/BlackMatter sample:

PolySwarm enrichment
Hash (SHA256): 5da5a1e3983982a92341953929d4c7726da65fe5125d264dd8932a870f2f154a
Assessment: Malicious (PolyScore 0.9999)
Detections: 6 malicious / 2 benign of 8 engines
Malicious engines: Qihoo 360, SecondWrite, SecureAge, Lionic, DrWeb, Filseclab, Crowdstrike Falcon ML, NanoAV, ClamAV, SentinelOne Static ML, Ikarus
Malware family: BlackMatter
Labels: ransomware, trojan
Tags: Ransomware, Trojan, PE32, Windows
Sandbox-reported family: lockbit
Sandbox scores: CAPE 8 / Triage 10
MITRE ATT&CK: T1027, T1070.004, T1082, T1486, T1489, T1542.003, T1614.001
File type: PE32 executable (GUI) Intel 80386, for MS Windows
Imphash: 41fb8cb2943df6de998b35a9d28668e8
Packer: AHTeam EP Protector 0.3 (fake PCGuard 4.03-4.15)
First seen: 2023-02-26 | Last seen: 2026-07-09
PolySwarm report: https://polyswarm.network/scan/results/file/5da5a1e.../75499664076494037

Every field is optional in the output: a line is omitted rather than printed as "n/a"
when the underlying data is absent, so a sparse record still produces a clean comment.
A hash PolySwarm has never seen produces a plain "no result" comment instead. If the
Key Vault lookup itself fails, the comment says the API key could not be retrieved and
names the parameter to check, rather than posting a misleading "no result" for a hash
that was never actually queried.

## Troubleshooting

See `README.md`, "Troubleshooting", for symptoms shared across every playbook. Playbook
specific: a comment posted with no Tags, Sandbox or ATT&CK lines means the secondary
metadata call failed, was rate-limited, or returned nothing; this is allowed to happen
by design and the primary verdict is unaffected.
