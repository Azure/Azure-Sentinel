# Google Cloud Platform Audit Logs

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-03-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Audit%20Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Audit%20Logs) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [GCP Pub/Sub Audit Logs](../connectors/gcpauditlogsdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform (GCP) audit logs, ingested from Microsoft Sentinel's connector, enables you to capture three types of audit logs: admin activity logs, data access logs, and access transparency logs. Google cloud audit logs record a trail that practitioners can use to monitor access and detect potential threats across Google Cloud Platform (GCP) resources.

| | |
|--------------------------|---|
| **Tables Ingested** | `GCPAuditLogs` |
| **Connector Definition Files** | [data_connector_definition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Audit%20Logs/Data%20Connectors/GCPAuditLogs_ccp/data_connector_definition.json) |

[→ View full connector details](../connectors/gcpauditlogsdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPAuditLogs` | [GCP Pub/Sub Audit Logs](../connectors/gcpauditlogsdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
