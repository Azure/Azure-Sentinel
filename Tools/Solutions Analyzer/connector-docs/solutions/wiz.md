# Wiz

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Wiz |
| **Support Tier** | Partner |
| **Support Link** | [https://support.wiz.io/](https://support.wiz.io/) |
| **Categories** | domains |
| **First Published** | 2023-06-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Wiz](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Wiz) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Wiz](../connectors/wiz.md)

**Publisher:** Wiz

The Wiz connector allows you to easily send Wiz Issues, Vulnerability Findings, and Audit logs to Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `WizAuditLogsV2_CL` |
| | `WizAuditLogs_CL` |
| | `WizIssuesV2_CL` |
| | `WizIssues_CL` |
| | `WizVulnerabilitiesV2_CL` |
| | `WizVulnerabilities_CL` |
| **Connector Definition Files** | [template_WIZ.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Wiz/Data%20Connectors/template_WIZ.json) |

[→ View full connector details](../connectors/wiz.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `WizAuditLogsV2_CL` | [Wiz](../connectors/wiz.md) |
| `WizAuditLogs_CL` | [Wiz](../connectors/wiz.md) |
| `WizIssuesV2_CL` | [Wiz](../connectors/wiz.md) |
| `WizIssues_CL` | [Wiz](../connectors/wiz.md) |
| `WizVulnerabilitiesV2_CL` | [Wiz](../connectors/wiz.md) |
| `WizVulnerabilities_CL` | [Wiz](../connectors/wiz.md) |

[← Back to Solutions Index](../solutions-index.md)
