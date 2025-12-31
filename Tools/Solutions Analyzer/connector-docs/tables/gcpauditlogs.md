# GCPAuditLogs

Reference for GCPAuditLogs table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | GCP |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✓ Yes |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/gcpauditlogs) |

## Solutions (2)

This table is used by the following solutions:

- [Google Cloud Platform Audit Logs](../solutions/google-cloud-platform-audit-logs.md)
- [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md)

## Connectors (2)

This table is ingested by the following connectors:

- [GCP Pub/Sub Audit Logs](../connectors/gcpauditlogsdefinition.md)
- [GCP Pub/Sub Audit Logs](../connectors/gcppub-subauditlogs.md)

---

## Content Items Using This Table (2)

### Analytic Rules (2)

**In solution [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md):**
- [Cross-Cloud Suspicious Compute resource creation in GCP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/Cross-CloudSuspiciousComputeResourcecreationinGCP.yaml)
- [Cross-Cloud Suspicious user activity observed in GCP Envourment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/CrossCloudSuspiciousUserActivityObservedInGCPEnvourment.yaml)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
