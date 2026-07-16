# TrendAI Vision One Solution for Microsoft Sentinel

## Overview

The TrendAI Vision One solution for Microsoft Sentinel provides data connectors that ingest security data from the TrendAI Vision One platform into Microsoft Sentinel using the Codeless Connector Framework (CCF).

This solution includes two data connectors:

| Connector | Description |
|-----------|-------------|
| **Workbench Alerts** | Ingests security alerts, incidents, and investigations from TrendAI Vision One Workbench |
| **OAT Detections** | Ingests Observed Attack Techniques (OAT) detections with MITRE ATT&CK mappings |

Both connectors poll the TrendAI Vision One API every **5 minutes**, retrieving data from the last 5-minute window.

---

## Solution Contents

| Component | Description |
|-----------|-------------|
| Data Connectors | 2 connectors (Workbench Alerts, OAT Detections) |
| Custom Tables | `TrendAI_XDR_WORKBENCH_V2_CL`, `TrendAI_XDR_OAT_V2_CL` |
| Parser Functions | `TrendAIWorkbench_Complete`, `TrendAIOAT_Complete` |
| Data Collection Rules | DCR-based ingestion-time transformations |
| Data Collection Endpoint | Shared DCE for both connectors |

---

## Prerequisites

### 1. Microsoft Sentinel Workspace

- An active Microsoft Sentinel workspace
- **Permissions required:**
  - Read and Write permissions on the Log Analytics workspace
  - Contributor or Owner role on the resource group

### 2. TrendAI Vision One API Token

You need an API token from your TrendAI Vision One console with appropriate permissions.

#### Steps to Generate API Token:

