# Mimecast Targeted Threat Protection

| | |
|----------|-------|
| **Connector ID** | `MimecastTTPAPI` |
| **Publisher** | Mimecast |
| **Tables Ingested** | [`MimecastTTPAttachment_CL`](../tables-index.md#mimecastttpattachment_cl), [`MimecastTTPImpersonation_CL`](../tables-index.md#mimecastttpimpersonation_cl), [`MimecastTTPUrl_CL`](../tables-index.md#mimecastttpurl_cl), [`Ttp_Attachment_CL`](../tables-index.md#ttp_attachment_cl), [`Ttp_Impersonation_CL`](../tables-index.md#ttp_impersonation_cl), [`Ttp_Url_CL`](../tables-index.md#ttp_url_cl) |
| **Used in Solutions** | [Mimecast](../solutions/mimecast.md), [MimecastTTP](../solutions/mimecastttp.md) |
| **Connector Definition Files** | [Mimecast_TTP_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Data%20Connectors/MimecastTTP/Mimecast_TTP_FunctionApp.json) |

The data connector for [Mimecast Targeted Threat Protection](https://integrations.mimecast.com/tech-partners/microsoft-sentinel/) provides customers with the visibility into security events related to the Targeted Threat Protection inspection technologies within Microsoft Sentinel. The data connector provides pre-created dashboards to allow analysts to view insight into email based threats, aid in incident correlation and reduce investigation response times coupled with custom alert capabilities.  

The Mimecast products included within the connector are: 

- URL Protect 

- Impersonation Protect 

- Attachment Protect



[← Back to Connectors Index](../connectors-index.md)
