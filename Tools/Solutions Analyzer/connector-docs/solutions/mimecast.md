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

This solution provides **5 data connector(s)**:

- [Mimecast Awareness Training](../connectors/mimecastatapi.md)
- [Mimecast Audit](../connectors/mimecastauditapi.md)
- [Mimecast Cloud Integrated](../connectors/mimecastciapi.md)
- [Mimecast Secure Email Gateway](../connectors/mimecastsegapi.md)
- [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md)

## Tables Reference

This solution uses **11 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Audit_CL`](../tables/audit-cl.md) | [Mimecast Audit](../connectors/mimecastauditapi.md) | Analytics, Workbooks |
| [`Awareness_Performance_Details_CL`](../tables/awareness-performance-details-cl.md) | [Mimecast Awareness Training](../connectors/mimecastatapi.md) | - |
| [`Awareness_SafeScore_Details_CL`](../tables/awareness-safescore-details-cl.md) | [Mimecast Awareness Training](../connectors/mimecastatapi.md) | Workbooks |
| [`Awareness_User_Data_CL`](../tables/awareness-user-data-cl.md) | [Mimecast Awareness Training](../connectors/mimecastatapi.md) | Workbooks |
| [`Awareness_Watchlist_Details_CL`](../tables/awareness-watchlist-details-cl.md) | [Mimecast Awareness Training](../connectors/mimecastatapi.md) | Workbooks |
| [`Cloud_Integrated_CL`](../tables/cloud-integrated-cl.md) | [Mimecast Cloud Integrated](../connectors/mimecastciapi.md) | Workbooks |
| [`Seg_Cg_CL`](../tables/seg-cg-cl.md) | [Mimecast Secure Email Gateway](../connectors/mimecastsegapi.md) | Analytics, Workbooks |
| [`Seg_Dlp_CL`](../tables/seg-dlp-cl.md) | [Mimecast Secure Email Gateway](../connectors/mimecastsegapi.md) | Analytics, Workbooks |
| [`Ttp_Attachment_CL`](../tables/ttp-attachment-cl.md) | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) | Analytics, Workbooks |
| [`Ttp_Impersonation_CL`](../tables/ttp-impersonation-cl.md) | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) | Analytics, Workbooks |
| [`Ttp_Url_CL`](../tables/ttp-url-cl.md) | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) | Analytics, Workbooks |

## Content Items

This solution includes **30 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 13 |
| Parsers | 11 |
| Workbooks | 5 |
| Playbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Mimecast Audit - Logon Authentication Failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastAudit/Mimecast_Audit.yaml) | High | Discovery, InitialAccess, CredentialAccess | [`Audit_CL`](../tables/audit-cl.md) |
| [Mimecast Data Leak Prevention - Hold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastSEG/MimecastDLP_hold.yaml) | Informational | Exfiltration | [`Seg_Dlp_CL`](../tables/seg-dlp-cl.md) |
| [Mimecast Data Leak Prevention - Notifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastSEG/MimecastDLP_Notifications.yaml) | High | Exfiltration | [`Seg_Dlp_CL`](../tables/seg-dlp-cl.md) |
| [Mimecast Secure Email Gateway - AV](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastSEG/MimecastCG_AV.yaml) | Informational | Execution | [`Seg_Cg_CL`](../tables/seg-cg-cl.md) |
| [Mimecast Secure Email Gateway - Attachment Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastSEG/MimecastCG_Attachment.yaml) | High | Collection, Exfiltration, Discovery, InitialAccess, Execution | [`Seg_Cg_CL`](../tables/seg-cg-cl.md) |
| [Mimecast Secure Email Gateway - Impersonation Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastSEG/MimecastCG_Impersonation.yaml) | High | Discovery, LateralMovement, Collection | [`Seg_Cg_CL`](../tables/seg-cg-cl.md) |
| [Mimecast Secure Email Gateway - Internal Email Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastSEG/MimecastCG_Internal_Mail_Protect.yaml) | High | LateralMovement, Persistence, Exfiltration | [`Seg_Cg_CL`](../tables/seg-cg-cl.md) |
| [Mimecast Secure Email Gateway - Spam Event Thread](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastSEG/MimecastCG_Spam_Event.yaml) | Low | Discovery | [`Seg_Cg_CL`](../tables/seg-cg-cl.md) |
| [Mimecast Secure Email Gateway - URL Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastSEG/MimecastCG_Url_Protect.yaml) | High | InitialAccess, Discovery, Execution | [`Seg_Cg_CL`](../tables/seg-cg-cl.md) |
| [Mimecast Secure Email Gateway - Virus](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastSEG/MimecastCG_Virus.yaml) | Informational | Execution | [`Seg_Cg_CL`](../tables/seg-cg-cl.md) |
| [Mimecast Targeted Threat Protection - Attachment Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastTTP/Mimecast_TTP_Attachment.yaml) | High | InitialAccess, Discovery | [`Ttp_Attachment_CL`](../tables/ttp-attachment-cl.md) |
| [Mimecast Targeted Threat Protection - Impersonation Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastTTP/Mimecast_TTP_Impersonation.yaml) | High | Exfiltration, Collection, Discovery | [`Ttp_Impersonation_CL`](../tables/ttp-impersonation-cl.md) |
| [Mimecast Targeted Threat Protection - URL Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Analytic%20Rules/MimecastTTP/Mimecast_TTP_Url.yaml) | High | InitialAccess, Discovery | [`Ttp_Url_CL`](../tables/ttp-url-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Mimecast_Audit_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Workbooks/Mimecast_Audit_Workbook.json) | [`Audit_CL`](../tables/audit-cl.md) |
| [Mimecast_Awareness_Training_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Workbooks/Mimecast_Awareness_Training_Workbook.json) | [`Awareness_SafeScore_Details_CL`](../tables/awareness-safescore-details-cl.md)<br>[`Awareness_User_Data_CL`](../tables/awareness-user-data-cl.md)<br>[`Awareness_Watchlist_Details_CL`](../tables/awareness-watchlist-details-cl.md) |
| [Mimecast_Cloud_Integrated_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Workbooks/Mimecast_Cloud_Integrated_Workbook.json) | [`Cloud_Integrated_CL`](../tables/cloud-integrated-cl.md) |
| [Mimecast_SEG_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Workbooks/Mimecast_SEG_Workbook.json) | [`Seg_Cg_CL`](../tables/seg-cg-cl.md)<br>[`Seg_Dlp_CL`](../tables/seg-dlp-cl.md) |
| [Mimecast_TTP_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Workbooks/Mimecast_TTP_Workbook.json) | [`Ttp_Attachment_CL`](../tables/ttp-attachment-cl.md)<br>[`Ttp_Impersonation_CL`](../tables/ttp-impersonation-cl.md)<br>[`Ttp_Url_CL`](../tables/ttp-url-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Mimecast-Data-Connector-Trigger-Sync](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Playbooks/Mimecast%20Data%20Connector%20Trigger%20Sync/azuredeploy.json) | Playbook to sync timer trigger of all Mimecast data connectors. | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Mimecast_AT_Performane_Detail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Parsers/MimecastAT/Mimecast_AT_Performane_Detail.yaml) | - | - |
| [Mimecast_AT_Safe_Score](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Parsers/MimecastAT/Mimecast_AT_Safe_Score.yaml) | - | - |
| [Mimecast_AT_User_Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Parsers/MimecastAT/Mimecast_AT_User_Data.yaml) | - | - |
| [Mimecast_AT_Watchlist](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Parsers/MimecastAT/Mimecast_AT_Watchlist.yaml) | - | - |
| [Mimecast_Audit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Parsers/MimecastAudit/Mimecast_Audit.yaml) | - | - |
| [Mimecast_Cloud_Integrated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Parsers/MimecastCI/Mimecast_Cloud_Integrated.yaml) | - | - |
| [Mimecast_SEG_CG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Parsers/MimecastSEG/Mimecast_SEG_CG.yaml) | - | - |
| [Mimecast_SEG_DLP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Parsers/MimecastSEG/Mimecast_SEG_DLP.yaml) | - | - |
| [Mimecast_TTP_Attachment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Parsers/MimecastTTP/Mimecast_TTP_Attachment.yaml) | - | - |
| [Mimecast_TTP_Impersonation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Parsers/MimecastTTP/Mimecast_TTP_Impersonation.yaml) | - | - |
| [Mimecast_TTP_Url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mimecast/Parsers/MimecastTTP/Mimecast_TTP_Url.yaml) | - | - |

## Release Notes

| **Version**   | **Date Modified**              | **Change History**                                                     |
|---------------|--------------------------------|------------------------------------------------------------------------|
| 3.1.0         | 29-10-2025                     | Added Log Ingestion API support in **Data Connectors**. Added Government button for support.                                                                                                                  |
| 3.0.1         | 12-02-2025                     | Updated default table for MimecastAudit to get the Connected label on **Data Connector** UI page.                                                     |
| 3.0.0         | 09-09-2024                     | Initial Solution Release                                               |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
