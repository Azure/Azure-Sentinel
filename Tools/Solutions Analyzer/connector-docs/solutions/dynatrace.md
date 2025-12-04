# Dynatrace

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Dynatrace |
| **Support Tier** | Partner |
| **Support Link** | [https://www.dynatrace.com/services-support/](https://www.dynatrace.com/services-support/) |
| **Categories** | domains |
| **First Published** | 2022-10-18 |
| **Last Updated** | 2023-10-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace) |\n\n## Data Connectors

This solution provides **4 data connector(s)**.

### Dynatrace Attacks

**Publisher:** Dynatrace

This connector uses the Dynatrace Attacks REST API to ingest detected attacks into Microsoft Sentinel Log Analytics

**Tables Ingested:**

- `DynatraceAttacks_CL`

**Connector Definition Files:**

- [Connector_Dynatrace_Attacks.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_Attacks.json)

### Dynatrace Audit Logs

**Publisher:** Dynatrace

This connector uses the [Dynatrace Audit Logs REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/audit-logs) to ingest tenant audit logs into Microsoft Sentinel Log Analytics

**Tables Ingested:**

- `DynatraceAuditLogs_CL`

**Connector Definition Files:**

- [Connector_Dynatrace_AuditLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_AuditLogs.json)

### Dynatrace Problems

**Publisher:** Dynatrace

This connector uses the [Dynatrace Problem REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/problems-v2) to ingest problem events into Microsoft Sentinel Log Analytics

**Tables Ingested:**

- `DynatraceProblems_CL`

**Connector Definition Files:**

- [Connector_Dynatrace_Problems.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_Problems.json)

### Dynatrace Runtime Vulnerabilities

**Publisher:** Dynatrace

This connector uses the [Dynatrace Security Problem REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/application-security/vulnerabilities/get-vulnerabilities) to ingest detected runtime vulnerabilities into Microsoft Sentinel Log Analytics.

**Tables Ingested:**

- `DynatraceSecurityProblems_CL`

**Connector Definition Files:**

- [Connector_Dynatrace_RuntimeVulnerabilities.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_RuntimeVulnerabilities.json)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `DynatraceAttacks_CL` | Dynatrace Attacks |
| `DynatraceAuditLogs_CL` | Dynatrace Audit Logs |
| `DynatraceProblems_CL` | Dynatrace Problems |
| `DynatraceSecurityProblems_CL` | Dynatrace Runtime Vulnerabilities |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n