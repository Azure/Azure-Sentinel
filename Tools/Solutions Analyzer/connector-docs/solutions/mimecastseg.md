# MimecastSEG

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Mimecast |
| **Support Tier** | Partner |
| **Support Link** | [https://mimecastsupport.zendesk.com/](https://mimecastsupport.zendesk.com/) |
| **Categories** | domains |
| **First Published** | 2022-02-24 |
| **Last Updated** | 2022-02-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Mimecast Secure Email Gateway](../connectors/mimecastsiemapi.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`MimecastDLP_CL`](../tables/mimecastdlp-cl.md) | [Mimecast Secure Email Gateway](../connectors/mimecastsiemapi.md) | Analytics |
| [`MimecastSIEM_CL`](../tables/mimecastsiem-cl.md) | [Mimecast Secure Email Gateway](../connectors/mimecastsiemapi.md) | Analytics, Workbooks |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 9 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Mimecast Data Leak Prevention - Hold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG/Analytic%20Rules/MimecastDLP_Hold.yaml) | Informational | Exfiltration | [`MimecastDLP_CL`](../tables/mimecastdlp-cl.md) |
| [Mimecast Data Leak Prevention - Notifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG/Analytic%20Rules/MimecastDLP.yaml) | High | Exfiltration | [`MimecastDLP_CL`](../tables/mimecastdlp-cl.md) |
| [Mimecast Secure Email Gateway - AV](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG/Analytic%20Rules/MimecastSIEM_AV.yaml) | Informational | Execution | [`MimecastSIEM_CL`](../tables/mimecastsiem-cl.md) |
| [Mimecast Secure Email Gateway - Attachment Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG/Analytic%20Rules/MimecastSIEM_Attachment.yaml) | High | Collection, Exfiltration, Discovery, InitialAccess, Execution | [`MimecastSIEM_CL`](../tables/mimecastsiem-cl.md) |
| [Mimecast Secure Email Gateway - Impersonation Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG/Analytic%20Rules/MimecastSIEM_Impersonation.yaml) | High | Discovery, LateralMovement, Collection | [`MimecastSIEM_CL`](../tables/mimecastsiem-cl.md) |
| [Mimecast Secure Email Gateway - Internal Email Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG/Analytic%20Rules/MimecastSIEM_Internal_Mail_Protect.yaml) | High | LateralMovement, Persistence, Exfiltration | [`MimecastSIEM_CL`](../tables/mimecastsiem-cl.md) |
| [Mimecast Secure Email Gateway - Spam Event Thread](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG/Analytic%20Rules/MimecastSIEM_Spam_Event.yaml) | Low | Discovery | [`MimecastSIEM_CL`](../tables/mimecastsiem-cl.md) |
| [Mimecast Secure Email Gateway - URL Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG/Analytic%20Rules/MimecastSIEM_Url_Protect.yaml) | High | InitialAccess, Discovery, Execution | [`MimecastSIEM_CL`](../tables/mimecastsiem-cl.md) |
| [Mimecast Secure Email Gateway - Virus](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG/Analytic%20Rules/MimecastSIEM_Virus.yaml) | Informational | Execution | [`MimecastSIEM_CL`](../tables/mimecastsiem-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [MimecastSEGworkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastSEG/Workbooks/MimecastSEGworkbook.json) | [`MimecastSIEM_CL`](../tables/mimecastsiem-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 06-03-2025                     | Solution Deprecated   |
| 3.0.1       | 05-12-2023                     | Enhanced **Dataconnector** to use existing workspace and updated checkpoint mechanism |
| 3.0.0       | 23-08-2023                     | Initial Solution Release                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
