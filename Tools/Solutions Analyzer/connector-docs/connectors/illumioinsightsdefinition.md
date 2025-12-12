# Illumio Insights

| | |
|----------|-------|
| **Connector ID** | `IllumioInsightsDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`IllumioInsights_CL`](../tables-index.md#illumioinsights_cl) |
| **Used in Solutions** | [Illumio Insight](../solutions/illumio-insight.md) |
| **Connector Definition Files** | [IllumioInsight_Definition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illumio%20Insight/Data%20Connectors/IllumioInsight_CCP/IllumioInsight_Definition.json) |

Illumio Insights Connector sends workload and security graph data from Illumio Insights into the Azure Microsoft Sentinel Data Lake, providing deep context for threat detection, lateral movement analysis, and real-time investigation.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### Configuration steps for the Illumio Insights Connector

**Prerequisites**
- Register and Login to Illumio Console with valid credentials
- Purchase Illumio Insights or Start a free Trial for Illumio Insights

**Step 1: Register the Service Account**
1. Go to **Illumio Console → Access → Service Accounts**
2. Create a service account for the tenant
3. Once you create a service account, you will receive the client credentials
4. Copy the **auth_username** (Illumio Insights API Key) and the **Secret** (API Secret)

**Step 2: Add Client Credentials to Sentinel Account**
- Add the API key and secret to Sentinel Account for tenant authentication
- These credentials will be used to authenticate calls to the Illumio SaaS API

Please fill in the required fields below with the credentials obtained from the Illumio Console:
- **Illumio Insights Api Key**: (password field)
- **Api Secret**: (password field)
- **Illumio Tenant Id**: {IllumioTenantId - Optional}
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
