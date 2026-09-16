---
name: sentinel-xdr-solution-deployer
description: Deploy and verify Sentinel Analytic Rules and Defender XDR Custom Detections disabled in an approved non-production environment.
---

# Deploy Sentinel and XDR detections safely

Use this skill only after conversion, runtime validation, and packaging have
passed. Deployment is a write operation and always requires explicit user
approval for the exact subscription, resource group, workspace, solution, and
deployment mode.

## Modes

### Package acceptance

Validate and optionally deploy `Package\mainTemplate.json` as a complete
solution:

- `E5Flavor=false` validates the Sentinel Analytic Rule installation path.
- `E5Flavor=true` validates the Defender XDR Custom Detection installation
  path.

Run an Azure Resource Manager validation or what-if before create. Do not
enable Custom Detection Content Hub registration unless explicitly requested
and supported by the live resource provider.

### Alert-parity preparation

Deploy both sides of every reviewed pair disabled:

```powershell
sentinel-xdr-migration deploy-analytic-rules `
  --solution "<solution-path>" `
  --workspace-resource-id "<workspace-arm-id>"

sentinel-xdr-migration deploy --solution "<solution-path>"
```

The first command writes `XDR Detections\deployment.sentinel.json`. The second
writes `XDR Detections\deployment.graph.json`.

## Safety gates

Before any write:

1. Confirm the target is a non-production lab.
2. Show the subscription, resource group, workspace, tenant, solution, package
   version, mode, and expected rule count.
3. Require explicit approval for those exact values.
4. Confirm every Custom Detection YAML has `properties.status: disabled`.
5. Stop on unresolved conversion review, invalid KQL, missing entity mappings,
   duplicate IDs, or count mismatches.
6. Never infer permission from Entra Global Administrator. Verify Azure RBAC
   and Microsoft Graph Custom Detection scopes separately.
7. Ask before launching interactive authentication.

## Verification

Deployment passes only when:

- every requested ARM or Graph operation succeeds;
- deployed AR and CD IDs match the reviewed source manifest;
- every deployed rule is disabled;
- display names, queries, schedules, severities, tactics, and entity mappings
  match the generated artifacts; and
- the deployment reports contain no failed or silently skipped item.

If Graph read permission is unavailable, report verification as blocked even
when the write deployment reports success. Do not claim live status solely
from the source template.

Do not enable a rule in this skill. Rule enablement belongs exclusively to
`sentinel-xdr-alert-parity-validator`, which must disable every test rule on
completion or abort.
