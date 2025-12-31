# Oracle Cloud Infrastructure

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Oracle Cloud Infrastructure (via Codeless Connector Framework)](../connectors/oci-connector-ccp-definition.md)
- [[DEPRECATED] Oracle Cloud Infrastructure](../connectors/oraclecloudinfrastructurelogsconnector.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md) | [Oracle Cloud Infrastructure (via Codeless Connector Framework)](../connectors/oci-connector-ccp-definition.md) | Analytics, Hunting, Workbooks |
| [`OCI_Logs_CL`](../tables/oci-logs-cl.md) | [[DEPRECATED] Oracle Cloud Infrastructure](../connectors/oraclecloudinfrastructurelogsconnector.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **22 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [OCI - Discovery activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Analytic%20Rules/OCIDiscoveryActivity.yaml) | Medium | Discovery | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Event rule deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Analytic%20Rules/OCIEventRuleDeleted.yaml) | High | DefenseEvasion | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Inbound SSH connection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Analytic%20Rules/OCIInboundSSHConnection.yaml) | Medium | InitialAccess | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Insecure metadata endpoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Analytic%20Rules/OCIInsecureMetadataEndpoint.yaml) | High | Discovery | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Instance metadata access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Analytic%20Rules/OCIMetadataEndpointIpAccess.yaml) | Medium | Discovery | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Multiple instances launched](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Analytic%20Rules/OCIMultipleInstancesLaunched.yaml) | Medium | Impact | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Multiple instances terminated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Analytic%20Rules/OCIMultipleInstancesTerminated.yaml) | High | Impact | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Multiple rejects on rare ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Analytic%20Rules/OCIMultipleRejects.yaml) | Medium | Reconnaissance | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - SSH scanner](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Analytic%20Rules/OCISSHScan.yaml) | High | Reconnaissance | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Unexpected user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Analytic%20Rules/OCIUnexpectedUserAgent.yaml) | Medium | InitialAccess | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [OCI - Delete operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Hunting%20Queries/OCIUserDeleteActions.yaml) | Impact | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Deleted users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Hunting%20Queries/OCIUserDeletedUsers.yaml) | Impact | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Destination ports (inbound traffic)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Hunting%20Queries/OCIDestinationsIn.yaml) | InitialAccess | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Destination ports (outbound traffic)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Hunting%20Queries/OCIDestinationsOut.yaml) | Exfiltration | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Launched instances](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Hunting%20Queries/OCILaunchedInstances.yaml) | Impact | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - New users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Hunting%20Queries/OCIUserNewUsers.yaml) | InitialAccess, Persistence | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Terminated instances](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Hunting%20Queries/OCIUserTerminatedInstances.yaml) | Impact | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Update activities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Hunting%20Queries/OCIUpdateActivities.yaml) | Impact | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - Updated instances](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Hunting%20Queries/OCIUserUpdatedInstances.yaml) | DefenseEvasion | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |
| [OCI - User source IP addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Hunting%20Queries/OCIUserSources.yaml) | Impact | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [OracleCloudInfrastructureOCI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Workbooks/OracleCloudInfrastructureOCI.json) | [`OCI_LogsV2_CL`](../tables/oci-logsv2-cl.md)<br>[`OCI_Logs_CL`](../tables/oci-logs-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [OCILogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Parsers/OCILogs.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                          |
|-------------|--------------------------------|-----------------------------------------------------------------------------|
| 3.0.6       | 09-12-2025                     | Support Multistream + multi partition.       |
| 3.0.5       | 13-11-2025                     | Updated partition id text box's description with zero-based indexing.       |
| 3.0.4       | 22-09-2025                     | Updated the OCI **CCF Data Connector** instructions to include information about the partition ID limitation.		 							 |
| 3.0.3       | 25-08-2025                     | Moving OCI **CCF Data Connector** to GA		 							 |
| 3.0.2       | 14-07-2025                     | Introduced new **CCF Connector** to the Solution - "OCI-Connector-CCP-Definition".|
| 3.0.1       | 05-10-2023                     | Manual deployment instructions updated for **Data Connector**.               |
| 3.0.0       | 21-08-2023                     | Modified the **Parser** by adding Columnifexists condition to avoid errors. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
