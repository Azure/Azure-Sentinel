# MimecastAudit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Mimecast |
| **Support Tier** | Partner |
| **Support Link** | [https://mimecastsupport.zendesk.com/](https://mimecastsupport.zendesk.com/) |
| **Categories** | domains |
| **First Published** | 2022-02-24 |
| **Last Updated** | 2022-02-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastAudit) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Mimecast Audit & Authentication](../connectors/mimecastauditapi.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`MimecastAudit_CL`](../tables/mimecastaudit-cl.md) | [Mimecast Audit & Authentication](../connectors/mimecastauditapi.md) | Analytics, Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Mimecast Audit - Logon Authentication Failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastAudit/Analytic%20Rules/MimecastAudit.yaml) | High | Discovery, InitialAccess, CredentialAccess | [`MimecastAudit_CL`](../tables/mimecastaudit-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [MimecastAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastAudit/Workbooks/MimecastAudit.json) | [`MimecastAudit_CL`](../tables/mimecastaudit-cl.md) |

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
