# CyeraDSPM

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cyera Inc |
| **Support Tier** | Partner |
| **Support Link** | [https://support.cyera.io](https://support.cyera.io) |
| **Categories** | domains |
| **First Published** | 2025-10-15 |
| **Last Updated** | 2025-10-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyeraDSPM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyeraDSPM) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md)

**Publisher:** Cyera Inc

### [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md)

**Publisher:** Cyera Inc

The **Cyera DSPM Azure Function Connector** enables seamless ingestion of Cyera’s **Data Security Posture Management (DSPM)** telemetry — *Assets*, *Identities*, *Issues*, and *Classifications* — into **Microsoft Sentinel**.\n\nThis connector uses an **Azure Function App** to call Cyera’s REST API on a schedule, fetch the latest DSPM telemetry, and send it to Microsoft Sentinel through the **Azure Monitor Logs Ingestion API** via a **Data Collection Endpoint (DCE)** and **Data Collection Rule (DCR, kind: Direct)** — no agents required.\n\n**Tables created/used**\n\n| Entity | Table | Purpose |\n|---|---|---|\n| Assets | `CyeraAssets_CL` | Raw asset metadata and data-store context |\n| Identities | `CyeraIdentities_CL` | Identity definitions and sensitivity context |\n| Issues | `CyeraIssues_CL` | Findings and remediation details |\n| Classifications | `CyeraClassifications_CL` | Data class & sensitivity definitions |\n| MS View | `CyeraAssets_MS_CL` | Normalized asset view for dashboards |\n\n> **Note:** This v7 connector supersedes the earlier CCF-based approach and aligns with Microsoft’s recommended Direct ingestion path for Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Note**

>**NOTE:** This connector uses an **Azure Function App** and the **Azure Monitor Logs Ingestion API** (DCE + DCR, kind: Direct). Function runtime and data egress may incur charges. See [Azure Functions pricing](https://azure.microsoft.com/pricing/details/functions/).

**2. Optional Step**

>**(Optional)** Store Cyera API credentials in **Azure Key Vault** and reference them from the Function App. See [Key Vault references](https://learn.microsoft.com/azure/app-service/app-service-key-vault-references).

**3. STEP 1 — Prepare Cyera API Access**

1) Generate a **Personal Access Token** [Generating Personal Access Token](https://support.cyera.io/hc/en-us/articles/19446274608919-Personal-and-API-Tokens) in your Cyera tenant.\n2) Note **API Base URL**, **Client ID**, and **Client Secret**.

**4. STEP 2 — Choose ONE deployment option**

> Before deploying, have these values handy:
- **Cyera Function Connector Name**: `CyeraDSPMConnector`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Workspace Name**: `{{workspace-location}}`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Workspace Location**: `{{workspace-location}}`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Cyera Base URL**: `https://api.cyera.io`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Cyera Personal Access Token Client ID**: `CyeraClientID`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Cyera Personal Access Token Secret**: `CyeraSecret`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**5. Option 1**

**Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Cyera DSPM Functions and all required resources to support the connector.

1. Click the **Deploy to Azure** button below. 

	[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/{{deployment-template-uri)
2. Select the preferred **FunctionName** and **Workspace Name**. 
3. Enter the **Workspace Location**, **Cyera API Base Url**, **Personal Access Token Client ID**, and **Personal Access Token Secret**. 
>Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**6. Option 2 — Manual Deployment**

Follow the [install pack’s step-by-step guide]({{userguide-url}}.\n\n1) Create/update the 5 custom tables, data collection rule with format `sentinel-dce-<functuion_name>`, and data collection endpoint with format `sentinel-dcr-<functuion_name>` using the scripts in [install-pack-v0_7_0/scripts]({{deployment-script-zip-url}}).\n2) Deploy the Azure Function from the repo`s Function folder (Timer-trigger; schedule typically 5–15 minutes).\n3) Configure Function App settings:\n   - `CyeraBaseUrl` — Cyera API Base URL\n   - `CyeraClientId` — Client ID (PAT)\n   - `CyeraSecret` — Client Secret (PAT)\n   - `DCR_IMMUTABLE_ID` — DCR immutable ID\n   - `DCE_ENDPOINT` — Logs ingestion endpoint URL\n   - `STREAM_ASSETS`=`Custom-CyeraAssets`, `STREAM_IDENTITIES`=`Custom-CyeraIdentities`, `STREAM_ISSUES`=`Custom-CyeraIssues`, `STREAM_CLASSIFICATIONS`=`Custom-CyeraClassifications`\n4) Save and Start the Function App.

| | |
|--------------------------|---|
| **Tables Ingested** | `CyeraAssets_CL` |
| | `CyeraAssets_MS_CL` |
| | `CyeraClassifications_CL` |
| | `CyeraIdentities_CL` |
| | `CyeraIssues_CL` |
| **Connector Definition Files** | [FunctionAppDC.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyeraDSPM/Data%20Connectors/CyeraDSPM_Functions/FunctionAppDC.json) |

[→ View full connector details](../connectors/cyerafunctionsconnector.md)

## Tables Reference

This solution ingests data into **5 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyeraAssets_CL` | [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md) |
| `CyeraAssets_MS_CL` | [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md) |
| `CyeraClassifications_CL` | [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md) |
| `CyeraIdentities_CL` | [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md) |
| `CyeraIssues_CL` | [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md) |

[← Back to Solutions Index](../solutions-index.md)
