# Wiz

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Wiz |
| **Support Tier** | Partner |
| **Support Link** | [https://support.wiz.io/](https://support.wiz.io/) |
| **Categories** | domains |
| **First Published** | 2023-06-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Wiz](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Wiz) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Wiz](../connectors/wiz.md)

## Tables Reference

This solution uses **6 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`WizAuditLogsV2_CL`](../tables/wizauditlogsv2-cl.md) | [Wiz](../connectors/wiz.md) | - |
| [`WizAuditLogs_CL`](../tables/wizauditlogs-cl.md) | [Wiz](../connectors/wiz.md) | - |
| [`WizIssuesV2_CL`](../tables/wizissuesv2-cl.md) | [Wiz](../connectors/wiz.md) | Workbooks |
| [`WizIssues_CL`](../tables/wizissues-cl.md) | [Wiz](../connectors/wiz.md) | Workbooks |
| [`WizVulnerabilitiesV2_CL`](../tables/wizvulnerabilitiesv2-cl.md) | [Wiz](../connectors/wiz.md) | - |
| [`WizVulnerabilities_CL`](../tables/wizvulnerabilities-cl.md) | [Wiz](../connectors/wiz.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [WizFindings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Wiz/Workbooks/WizFindings.json) | [`WizIssuesV2_CL`](../tables/wizissuesv2-cl.md)<br>[`WizIssues_CL`](../tables/wizissues-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 15-07-2024                     | Updated the queries on the **Workbook** and **Connector** to match with the new table names we offer  |
| 2.0.0       | 07-09-2023                     | Updated **Workbook** query in Maintemplate  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
