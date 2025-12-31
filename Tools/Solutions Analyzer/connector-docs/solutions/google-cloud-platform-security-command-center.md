# Google Cloud Platform Security Command Center

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-09-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Google Security Command Center](../connectors/googlesccdefinition.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`GoogleCloudSCC`](../tables/googlecloudscc.md) | [Google Security Command Center](../connectors/googlesccdefinition.md) | Analytics, Hunting |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 5 |
| Hunting Queries | 5 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [GCP Security Command Center - Detect DNSSEC disabled for DNS zones](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Analytic%20Rules/GCPDNSSECDisabled.yaml) | Medium | Collection, CommandAndControl, DefenseEvasion | [`GoogleCloudSCC`](../tables/googlecloudscc.md) |
| [GCP Security Command Center - Detect Firewall rules allowing unrestricted high-risk ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Analytic%20Rules/GCPFirewallHighRiskOpenPorts.yaml) | High | InitialAccess, LateralMovement, Discovery | [`GoogleCloudSCC`](../tables/googlecloudscc.md) |
| [GCP Security Command Center - Detect Open/Unrestricted API Keys](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Analytic%20Rules/GCPAPIKeyApisUnrestricted.yaml) | Medium | InitialAccess, CredentialAccess | [`GoogleCloudSCC`](../tables/googlecloudscc.md) |
| [GCP Security Command Center - Detect Resources with Logging Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Analytic%20Rules/GCPLoggingDisabled.yaml) | Medium | DefenseEvasion | [`GoogleCloudSCC`](../tables/googlecloudscc.md) |
| [GCP Security Command Center - Detect projects with API Keys present](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Analytic%20Rules/GCPAPIKeyExists.yaml) | Medium | CredentialAccess | [`GoogleCloudSCC`](../tables/googlecloudscc.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Identify Compute VMs with Secure Boot Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Hunting%20Queries/GCPComputeSecureBootDisabledDetection.yaml) | ResourceDevelopment, DefenseEvasion | [`GoogleCloudSCC`](../tables/googlecloudscc.md) |
| [Identify GCP Instances with Full API Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Hunting%20Queries/GCPFullAPIAccessDetection.yaml) | PrivilegeEscalation | [`GoogleCloudSCC`](../tables/googlecloudscc.md) |
| [Identify GCP Service Account with Overly Permissive Roles](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Hunting%20Queries/GCPAdminServiceAccountDetection.yaml) | PrivilegeEscalation, Persistence | [`GoogleCloudSCC`](../tables/googlecloudscc.md) |
| [Identify GCP User-Managed Service Account Keys](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Hunting%20Queries/GCPUserManagedServiceAccountKeyDetection.yaml) | CredentialAccess | [`GoogleCloudSCC`](../tables/googlecloudscc.md) |
| [Identify Public GCP Storage Buckets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Hunting%20Queries/GCPPublicBuckets.yaml) | Exfiltration, Discovery | [`GoogleCloudSCC`](../tables/googlecloudscc.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.0.7       | 11-11-2025                     | Add New **Analytic Rules** and **Hunting Queries** |
| 3.0.6       | 12-11-2024                     | Modified datatype query for **Data Connector** |
| 3.0.5       | 16-05-2024                     | Modification in ** Data Connector **           |
| 3.0.4       | 28-02-2024                     | Initial solution release                       |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
