# GoogleCloudSCC

Reference for GoogleCloudSCC table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | GCP |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✓ Yes |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/googlecloudscc) |

## Solutions (1)

This table is used by the following solutions:

- [Google Cloud Platform Security Command Center](../solutions/google-cloud-platform-security-command-center.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Google Security Command Center](../connectors/googlesccdefinition.md)

---

## Content Items Using This Table (10)

### Analytic Rules (5)

**In solution [Google Cloud Platform Security Command Center](../solutions/google-cloud-platform-security-command-center.md):**
- [GCP Security Command Center - Detect DNSSEC disabled for DNS zones](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Analytic%20Rules/GCPDNSSECDisabled.yaml)
- [GCP Security Command Center - Detect Firewall rules allowing unrestricted high-risk ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Analytic%20Rules/GCPFirewallHighRiskOpenPorts.yaml)
- [GCP Security Command Center - Detect Open/Unrestricted API Keys](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Analytic%20Rules/GCPAPIKeyApisUnrestricted.yaml)
- [GCP Security Command Center - Detect Resources with Logging Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Analytic%20Rules/GCPLoggingDisabled.yaml)
- [GCP Security Command Center - Detect projects with API Keys present](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Analytic%20Rules/GCPAPIKeyExists.yaml)

### Hunting Queries (5)

**In solution [Google Cloud Platform Security Command Center](../solutions/google-cloud-platform-security-command-center.md):**
- [Identify Compute VMs with Secure Boot Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Hunting%20Queries/GCPComputeSecureBootDisabledDetection.yaml)
- [Identify GCP Instances with Full API Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Hunting%20Queries/GCPFullAPIAccessDetection.yaml)
- [Identify GCP Service Account with Overly Permissive Roles](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Hunting%20Queries/GCPAdminServiceAccountDetection.yaml)
- [Identify GCP User-Managed Service Account Keys](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Hunting%20Queries/GCPUserManagedServiceAccountKeyDetection.yaml)
- [Identify Public GCP Storage Buckets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Hunting%20Queries/GCPPublicBuckets.yaml)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
