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

This solution provides **1 data connector(s)**.

### [Azure Key Vault](../connectors/azurekeyvault.md)

**Publisher:** Microsoft

Azure Key Vault is a cloud service for securely storing and accessing secrets. A secret is anything that you want to tightly control access to, such as API keys, passwords, certificates, or cryptographic keys.   This connector lets you stream your Azure Key Vault diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity in all your instances. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220125&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureKeyVault.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Data%20Connectors/AzureKeyVault.JSON) |

[→ View full connector details](../connectors/azurekeyvault.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Key Vault](../connectors/azurekeyvault.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|   
| 3.0.3       | 25-10-2024                     | Updated description of CreateUi and **Analytic Rule**					  |         
| 3.0.2       | 14-02-2024                     | Updated Entity Mapping for KeyVaultSensitiveOperations and NRT_KeyVaultSensitiveOperations **Analytic Rules** to render the GUID information correctly| 
| 3.0.1       | 01-02-2024                     | Updated ObjectGuid Identifier with Name (KeyvaultMassSecretRetrieval) **Analytic Rule** to render the GUID information correctly| 
| 3.0.0       | 03-01-2024                     | Added field ResourceId in (KeyvaultMassSecretRetrieval) **Analytic Rule** for proper Entity Mapping|

[← Back to Solutions Index](../solutions-index.md)
