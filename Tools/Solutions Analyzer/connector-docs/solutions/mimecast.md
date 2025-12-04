# Mimecast

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Mimecast |
| **Support Tier** | Partner |
| **Support Link** | [https://mimecastsupport.zendesk.com/](https://mimecastsupport.zendesk.com/) |
| **Categories** | domains |
| **First Published** | 2024-09-10 |
| **Last Updated** | 2024-09-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast) |

## Data Connectors

This solution provides **5 data connector(s)**.

### [Mimecast Awareness Training](../connectors/mimecastatapi.md)

**Publisher:** Mimecast

### [Mimecast Audit](../connectors/mimecastauditapi.md)

**Publisher:** Mimecast

### [Mimecast Cloud Integrated](../connectors/mimecastciapi.md)

**Publisher:** Mimecast

### [Mimecast Secure Email Gateway](../connectors/mimecastsegapi.md)

**Publisher:** Mimecast

### [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md)

**Publisher:** Mimecast

The data connector for [Mimecast Targeted Threat Protection](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to the Targeted Threat Protection inspection technologies within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.  

The Mimecast products included within the connector are: 

- URL Protect 

- Impersonation Protect 

- Attachment Protect



| | |
|--------------------------|---|
| **Tables Ingested** | `Ttp_Attachment_CL` |
| | `Ttp_Impersonation_CL` |
| | `Ttp_Url_CL` |
| **Connector Definition Files** | [Mimecast_TTP_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Data%20Connectors/MimecastTTP/Mimecast_TTP_FunctionApp.json) |

[→ View full connector details](../connectors/mimecastttpapi.md)

## Tables Reference

This solution ingests data into **11 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Audit_CL` | [Mimecast Audit](../connectors/mimecastauditapi.md) |
| `Awareness_Performance_Details_CL` | [Mimecast Awareness Training](../connectors/mimecastatapi.md) |
| `Awareness_SafeScore_Details_CL` | [Mimecast Awareness Training](../connectors/mimecastatapi.md) |
| `Awareness_User_Data_CL` | [Mimecast Awareness Training](../connectors/mimecastatapi.md) |
| `Awareness_Watchlist_Details_CL` | [Mimecast Awareness Training](../connectors/mimecastatapi.md) |
| `Cloud_Integrated_CL` | [Mimecast Cloud Integrated](../connectors/mimecastciapi.md) |
| `Seg_Cg_CL` | [Mimecast Secure Email Gateway](../connectors/mimecastsegapi.md) |
| `Seg_Dlp_CL` | [Mimecast Secure Email Gateway](../connectors/mimecastsegapi.md) |
| `Ttp_Attachment_CL` | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) |
| `Ttp_Impersonation_CL` | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) |
| `Ttp_Url_CL` | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) |

[← Back to Solutions Index](../solutions-index.md)
