# Mimecast

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

The data connector for [Mimecast Awareness Training](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to the Targeted Threat Protection inspection technologies within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.  

The Mimecast products included within the connector are: 

- Performance Details 

- Safe Score Details 

- User Data

- Watchlist Details



| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Awareness_Performance_Details_CL` |
| | `Awareness_SafeScore_Details_CL` |
| | `Awareness_User_Data_CL` |
| | `Awareness_Watchlist_Details_CL` |
| **Connector Definition Files** | [Mimecast_AT_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Data%20Connectors/MimecastAT/Mimecast_AT_FunctionApp.json) |

[→ View full connector details](../connectors/mimecastatapi.md)

### [Mimecast Audit](../connectors/mimecastauditapi.md)

**Publisher:** Mimecast

The data connector for [Mimecast Audit](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to audit and authentication events within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into user activity, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.  

The Mimecast products included within the connector are: 

Audit

 

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Audit_CL` |
| **Connector Definition Files** | [Mimecast_Audit_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Data%20Connectors/MimecastAudit/Mimecast_Audit_FunctionApp.json) |

[→ View full connector details](../connectors/mimecastauditapi.md)

### [Mimecast Cloud Integrated](../connectors/mimecastciapi.md)

**Publisher:** Mimecast

The data connector for [Mimecast Cloud Integrated](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to the Cloud Integrated inspection technologies within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Cloud_Integrated_CL` |
| **Connector Definition Files** | [Mimecast_Cloud_Integrated_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Data%20Connectors/MimecastCloudIntegrated/Mimecast_Cloud_Integrated_FunctionApp.json) |

[→ View full connector details](../connectors/mimecastciapi.md)

### [Mimecast Secure Email Gateway](../connectors/mimecastsegapi.md)

**Publisher:** Mimecast

The data connector for [Mimecast Secure Email Gateway](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) allows easy log collection from the Secure Email Gateway to surface email insight and user activity within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities. Mimecast products and features required: 

- Mimecast Cloud Gateway 

- Mimecast Data Leak Prevention

 

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Seg_Cg_CL` |
| | `Seg_Dlp_CL` |
| **Connector Definition Files** | [Mimecast_SEG_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Data%20Connectors/MimecastSEG/Mimecast_SEG_FunctionApp.json) |

[→ View full connector details](../connectors/mimecastsegapi.md)

### [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md)

**Publisher:** Mimecast

The data connector for [Mimecast Targeted Threat Protection](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to the Targeted Threat Protection inspection technologies within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.  

The Mimecast products included within the connector are: 

- URL Protect 

- Impersonation Protect 

- Attachment Protect



| Attribute | Value |
|:-------------------------|:---|
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
