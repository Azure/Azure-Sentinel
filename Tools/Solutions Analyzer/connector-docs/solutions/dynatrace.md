# Dynatrace

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Dynatrace |
| **Support Tier** | Partner |
| **Support Link** | [https://www.dynatrace.com/services-support/](https://www.dynatrace.com/services-support/) |
| **Categories** | domains |
| **First Published** | 2022-10-18 |
| **Last Updated** | 2023-10-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace) |

## Data Connectors

This solution provides **4 data connector(s)**.

### [Dynatrace Attacks](../connectors/dynatraceattacks.md)

**Publisher:** Dynatrace

This connector uses the Dynatrace Attacks REST API to ingest detected attacks into Microsoft Sentinel Log Analytics

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `DynatraceAttacks_CL` |
| **Connector Definition Files** | [Connector_Dynatrace_Attacks.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_Attacks.json) |

[→ View full connector details](../connectors/dynatraceattacks.md)

### [Dynatrace Audit Logs](../connectors/dynatraceauditlogs.md)

**Publisher:** Dynatrace

This connector uses the [Dynatrace Audit Logs REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/audit-logs) to ingest tenant audit logs into Microsoft Sentinel Log Analytics

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `DynatraceAuditLogs_CL` |
| **Connector Definition Files** | [Connector_Dynatrace_AuditLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_AuditLogs.json) |

[→ View full connector details](../connectors/dynatraceauditlogs.md)

### [Dynatrace Problems](../connectors/dynatraceproblems.md)

**Publisher:** Dynatrace

This connector uses the [Dynatrace Problem REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/problems-v2) to ingest problem events into Microsoft Sentinel Log Analytics

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `DynatraceProblems_CL` |
| **Connector Definition Files** | [Connector_Dynatrace_Problems.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_Problems.json) |

[→ View full connector details](../connectors/dynatraceproblems.md)

### [Dynatrace Runtime Vulnerabilities](../connectors/dynatraceruntimevulnerabilities.md)

**Publisher:** Dynatrace

This connector uses the [Dynatrace Security Problem REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/application-security/vulnerabilities/get-vulnerabilities) to ingest detected runtime vulnerabilities into Microsoft Sentinel Log Analytics.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `DynatraceSecurityProblems_CL` |
| **Connector Definition Files** | [Connector_Dynatrace_RuntimeVulnerabilities.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_RuntimeVulnerabilities.json) |

[→ View full connector details](../connectors/dynatraceruntimevulnerabilities.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `DynatraceAttacks_CL` | [Dynatrace Attacks](../connectors/dynatraceattacks.md) |
| `DynatraceAuditLogs_CL` | [Dynatrace Audit Logs](../connectors/dynatraceauditlogs.md) |
| `DynatraceProblems_CL` | [Dynatrace Problems](../connectors/dynatraceproblems.md) |
| `DynatraceSecurityProblems_CL` | [Dynatrace Runtime Vulnerabilities](../connectors/dynatraceruntimevulnerabilities.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 03-05-2024                     | Repackaged for parser issue fix on reinstall                       |
| 3.0.1       | 18-01-2024                     | Changes for rebranding from Microsoft 365 Defender to Microsoft Defender XDR,         |
|             |                                | Updated user-agent strings used when calling Dynatrace REST API's,                    |
|             |                                | Added new Entity Mappings to **Analytic Rules**                                       |
|             |                                | Aligned Playbook, Data Connector & Workbook version numbers with rest of solution     |
| 3.0.0       | 16-10-2023                     | Enabled new api paging mode on **Data Connector** to fix issues related to polling Dynatrace REST API's with a large number of results.   |
| 2.0.0       | 18-10-2022                     | Initial Solution Release.   |

[← Back to Solutions Index](../solutions-index.md)
