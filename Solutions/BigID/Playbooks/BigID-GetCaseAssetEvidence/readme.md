# BigID-GetCaseAssetEvidence

Author: BigID

## Overview

`BigID-GetCaseAssetEvidence` is an on-demand Microsoft Sentinel Playbook (Azure Logic App) designed to be invoked directly from the **BigID DSPM Posture & Case Triage** Workbook (`BigIDDSPMOverview`) via an Azure Resource Manager (ARM) Action.

When a SOC analyst selects a DSPM case in the Workbook and triggers this Playbook:
1. It exchanges the configured BigID API refresh token (`BigIDToken`) for a short-lived BigID system token via `GET https://<bigidFqdn>/api/v1/refresh-access-token`.
2. It queries the BigID Data Catalog API (`GET https://<bigidFqdn>/api/v1/data-catalog/?queryType=SIMPLE_PROJECT&limit=1000`) filtered by the case's `dataSourceName` and `policyName`.
3. It projects the returned catalog objects and ingests them in batches of 200 into the `BigIDDSPMEvidence_CL` custom table using the Azure Monitor Logs Ingestion API (`Custom-BigIDDSPMEvidence_CL` stream on `BigIDDSPMCasesDCR`) authenticated via the Playbook's system-assigned Managed Identity.

## Prerequisites

1. **BigID DSPM CCF Data Connector deployed**: Deploying the BigID solution's Codeless Connector Framework (CCF) data connector creates the `BigIDDSPMEvidence_CL` table, the Data Collection Endpoint (DCE), and the `BigIDDSPMCasesDCR` Data Collection Rule (DCR).
2. **BigID API Refresh Token**: A BigID user refresh token with permissions to access the BigID Data Catalog API (`/api/v1/data-catalog/`).
3. **Azure RBAC Permissions for Deployment**: Permissions to deploy Azure Logic Apps and create `Monitoring Metrics Publisher` (`3913510d-42f4-4e42-8a64-420c390055eb`) and `Monitoring Reader` (`43d0d8ad-25c7-4714-9337-8ba259a9fe05`) role assignments in the target resource group (e.g., `Owner` or `User Access Administrator` + `Contributor`).

## Deployment

You can deploy this Playbook from Microsoft Sentinel **Content Hub** (as part of the **BigID** solution) or directly using the ARM template in this folder (`azuredeploy.json`).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FBigID%2FPlaybooks%2FBigID-GetCaseAssetEvidence%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FBigID%2FPlaybooks%2FBigID-GetCaseAssetEvidence%2Fazuredeploy.json)

### Deployment Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `PlaybookName` | string | Name of the Logic App/Playbook (default: `BigID-GetCaseAssetEvidence`). |
| `BigIDToken` | securestring | BigID API refresh token. Stored securely and masked in Logic App run history. |

> **Automatic DCE / DCR discovery:** The Playbook automatically discovers the `BigIDDSPMCasesDCR` Data Collection Rule (including Sentinel-prefixed names such as `Microsoft-Sentinel-BigIDDSPMCasesDCR-*`) and its linked Data Collection Endpoint in the resource group at runtime via its Managed Identity - no workspace name, DCE URI, or DCR ID input is required.

## Post-Deployment / Workbook ARM Action Usage

1. Verify that the Playbook's system-assigned Managed Identity has the **Monitoring Metrics Publisher** role assigned on the resource group containing `BigIDDSPMCasesDCR` (automatically provisioned by the ARM template).
2. Open **Microsoft Sentinel** -> **Workbooks** -> **BigID DSPM Posture & Case Triage** (`BigIDDSPMOverview`).
3. Navigate to the **Case & Objects Triage** tab and select the deployed `BigID-GetCaseAssetEvidence` Playbook in the Playbook parameter selector.
4. Select any case row in the **DSPM Cases** table.
5. Switch the objects view mode to **Pull up to 1,000 Objects from BigID (Playbook)** and click **Fetch up to 1,000 Objects from BigID**.
6. Wait approximately 1-2 minutes for Log Analytics ingestion to complete, then click **Refresh** on the **Full Catalog Objects from BigID Playbook** table to inspect the results from `BigIDDSPMEvidence_CL`.

## Troubleshooting

- **401 / 403 from BigID API (`Exchange_BigID_Refresh_Token` or `Fetch_Catalog_Objects_SimpleProject`)**: Verify that `BigIDToken` is a valid, non-expired BigID refresh token and that the associated BigID user has permission to query `/api/v1/data-catalog/`. Confirm that the BigID instance is reachable from Azure Logic Apps over HTTPS.
- **403 from Azure Monitor Logs Ingestion API (`Ingest_To_Log_Analytics`)**: Confirm the Playbook's system-assigned Managed Identity has the **Monitoring Metrics Publisher** role on `BigIDDSPMCasesDCR` (or its parent resource group). Allow a few minutes for RBAC propagation immediately after deployment.
- **400 / 404 from Logs Ingestion API or deployment fails resolving DCE/DCR**: Ensure the BigID DSPM CCF Data Connector is deployed in the same resource group as the Playbook so `BigIDDSPMCasesDCR` and its linked Data Collection Endpoint exist before deploying the Playbook.
- **No rows appearing in Workbook after successful run**: Log Analytics ingestion typically takes 1-2 minutes. Confirm the Playbook run succeeded in Azure Portal (**Logic App -> Runs history**) and verify `Check_Has_Records` evaluated to `true`.
