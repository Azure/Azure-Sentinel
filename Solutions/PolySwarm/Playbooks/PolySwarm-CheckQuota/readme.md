# PolySwarm-CheckQuota

Reads PolySwarm account features and remaining API and sandbox uses
(`GET /v3/public/accounts`) and comments on the incident when API or sandbox quota is
below a configured warning threshold, a pattern also seen in other vendors' published
quota-check playbooks. Matters because sandbox detonations are metered: this playbook
warns before a quota is exhausted rather than after a submission fails.

File: `Playbooks/PolySwarm-CheckQuota/azuredeploy.json`, Microsoft Sentinel
incident-triggered.

## Summary

Reads the PolySwarm API key from Key Vault, calls `GET /v3/public/accounts`, and
compares remaining API and sandbox usage against two independent percentage
thresholds. If either is crossed, posts a warning comment on the triggering incident.

Revision 2: HTTP 204 with an empty body from the account call is reported as no account record
and is never parsed.

## Prerequisites

- A Microsoft Sentinel workspace, and permission to deploy Logic Apps and assign RBAC
  roles.
- A PolySwarm API key stored as a secret in an Azure Key Vault.

## Parameters

| Parameter | Notes |
| --- | --- |
| `PlaybookName` | Defaults to `PolySwarm-CheckQuota`. |
| `KeyVaultName` | No default; required. |
| `KeyVaultSecretName` | Default `PolySwarmApiKey`. |
| `PolySwarmApiBaseUrl` | Default `https://api.polyswarm.network/v3`. |
| `ApiQuotaWarningThresholdPercent` | Default `20`. Warn when remaining API quota falls below this percentage. |
| `SandboxQuotaWarningThresholdPercent` | Default `20`. Warn when remaining sandbox quota falls below this percentage. |
| `SandboxFeatureTagFilter` | Default `sandbox`. The account-features tag this playbook reads to find the sandbox quota entry. |

## Post-deployment steps

1. Grant this playbook's managed identity **Key Vault Secrets User** on the Key Vault
   named in `KeyVaultName`.
2. Assign the **Microsoft Sentinel Responder** role on the resource group (or
   workspace) to the same managed identity.
3. Authorize the Microsoft Sentinel and Key Vault API connections if they show as
   unauthorized.
4. Attach the playbook to an automation rule triggered on incident creation. This
   playbook is Sentinel incident-triggered, not on a recurrence schedule; to check
   quota on a regular cadence independent of real incidents, attach it to an
   automation rule that runs against a scheduled synthetic incident, or trigger it
   manually.

## What the comment looks like

On a healthy account the comment reads:

```
PolySwarm quota check
API and sandbox quota are within normal range.
```

The low-quota warning has not yet been seen on a live account, because the account
used for testing has no quota limit.

## Troubleshooting

See `README.md`, "Troubleshooting", for symptoms shared across every playbook.
