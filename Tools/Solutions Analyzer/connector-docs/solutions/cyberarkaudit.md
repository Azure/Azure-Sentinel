# CyberArkAudit

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | CyberArk Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyberark.com/services-support/technical-support-contact/](https://www.cyberark.com/services-support/technical-support-contact/) |
| **Categories** | domains |
| **First Published** | 2024-03-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkAudit) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CyberArkAudit](../connectors/cyberarkaudit.md)

**Publisher:** CyberArk

The [CyberArk Audit](https://docs.cyberark.com/Audit/Latest/en/Content/Resources/_TopNav/cc_Home.htm) data connector provides the capability to retrieve security event logs of the CyberArk Audit service and more events into Microsoft Sentinel through the REST API. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
| **Tables Ingested** | `CyberArkAudit` |
| | `CyberArk_AuditEvents_CL` |
| **Connector Definition Files** | [CyberArkAudit_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkAudit/Data%20Connectors/CyberArkAudit_API_FunctionApp.json) |

[→ View full connector details](../connectors/cyberarkaudit.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyberArkAudit` | [CyberArkAudit](../connectors/cyberarkaudit.md) |
| `CyberArk_AuditEvents_CL` | [CyberArkAudit](../connectors/cyberarkaudit.md) |

[← Back to Solutions Index](../solutions-index.md)
