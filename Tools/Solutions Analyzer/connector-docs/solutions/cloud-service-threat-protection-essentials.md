# Cloud Service Threat Protection Essentials

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-11-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Service%20Threat%20Protection%20Essentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Service%20Threat%20Protection%20Essentials) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **3 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AzureActivity`](../tables/azureactivity.md) | Hunting |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Hunting |
| [`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md) | Hunting |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 2 |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Azure Key Vault Access Policy Manipulation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Service%20Threat%20Protection%20Essentials/Hunting%20Queries/AzureKeyVaultAccessManipulation.yaml) | CredentialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Azure Resources Assigned Public IP Addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Service%20Threat%20Protection%20Essentials/Hunting%20Queries/AzureResourceAssignedPublicIP.yaml) | Impact | [`AzureActivity`](../tables/azureactivity.md)<br>[`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                            |
|-------------|--------------------------------|-----------------------------------------------|
| 3.0.0       | 09-02-2024                     | Tagged for dependent solutions for deployment |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
