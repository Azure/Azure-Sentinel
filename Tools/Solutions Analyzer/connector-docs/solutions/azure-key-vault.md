# Azure Key Vault

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Azure Key Vault](../connectors/azurekeyvault.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | [Azure Key Vault](../connectors/azurekeyvault.md) | Analytics, Workbooks |
| [`securityresources`](../tables/securityresources.md) | - | Workbooks |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | - | Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | - | Workbooks |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 4 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Azure Key Vault access TimeSeries anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/TimeSeriesKeyvaultAccessAnomaly.yaml) | Low | CredentialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Mass secret retrieval from Azure Key Vault](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/KeyvaultMassSecretRetrieval.yaml) | Low | CredentialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [NRT Sensitive Azure Key Vault operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/NRT_KeyVaultSensitiveOperations.yaml) | Low | Impact | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Sensitive Azure Key Vault operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/KeyVaultSensitiveOperations.yaml) | Low | Impact | [`AzureDiagnostics`](../tables/azurediagnostics.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AzureKeyVaultWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Workbooks/AzureKeyVaultWorkbook.json) | [`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`securityresources`](../tables/securityresources.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|   
| 3.0.3       | 25-10-2024                     | Updated description of CreateUi and **Analytic Rule**					  |         
| 3.0.2       | 14-02-2024                     | Updated Entity Mapping for KeyVaultSensitiveOperations and NRT_KeyVaultSensitiveOperations **Analytic Rules** to render the GUID information correctly| 
| 3.0.1       | 01-02-2024                     | Updated ObjectGuid Identifier with Name (KeyvaultMassSecretRetrieval) **Analytic Rule** to render the GUID information correctly| 
| 3.0.0       | 03-01-2024                     | Added field ResourceId in (KeyvaultMassSecretRetrieval) **Analytic Rule** for proper Entity Mapping|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
