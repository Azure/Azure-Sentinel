# MimecastTTP

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Mimecast |
| **Support Tier** | Partner |
| **Support Link** | [https://mimecastsupport.zendesk.com/](https://mimecastsupport.zendesk.com/) |
| **Categories** | domains |
| **First Published** | 2022-02-24 |
| **Last Updated** | 2022-02-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTTP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTTP) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md)

**Publisher:** Mimecast

The data connector for [Mimecast Targeted Threat Protection](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to the Targeted Threat Protection inspection technologies within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.  

The Mimecast products included within the connector are: 

- URL Protect 

- Impersonation Protect 

- Attachment Protect



| | |
|--------------------------|---|
| **Tables Ingested** | `MimecastTTPAttachment_CL` |
| | `MimecastTTPImpersonation_CL` |
| | `MimecastTTPUrl_CL` |
| **Connector Definition Files** | [MimecastTTP_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTTP/Data%20Connectors/MimecastTTP_API_FunctionApp.json) |

[→ View full connector details](../connectors/mimecastttpapi.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MimecastTTPAttachment_CL` | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) |
| `MimecastTTPImpersonation_CL` | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) |
| `MimecastTTPUrl_CL` | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) |

[← Back to Solutions Index](../solutions-index.md)
