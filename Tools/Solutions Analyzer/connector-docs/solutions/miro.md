# Miro

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Miro |
| **Support Tier** | Partner |
| **Support Link** | [https://help.miro.com](https://help.miro.com) |
| **Categories** | domains |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Miro](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Miro) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Miro Audit Logs (Enterprise Plan)](../connectors/miroauditlogsdataconnector.md)

**Publisher:** Miro

The [Miro Audit Logs](https://help.miro.com/hc/en-us/articles/360017571434-Audit-logs) data connector enables you to ingest organization-wide audit events from Miro into Microsoft Sentinel. Monitor user activities, security events, content access, team changes, and administrative actions to enhance your security operations and compliance capabilities.



**Key features:**

- Track user authentication and access patterns.

- Monitor content creation, sharing, and deletion.

- Audit team and organization configuration changes.

- Detect suspicious activities and policy violations.

- Meet compliance and regulatory requirements.



**Requirements:**

- **Miro Plan**: [Enterprise Plan](https://miro.com/pricing/).

- **OAuth scope**: `auditlogs:read`.

- **Role**: Company Admin in your Miro organization.



💡 **Not on Enterprise Plan yet?** Upgrade to [Miro Enterprise](https://miro.com/enterprise/) to unlock audit logs and gain comprehensive visibility into your team's activities in Microsoft Sentinel.



For detailed instructions, refer to the [documentation](https://help.miro.com/hc/en-us/articles/31325908249362).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `MiroAuditLogs_CL` |
| **Connector Definition Files** | [MiroAuditLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Miro/Data%20Connectors/MiroAuditLogs_CCF/MiroAuditLogs_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/miroauditlogsdataconnector.md)

### [Miro Content Logs (Enterprise Plan + Enterprise Guard)](../connectors/mirocontentlogsdataconnector.md)

**Publisher:** Miro

The [Miro Content Logs](https://help.miro.com/hc/en-us/articles/17774729839378-Content-Logs-overview) data connector enables you to ingest content activity logs from Miro into Microsoft Sentinel. Part of Miro's Enterprise Guard eDiscovery capabilities, this connector provides content-level visibility for compliance, legal hold, and advanced threat detection.



**Key features:**

- Track all content item changes.

- Monitor content modifications by user and timestamp.

- Support compliance and eDiscovery requirements.

- Detect data exfiltration and insider threats.

- Meet regulatory and legal hold obligations.



**Requirements:**

- **Miro Plan**: [Enterprise Plan](https://miro.com/pricing/) + **Enterprise Guard** add-on.

- **OAuth scope**: `contentlogs:export`.

- **Role**: Company Admin in your Miro organization.

- **Organization ID**: Your Miro organization identifier.



💡 **Not on Enterprise Plan yet?** Upgrade to [Miro Enterprise](https://miro.com/enterprise/) to unlock advanced security and compliance features for your team's collaboration activities in Microsoft Sentinel.



💡 **Need Content Logs?** Content activity logging is part of [Miro Enterprise Guard](https://miro.com/enterprise-guard/), which provides advanced security, compliance, and eDiscovery features. Contact your Miro account manager to add Enterprise Guard to your Enterprise Plan and unlock content-level monitoring in Microsoft Sentinel.



**Note:** If you only have the base Enterprise Plan (without Enterprise Guard), please use the **Miro Audit Logs** connector instead for organization-level event monitoring.



For detailed instructions, refer to the [documentation](https://help.miro.com/hc/en-us/articles/31325908249362).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `MiroContentLogs_CL` |
| **Connector Definition Files** | [MiroContentLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Miro/Data%20Connectors/MiroContentLogs_CCF/MiroContentLogs_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/mirocontentlogsdataconnector.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MiroAuditLogs_CL` | [Miro Audit Logs (Enterprise Plan)](../connectors/miroauditlogsdataconnector.md) |
| `MiroContentLogs_CL` | [Miro Content Logs (Enterprise Plan + Enterprise Guard)](../connectors/mirocontentlogsdataconnector.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                              |
|-------------|--------------------------------|-------------------------------------------------------------------------------------------------|
| 3.0.0       | 05-12-2025                     | Initial release of the Miro solution with two **CCF connectors** (Audit Logs and Content Logs). |

[← Back to Solutions Index](../solutions-index.md)
