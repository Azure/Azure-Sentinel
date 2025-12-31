# MimecastTTP

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Mimecast |
| **Support Tier** | Partner |
| **Support Link** | [https://mimecastsupport.zendesk.com/](https://mimecastsupport.zendesk.com/) |
| **Categories** | domains |
| **First Published** | 2022-02-24 |
| **Last Updated** | 2022-02-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTTP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTTP) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`MimecastTTPAttachment_CL`](../tables/mimecastttpattachment-cl.md) | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) | Analytics, Workbooks |
| [`MimecastTTPImpersonation_CL`](../tables/mimecastttpimpersonation-cl.md) | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) | Analytics, Workbooks |
| [`MimecastTTPUrl_CL`](../tables/mimecastttpurl-cl.md) | [Mimecast Targeted Threat Protection](../connectors/mimecastttpapi.md) | Analytics, Workbooks |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 3 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Mimecast Targeted Threat Protection - Attachment Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTTP/Analytic%20Rules/MimecastTTPAttachment.yaml) | High | InitialAccess, Discovery | [`MimecastTTPAttachment_CL`](../tables/mimecastttpattachment-cl.md) |
| [Mimecast Targeted Threat Protection - Impersonation Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTTP/Analytic%20Rules/MimecastTTPImpersonation.yaml) | High | Exfiltration, Collection, Discovery | [`MimecastTTPImpersonation_CL`](../tables/mimecastttpimpersonation-cl.md) |
| [Mimecast Targeted Threat Protection - URL Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTTP/Analytic%20Rules/MimecastTTPUrl.yaml) | High | InitialAccess, Discovery | [`MimecastTTPUrl_CL`](../tables/mimecastttpurl-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [MimecastTTPWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTTP/Workbooks/MimecastTTPWorkbook.json) | [`MimecastTTPAttachment_CL`](../tables/mimecastttpattachment-cl.md)<br>[`MimecastTTPImpersonation_CL`](../tables/mimecastttpimpersonation-cl.md)<br>[`MimecastTTPUrl_CL`](../tables/mimecastttpurl-cl.md) |

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
