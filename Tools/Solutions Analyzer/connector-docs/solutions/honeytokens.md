# HoneyTokens

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** |  |
| **Support Tier** |  |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HoneyTokens](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HoneyTokens) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Additional Documentation

> 📄 *Source: [HoneyTokens/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HoneyTokens/README.md)*

For more details: <br>
Blog post: https://aka.ms/honeytokensblog<br>

> **IMPORTANT** <br>
> The Microsoft Sentinel Deception (Honey Tokens) solution is offered in a community supported model by the [Microsoft SIEM & XDR Community](https://github.com/Azure/Azure-Sentinel/wiki). Any support required can be raised as an [issue](https://github.com/Azure/Azure-Sentinel/issues) on GitHub where the Microsoft Sentinel community can assist. 

This article describes how to use the **Microsoft Sentinel Deception (Honey Tokens)** solution to plant decoy [Azure Key Vault](../key-vault/index.yml) keys and secrets, called *honeytokens*, into existing workloads.

Use the [analytics rules](detect-threats-built-in.md), [watchlists](watchlists.md), and [workbooks](monitor-your-data.md) provided by the solution to monitor access to the deployed honeytokens.

When using honeytokens in your system, detection principles remains the same. Because there is no legitimate reason to access a honeytoken, any activity will indicate the presence of a user who is not familiar with the environment, and could potentially be an attacker.

## Before you begin

In order to start using the **Microsoft Sentinel Deception (Honey Tokens)** solution, make sure that you have:

- **Required roles**: You must be a tenant admin to install the **Microsoft Sentinel Deception (Honey Tokens)** solution. Once the solution is installed, you can share the workbook with key vault owners so that they can deploy their own honeytokens.

- **Required data connectors**: Make sure that you've deployed the [Azure Key Vault](data-connectors-reference.md#azure-key-vault) and the [Azure Activity](data-connectors-reference.md#azure-activity) data connectors in your workspace, and that they're connected.

  Verify that data routing succeeded and that the **KeyVault** and **AzureActivity** data is flowing into Microsoft Sentinel. For more information, see:

  - [Connect Microsoft Sentinel to Azure, Windows, Microsoft, and Amazon services](https://connect-azure-windows-microsoft-services.md?tabs=AP#diagnostic-settings-based-connections)
  - [Find your Microsoft Sentinel data connector](data-connectors-reference.md)

## Install the solution

Install the **Microsoft Sentinel Deception (Honey Tokens)** solution as you would [other solutions](sentinel-solutions-deploy.md). On the **Microsoft Sentinel Deception** solution page, select **Start** to get started.

![Screenshot of the create solution page](https://learn.microsoft.com/en-us/azure/sentinel/media/monitor-key-vault-honeytokens/honeytoken-create-solution.png)

**To install the Deception solution**:

The following steps describe specific actions required for the **Microsoft Sentinel Deception (Honey Tokens)** solution.

1. On the **Basics** tab, select the same resource group where your Microsoft Sentinel workspace is located.


*[Content truncated...]*

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
