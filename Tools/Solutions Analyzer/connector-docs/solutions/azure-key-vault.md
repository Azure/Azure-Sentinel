# Azure Key Vault

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureKeyVault.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Data%20Connectors/AzureKeyVault.JSON) |

[→ View full connector details](../connectors/azurekeyvault.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Key Vault](../connectors/azurekeyvault.md) |

[← Back to Solutions Index](../solutions-index.md)
