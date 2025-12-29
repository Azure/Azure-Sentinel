# Google Cloud Platform Audit Logs

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-03-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Audit%20Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Audit%20Logs) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [GCP Pub/Sub Audit Logs](../connectors/gcpauditlogsdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform (GCP) audit logs, ingested from Microsoft Sentinel's connector, enables you to capture three types of audit logs: admin activity logs, data access logs, and access transparency logs. Google cloud audit logs record a trail that practitioners can use to monitor access and detect potential threats across Google Cloud Platform (GCP) resources.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `GCPAuditLogs` |
| **Connector Definition Files** | [data_connector_definition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Audit%20Logs/Data%20Connectors/GCPAuditLogs_ccp/data_connector_definition.json) |

[→ View full connector details](../connectors/gcpauditlogsdefinition.md)

### [GCP Pub/Sub Audit Logs](../connectors/gcppub-subauditlogs.md)

**Publisher:** Microsoft

The Google Cloud Platform (GCP) audit logs, ingested from Sentinel's connector, enable you to capture three types of audit logs: admin activity logs, data access logs, and access transparency logs. Google cloud audit logs record a trail that practitioners can use to monitor access and detect potential threats across Google Cloud Platform (GCP) resources.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `GCPAuditLogs` |
| **Connector Definition Files** | [GCPAuditLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Audit%20Logs/Data%20Connectors/GCPAuditLogs.json) |

[→ View full connector details](../connectors/gcppub-subauditlogs.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPAuditLogs` | [GCP Pub/Sub Audit Logs](../connectors/gcppub-subauditlogs.md), [GCP Pub/Sub Audit Logs](../connectors/gcpauditlogsdefinition.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------| 
| 3.0.1       | 28-04-2025                     | Updated **Data Connector** definition file and fixed overlapping collector issue.|
| 3.0.0       | 15-01-2024                     |	Created CCP Package   |

[← Back to Solutions Index](../solutions-index.md)
