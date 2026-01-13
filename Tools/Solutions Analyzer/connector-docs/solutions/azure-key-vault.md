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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **Policy​**: owner role assigned for each policy assignment scope.​

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect your Azure Key Vault diagnostics logs into Sentinel.**

This connector uses Azure Policy to apply a single Azure Key Vault  log-streaming configuration to a collection of instances, defined as a scope.   
Follow the instructions below to create and apply a policy to all current and future instances. **Note**, you may already have an active policy for this resource type.
**Stream diagnostics logs from your Azure Key Vault at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.​**

    >1. In the **Basics** tab, click the button with the three dots under **Scope** to select your resources assignment scope.
        >2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log and metric types you want to ingest.
        >3. To apply the policy on your existing resources, select the **Remediation tab** and mark the **Create a remediation task** checkbox.
    - **Configure policy assignment**

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
