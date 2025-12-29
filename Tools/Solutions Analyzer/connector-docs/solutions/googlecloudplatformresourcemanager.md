# GoogleCloudPlatformResourceManager

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2025-03-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformResourceManager](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformResourceManager) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Google Cloud Platform Resource Manager (via Codeless Connector Framework)](../connectors/gcpresourcemanagerlogsccfdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform Resource Manager data connector provides the capability to ingest Resource Manager [Admin Activity and Data Access Audit logs](https://cloud.google.com/resource-manager/docs/audit-logging) into Microsoft Sentinel using the Cloud Resource Manager API. Refer the [Product overview](https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy) document for more details.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `GCPResourceManager` |
| **Connector Definition Files** | [GCPResourceManagerAuditLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformResourceManager/Data%20Connectors/GCPResourceManagerAuditLogs_ccf/GCPResourceManagerAuditLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpresourcemanagerlogsccfdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPResourceManager` | [Google Cloud Platform Resource Manager (via Codeless Connector Framework)](../connectors/gcpresourcemanagerlogsccfdefinition.md) |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.1      | 02-09-2025                    | GCP Resource Manager **CCF Conector** moving to GA                                        |
| 3.0.0      | 18-06-2025                    | Initial Solution Release.                                               |

[← Back to Solutions Index](../solutions-index.md)
