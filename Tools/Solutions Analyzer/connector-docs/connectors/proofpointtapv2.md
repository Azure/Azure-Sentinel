# Proofpoint TAP (via Codeless Connector Platform)

| | |
|----------|-------|
| **Connector ID** | `ProofpointTAPv2` |
| **Publisher** | Proofpoint |
| **Tables Ingested** | [`ProofPointTAPClicksBlockedV2_CL`](../tables-index.md#proofpointtapclicksblockedv2_cl), [`ProofPointTAPClicksPermittedV2_CL`](../tables-index.md#proofpointtapclickspermittedv2_cl), [`ProofPointTAPMessagesBlockedV2_CL`](../tables-index.md#proofpointtapmessagesblockedv2_cl), [`ProofPointTAPMessagesDeliveredV2_CL`](../tables-index.md#proofpointtapmessagesdeliveredv2_cl) |
| **Used in Solutions** | [ProofPointTap](../solutions/proofpointtap.md) |
| **Connector Definition Files** | [ProofpointTAP_defination.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap/Data%20Connectors/ProofpointTAP_CCP/ProofpointTAP_defination.json) |

The [Proofpoint Targeted Attack Protection (TAP)](https://www.proofpoint.com/us/products/advanced-threat-protection/targeted-attack-protection) connector provides the capability to ingest Proofpoint TAP logs and events into Microsoft Sentinel. The connector provides visibility into Message and Click events in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.

**Custom Permissions:**
- **Proofpoint TAP API Key**: A Proofpoint TAP API service principal and secret is required to access Proofpoint's SIEM API. [See the documentation to learn more about Proofpoint SIEM API](https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/SIEM_API).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**Configuration steps for the Proofpoint TAP API**

1. Log into the [Proofpoint TAP dashboard](https://threatinsight.proofpoint.com/) 
2. Navigate to **Settings** and go to **Connected Applications** tab 
 3. Click on **Create New Credential** 
 4. Provide a name and click **Generate** 
 5. Copy **Service Principal** and **Secret** values

>**NOTE:** This connector depends on a parser based on Kusto Function to work as expected [**ProofpointTAPEvent**](https://aka.ms/sentinel-ProofpointTAPDataConnector-parser) which is deployed with the Microsoft Sentinel Solution.

- **Service Principal**: 123456
- **Secret**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
