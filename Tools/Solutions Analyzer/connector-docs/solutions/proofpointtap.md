# ProofPointTap

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

The [Proofpoint Targeted Attack Protection (TAP)](https://www.proofpoint.com/us/products/advanced-threat-protection/targeted-attack-protection) connector provides the capability to ingest Proofpoint TAP logs and events into Microsoft Sentinel. The connector provides visibility into Message and Click events in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ProofPointTAPClicksBlocked_CL` |
| | `ProofPointTAPClicksPermitted_CL` |
| | `ProofPointTAPMessagesBlocked_CL` |
| | `ProofPointTAPMessagesDelivered_CL` |
| **Connector Definition Files** | [ProofpointTAP_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ProofPointTap/Data%20Connectors/ProofpointTAP_API_FunctionApp.json) |

[→ View full connector details](../connectors/proofpointtap.md)

### [Proofpoint TAP (via Codeless Connector Platform)](../connectors/proofpointtapv2.md)

**Publisher:** Proofpoint

The [Proofpoint Targeted Attack Protection (TAP)](https://www.proofpoint.com/us/products/advanced-threat-protection/targeted-attack-protection) connector provides the capability to ingest Proofpoint TAP logs and events into Microsoft Sentinel. The connector provides visibility into Message and Click events in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

| Attribute | Value |
|:-------------------------|:---|
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

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                           |
|-------------|--------------------------------|--------------------------------------------------------------|
| 3.1.1       | 03-11-2025                     | Update support url in **SolutionMetadata.json**.|  
| 3.1.0       | 31-07-2025                     | Updated Support details and publisherId in **SolutionMetadata.json**, updated Author details and Logo in **Solution_ProofTap.json** from Microsoft to Proofpoint.|
| 3.0.10      | 28-07-2025                     | Removed Deprecated **Data Connector**.							|  
| 3.0.9       | 20-06-2025                     | Expanded the query for *ProofpointTAPEvent* **Parser** to include additional columns and data sources (V2).               |
| 3.0.8       | 06-05-2025                     | Launching CCP **Data Connector** *Proofpoint TAP (via Codeless Connector Platform)* from Public Preview to Global Availability.           |
| 3.0.7       | 21-04-2025                     | Correction in **CCP Connector** DCR File to resolve deployment issue. | 
| 3.0.6       | 04-04-2025                     | New **CCP Connector** added *Proofpoint TAP (via Codeless Connector Platform)*.  		  | 
| 3.0.5       | 12-01-2025                     | Updated **Analytic Rule** MalwareLinkClicked.yaml.  		  | 
| 3.0.4       | 26-04-2024                     | Repackaged for fix on parser in maintemplate to have old parsername and parentid.        |
| 3.0.3       | 16-04-2024                     | Repackaged for parser issue in maintemplate.  				  |
| 3.0.2       | 10-04-2024                     | Added Azure Deploy button for government portal deployments.  |
| 3.0.1       | 10-10-2023                     | Manual deployment instructions updated for **Data Connector**.|          
| 3.0.0       | 01-08-2023                     | Updated solution logo with Microsoft Sentinel logo.           |

[← Back to Solutions Index](../solutions-index.md)
