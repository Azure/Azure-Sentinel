# MimecastAudit

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Mimecast |
| **Support Tier** | Partner |
| **Support Link** | [https://mimecastsupport.zendesk.com/](https://mimecastsupport.zendesk.com/) |
| **Categories** | domains |
| **First Published** | 2022-02-24 |
| **Last Updated** | 2022-02-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastAudit) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Mimecast Audit & Authentication](../connectors/mimecastauditapi.md)

**Publisher:** Mimecast

The data connector for [Mimecast Audit & Authentication](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to audit and authentication events within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into user activity, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.  

The Mimecast products included within the connector are: 

Audit & Authentication

 

| | |
|--------------------------|---|
| **Tables Ingested** | `MimecastAudit_CL` |
| **Connector Definition Files** | [MimecastAudit_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastAudit/Data%20Connectors/MimecastAudit_API_AzureFunctionApp.json) |

[→ View full connector details](../connectors/mimecastauditapi.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MimecastAudit_CL` | [Mimecast Audit & Authentication](../connectors/mimecastauditapi.md) |

[← Back to Solutions Index](../solutions-index.md)