1. Log in to the [TrendAI Vision One Console](https://portal.xdr.trendmicro.com)
2. Navigate to **Administration** → **API Keys**
3. Click **Add API Key**
4. Configure the API key:
   - **Name:** Microsoft Sentinel Integration (or your preferred name)
   - **Role:** Select a role with the following permissions:
     - Workbench (View)
     - Observed Attack Techniques (View)
   - **Expiration:** Set according to your security policy
5. Click **Add**
6. **Important:** Copy and securely store the API token immediately. It will not be shown again.

### 3. Identify Your API Region

Determine the API domain based on your TrendAI Vision One tenant region:

| Region | API Domain |
|--------|------------|
| US | `api.xdr.trendmicro.com` |
| EU | `api.eu.xdr.trendmicro.com` |
| SG | `api.sg.xdr.trendmicro.com` |
| JP | `api.xdr.trendmicro.co.jp` / `api.jp.xdr.trendmicro.co.jp` |
| AU | `api.au.xdr.trendmicro.com` |
| IN | `api.in.xdr.trendmicro.com` |
| MEA | `api.mea.xdr.trendmicro.com` |
| UK | `api.uk.xdr.trendmicro.com` |
| CA | `api.ca.xdr.trendmicro.com` |
| ZA (South Africa) | `api.za.xdr.trendmicro.com` |

---

## Installation from Content Hub

### Step 1: Navigate to Content Hub

1. Sign in to the [Azure Portal](https://portal.azure.com)
2. Navigate to **Microsoft Sentinel**
3. Select your Sentinel workspace
4. In the left menu, click **Content hub**

### Step 2: Find and Install the Solution

1. In the Content Hub, search for **"TrendAI Vision One"**
2. Click on the **TrendAI Vision One** solution card
3. Click **Install**
4. Review the solution details and click **Create**
5. Configure the deployment:
   - **Subscription:** Select your subscription
   - **Resource Group:** Select the resource group containing your Sentinel workspace
   - **Workspace:** Select your Sentinel workspace
   - **Region:** Select the region matching your workspace
6. Click **Review + Create**
7. Click **Create** to deploy the solution

### Step 3: Verify Installation

1. Navigate to **Microsoft Sentinel** → **Data connectors**
2. Search for **"TrendAI"**
3. You should see two connectors:
   - TrendAI Vision One - Workbench Alerts (via Codeless Connector Framework)
   - TrendAI Vision One - OAT Detections (via Codeless Connector Framework)

---

## Connecting the Data Connectors

### Connect Workbench Alerts Connector

1. Navigate to **Microsoft Sentinel** → **Data connectors**
2. Search for and select **"TrendAI Vision One - Workbench Alerts"**
3. Click **Open connector page**
4. Enter the following parameters:

   | Parameter | Description | Required |
   |-----------|-------------|----------|
   | **API Domain** | The API endpoint for your region (e.g., `api.xdr.trendmicro.com`) | Yes |
   | **API Token** | Your TrendAI Vision One API token | Yes |
   | **TMV1-Filter (Optional)** | OData filter to limit ingested alerts (e.g., `severity ge 'high'`) | No |

5. Click **Connect**
6. Wait for the connector status to show **Connected**

### Connect OAT Detections Connector

1. Navigate to **Microsoft Sentinel** → **Data connectors**
2. Search for and select **"TrendAI Vision One - OAT Detections"**
3. Click **Open connector page**
4. Enter the following parameters:

   | Parameter | Description | Required |
   |-----------|-------------|----------|
   | **API Domain** | The API endpoint for your region (e.g., `api.xdr.trendmicro.com`) | Yes |
   | **API Token** | Your TrendAI Vision One API token | Yes |
   | **TMV1-Filter (Optional)** | OData filter to limit ingested detections (e.g., `riskLevel eq 'high'`) | No |
   | **Exclude Third-Party OAT** | Enter `true` to exclude detections from third-party linked sources, `false` to include all | No |

5. Click **Connect**
6. Wait for the connector status to show **Connected**

---

## Parameter Reference

### Workbench Alerts Connector Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `apiDomain` | String | Yes | - | TrendAI Vision One API domain for your region |
| `apiToken` | SecureString | Yes | - | API token with Workbench view permissions |
| `workbenchFilter` | String | No | (empty) | TMV1-Filter header value for filtering alerts |

**Example Filter Values:**
- `severity eq 'critical'` - Only critical alerts
- `severity ge 'high'` - High and critical alerts
- `investigationStatus eq 'New'` - Only new investigations

### OAT Detections Connector Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `apiDomain` | String | Yes | - | TrendAI Vision One API domain for your region |
| `apiToken` | SecureString | Yes | - | API token with OAT view permissions |
| `oatFilter` | String | No | (empty) | TMV1-Filter header value for filtering detections |
| `excludeThirdPartyOat` | String | No | `false` | Set to `true` to exclude third-party detections (productCode == 'tlc') |

**Example Filter Values:**
- `riskLevel eq 'high'` - Only high-risk detections
- `riskLevel eq 'critical'` - Only critical detections

---

## Data Tables

### TrendAI_XDR_WORKBENCH_V2_CL

Contains Workbench alerts with the following key fields:

| Field | Type | Description |
|-------|------|-------------|
| `TimeGenerated` | datetime | Time the alert was created |
| `workbenchId_s` | string | Unique Workbench alert ID |
| `workbenchName_s` | string | Name/title of the alert |
| `severity_s` | string | Severity level (low, medium, high, critical) |
| `priorityScore_d` | real | Priority score (0-100) |
| `description_s` | string | Alert description |
| `investigationStatus_s` | string | Current investigation status |
| `indicators_s` | string | Associated indicators (IOCs) |
| `impactScope_s` | string | Affected entities summary |
| `workbenchLink_s` | string | Direct link to Vision One console |

### TrendAI_XDR_OAT_V2_CL

Contains OAT detections with the following key fields:

| Field | Type | Description |
|-------|------|-------------|
| `TimeGenerated` | datetime | Time the detection occurred |
| `detail_filterRiskLevel_s` | string | Risk level (low, medium, high, critical) |
| `detail_ruleName_s` | string | Detection rule name |
| `detail_endpointHostName_s` | string | Affected endpoint hostname |
| `detail_processCmd_s` | string | Process command line |
| `detail_processFileHashSha256_s` | string | Process file SHA256 hash |
| `detail_parentCmd_s` | string | Parent process command line |
| `detail_src_s` | string | Source IP address |
| `detail_dst_s` | string | Destination IP address |

---

## Sample Queries

### Workbench Alerts

```kusto
// Get all high and critical severity alerts
TrendAI_XDR_WORKBENCH_V2_CL
| where severity_s in ('high', 'critical')
| project TimeGenerated, workbenchId_s, workbenchName_s, severity_s, priorityScore_d, description_s
| order by TimeGenerated desc
```

```kusto
// Count alerts by severity over time
TrendAI_XDR_WORKBENCH_V2_CL
| summarize Count = count() by severity_s, bin(TimeGenerated, 1h)
| render timechart
```

### OAT Detections

```kusto
// Get high-risk detections with process details
TrendAI_XDR_OAT_V2_CL
| where detail_filterRiskLevel_s == 'high'
| project TimeGenerated, detail_endpointHostName_s, detail_ruleName_s, detail_processCmd_s, detail_processFileHashSha256_s
| order by TimeGenerated desc
```

```kusto
// Top 10 endpoints with most detections
TrendAI_XDR_OAT_V2_CL
| summarize DetectionCount = count() by detail_endpointHostName_s
| top 10 by DetectionCount desc
```

---

## Troubleshooting

### Connector Shows "Disconnected"

1. Verify the API token is valid and not expired
2. Confirm the API domain matches your Vision One tenant region
3. Check that the API token has the required permissions

### No Data Appearing

1. Data ingestion may take up to 10 minutes after initial connection
2. Verify there is activity in your Vision One tenant (Workbench alerts or OAT detections)
3. Check if filters are too restrictive
4. Query the tables directly to verify data:
   ```kusto
   TrendAI_XDR_WORKBENCH_V2_CL | take 10
   TrendAI_XDR_OAT_V2_CL | take 10
   ```

### Authentication Errors

1. Regenerate the API token in Vision One console
2. Ensure no extra spaces when copying the token
3. Verify the token role has appropriate view permissions

---

## Support

For issues and support:

- **Trend Micro Support Portal:** [https://success.trendmicro.com/](https://success.trendmicro.com/)
- **TrendAI Vision One Documentation:** [https://docs.trendmicro.com/en-us/documentation/article/trend-vision-one-documentation](https://docs.trendmicro.com/en-us/documentation/article/trend-vision-one-documentation)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 3.1.1 | 2026-07 | Fixed ARM template bracket escaping, added token rotation warning, optimized workbook queries |
| 3.0.0 | 2026-07 | Initial release with CCF-based connectors, dropdown selectors for API domain and third-party exclusion, TMV1-Filter support, MITRE ATT&CK mappings |

---

## License

This solution is provided under the terms specified in the LICENSE file.
