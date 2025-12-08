# MimecastSEG

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Mimecast |
| **Support Tier** | Partner |
| **Support Link** | [https://mimecastsupport.zendesk.com/](https://mimecastsupport.zendesk.com/) |
| **Categories** | domains |
| **First Published** | 2022-02-24 |
| **Last Updated** | 2022-02-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Mimecast Secure Email Gateway](../connectors/mimecastsiemapi.md)

**Publisher:** Mimecast

The data connector for [Mimecast Secure Email Gateway](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) allows easy log collection from the Secure Email Gateway to surface email insight and user activity within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities. Mimecast products and features required: 

- Mimecast Secure Email Gateway 

- Mimecast Data Leak Prevention

 

| | |
|--------------------------|---|
| **Tables Ingested** | `MimecastDLP_CL` |
| | `MimecastSIEM_CL` |
| **Connector Definition Files** | [MimecastSEG_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG/Data%20Connectors/MimecastSEG_API_AzureFunctionApp.json) |

[→ View full connector details](../connectors/mimecastsiemapi.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MimecastDLP_CL` | [Mimecast Secure Email Gateway](../connectors/mimecastsiemapi.md) |
| `MimecastSIEM_CL` | [Mimecast Secure Email Gateway](../connectors/mimecastsiemapi.md) |

[← Back to Solutions Index](../solutions-index.md)
