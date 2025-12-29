# Proofpoint On demand(POD) Email Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Proofpoint, Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://proofpoint.my.site.com/community/s/](https://proofpoint.my.site.com/community/s/) |
| **Categories** | domains |
| **First Published** | 2021-03-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md)

**Publisher:** Proofpoint

Proofpoint On Demand Email Security data connector provides the capability to get Proofpoint on Demand Email Protection data, allows users to check message traceability, monitoring into email activity, threats,and data exfiltration by attackers and malicious insiders. The connector provides ability to review events in your org on an accelerated basis, get event log files in hourly increments for recent activity.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ProofpointPODMailLog_CL` |
| | `ProofpointPODMessage_CL` |
| **Connector Definition Files** | [ProofpointPOD_Definaton.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Data%20Connectors/ProofPointEmailSecurity_CCP/ProofpointPOD_Definaton.json) |

[→ View full connector details](../connectors/proofpointccpdefinition.md)

### [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md)

**Publisher:** Proofpoint

Proofpoint On Demand Email Security data connector provides the capability to get Proofpoint on Demand Email Protection data, allows users to check message traceability, monitoring into email activity, threats,and data exfiltration by attackers and malicious insiders. The connector provides ability to review events in your org on an accelerated basis, get event log files in hourly increments for recent activity.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ProofpointPODMessage_CL` |
| | `ProofpointPOD_maillog_CL` |
| | `ProofpointPOD_message_CL` |
| | `maillog_CL` |
| **Connector Definition Files** | [ProofpointPOD_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Data%20Connectors/ProofpointPOD_API_FunctionApp.json) |

[→ View full connector details](../connectors/proofpointpod.md)

## Tables Reference

This solution ingests data into **5 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ProofpointPODMailLog_CL` | [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md) |
| `ProofpointPODMessage_CL` | [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md), [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |
| `ProofpointPOD_maillog_CL` | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |
| `ProofpointPOD_message_CL` | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |
| `maillog_CL` | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                   |
|-------------|--------------------------------|------------------------------------------------------|
| 3.1.2       | 08-12-2025                     | Update **ProofpointPOD_PollingConfig.json** to remove start and end time query params, it impacts time frames at server side and causes duplicate data ingestion.|  
| 3.1.1       | 03-11-2025                     | Update support url in **SolutionMetadata.json**.|  
| 3.1.0       | 31-07-2025                     | Updated Support details and publisherId in **SolutionMetadata.json**, updated Author details and Logo in **Solution_ProofPointPOD.json** from Microsoft to Proofpoint.|
| 3.0.5       | 28-07-2025                     | Removed Deprecated **Data Connector**.							|  
| 3.0.4       | 06-05-2025                     | Launching CCP **Data Connector** - *Proofpoint On Demand Email Security* from Public Preview to Global Availability.           |
| 3.0.3       | 12-03-2025                     | Added new CCP **Data Connector** - *Proofpoint On Demand Email Security*.            |
| 3.0.2       | 06-09-2024                     | Updated the python runtime version to 3.11 in **Data Connector** Function App.           |
| 3.0.1       | 02-05-2024                     | Optimized **Parser**.                                      |
| 3.0.0       | 01-08-2023                     | Updated solution logo with Microsoft Sentinel logo.   |

[← Back to Solutions Index](../solutions-index.md)
