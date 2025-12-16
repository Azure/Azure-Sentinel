# ProofPointTap

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Proofpoint, Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://proofpoint.my.site.com/community/s/](https://proofpoint.my.site.com/community/s/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Proofpoint TAP](../connectors/proofpointtap.md)

**Publisher:** Proofpoint

### [Proofpoint TAP (via Codeless Connector Platform)](../connectors/proofpointtapv2.md)

**Publisher:** Proofpoint

The [Proofpoint Targeted Attack Protection (TAP)](https://www.proofpoint.com/us/products/advanced-threat-protection/targeted-attack-protection) connector provides the capability to ingest Proofpoint TAP logs and events into Microsoft Sentinel. The connector provides visibility into Message and Click events in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.

**Custom Permissions:**
- **Proofpoint TAP API Key**: A Proofpoint TAP API service principal and secret is required to access Proofpoint's SIEM API. [See the documentation to learn more about Proofpoint SIEM API](https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/SIEM_API).

**Setup Instructions:**

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

| | |
|--------------------------|---|
| **Tables Ingested** | `ProofPointTAPClicksBlockedV2_CL` |
| | `ProofPointTAPClicksPermittedV2_CL` |
| | `ProofPointTAPMessagesBlockedV2_CL` |
| | `ProofPointTAPMessagesDeliveredV2_CL` |
| **Connector Definition Files** | [ProofpointTAP_defination.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap/Data%20Connectors/ProofpointTAP_CCP/ProofpointTAP_defination.json) |

[→ View full connector details](../connectors/proofpointtapv2.md)

## Tables Reference

This solution ingests data into **8 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ProofPointTAPClicksBlockedV2_CL` | [Proofpoint TAP (via Codeless Connector Platform)](../connectors/proofpointtapv2.md) |
| `ProofPointTAPClicksBlocked_CL` | [[Deprecated] Proofpoint TAP](../connectors/proofpointtap.md) |
| `ProofPointTAPClicksPermittedV2_CL` | [Proofpoint TAP (via Codeless Connector Platform)](../connectors/proofpointtapv2.md) |
| `ProofPointTAPClicksPermitted_CL` | [[Deprecated] Proofpoint TAP](../connectors/proofpointtap.md) |
| `ProofPointTAPMessagesBlockedV2_CL` | [Proofpoint TAP (via Codeless Connector Platform)](../connectors/proofpointtapv2.md) |
| `ProofPointTAPMessagesBlocked_CL` | [[Deprecated] Proofpoint TAP](../connectors/proofpointtap.md) |
| `ProofPointTAPMessagesDeliveredV2_CL` | [Proofpoint TAP (via Codeless Connector Platform)](../connectors/proofpointtapv2.md) |
| `ProofPointTAPMessagesDelivered_CL` | [[Deprecated] Proofpoint TAP](../connectors/proofpointtap.md) |

[← Back to Solutions Index](../solutions-index.md)
