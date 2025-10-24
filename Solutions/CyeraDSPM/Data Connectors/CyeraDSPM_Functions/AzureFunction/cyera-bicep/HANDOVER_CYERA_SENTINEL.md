# HANDOVER — Cyera → Microsoft Sentinel (Bicep package)

## Included
- DCE/DCR with canonical streams and output projections
- KQL transforms (placeholders) and Log Analytics table schemas
- Function App (Linux/Python) with MSI and app settings
- RBAC for DCR/DCE (+ optional Storage if blob-state enabled)
- Helper script to set WEBSITE_RUN_FROM_PACKAGE via SAS URL

## Canonical names
- Inputs: Custom-CyeraAssets_SRC, Custom-CyeraIdentities_SRC, Custom-CyeraClassifications_SRC, Custom-CyeraIssues_SRC
- Outputs (tables): CyeraAssets_MS_CL, CyeraAssets_CL, CyeraIdentities_CL, CyeraClassifications_CL, CyeraIssues_CL

## How to resume
1) Edit `infra/parameters/main.sample.bicepparam` (location, workspaceResourceId, functionAppName, Cyera creds).
2) Deploy `infra/main.bicep` to the target RG.
3) Deploy code:
   - `az functionapp deployment source config-zip ...` **or**
   - `scripts/upload_function_package.sh ...` to set run-from-package
4) Push a small sample to `Custom-CyeraAssets_SRC` and query MS/Extended tables.

## Notes
- Keep DCE/DCR/Workspace in the same region.
- Tables are created via `deploymentScripts` (az rest).
- For production secrets, use Key Vault references in app settings.
