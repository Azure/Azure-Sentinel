# Dynatrace Runtime Vulnerabilities

| | |
|----------|-------|
| **Connector ID** | `DynatraceRuntimeVulnerabilities` |
| **Publisher** | Dynatrace |
| **Tables Ingested** | [`DynatraceSecurityProblems_CL`](../tables-index.md#dynatracesecurityproblems_cl) |
| **Used in Solutions** | [Dynatrace](../solutions/dynatrace.md) |
| **Connector Definition Files** | [Connector_Dynatrace_RuntimeVulnerabilities.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_RuntimeVulnerabilities.json) |

This connector uses the [Dynatrace Security Problem REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/application-security/vulnerabilities/get-vulnerabilities) to ingest detected runtime vulnerabilities into Microsoft Sentinel Log Analytics.

[← Back to Connectors Index](../connectors-index.md)
