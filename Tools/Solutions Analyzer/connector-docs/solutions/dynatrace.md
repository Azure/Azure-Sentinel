# Dynatrace

## Solution Information

| | |
|------------------------|-------|
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

### [Dynatrace Audit Logs](../connectors/dynatraceauditlogs.md)

**Publisher:** Dynatrace

### [Dynatrace Problems](../connectors/dynatraceproblems.md)

**Publisher:** Dynatrace

### [Dynatrace Runtime Vulnerabilities](../connectors/dynatraceruntimevulnerabilities.md)

**Publisher:** Dynatrace

This connector uses the [Dynatrace Security Problem REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/application-security/vulnerabilities/get-vulnerabilities) to ingest detected runtime vulnerabilities into Microsoft Sentinel Log Analytics.

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
