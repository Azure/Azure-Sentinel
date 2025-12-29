# Azure Firewall

| | |
|----------|-------|
| **Connector ID** | `AzureFirewall` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AZFWApplicationRule`](../tables-index.md#azfwapplicationrule), [`AZFWDnsQuery`](../tables-index.md#azfwdnsquery), [`AZFWFatFlow`](../tables-index.md#azfwfatflow), [`AZFWFlowTrace`](../tables-index.md#azfwflowtrace), [`AZFWIdpsSignature`](../tables-index.md#azfwidpssignature), [`AZFWInternalFqdnResolutionFailure`](../tables-index.md#azfwinternalfqdnresolutionfailure), [`AZFWNatRule`](../tables-index.md#azfwnatrule), [`AZFWNetworkRule`](../tables-index.md#azfwnetworkrule), [`AZFWThreatIntel`](../tables-index.md#azfwthreatintel), [`AzureDiagnostics`](../tables-index.md#azurediagnostics) |
| **Used in Solutions** | [Azure Firewall](../solutions/azure-firewall.md) |
| **Connector Definition Files** | [AzureFirewall.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Data%20Connectors/AzureFirewall.JSON) |

Connect to Azure Firewall. Azure Firewall is a managed, cloud-based network security service that protects your Azure Virtual Network resources. It's a fully stateful firewall as a service with built-in high availability and unrestricted cloud scalability. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220124&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Azure Firewall to Microsoft Sentinel**

Enable Diagnostic Logs on All Firewalls.
- **Configure Azure Firewall**

Inside your Firewall resource:

1.  Select **Diagnostic logs.​**
2.  Select **+ Add diagnostic setting.​**
3.  In the **Diagnostic setting** blade:
    -   Type a **Name**.
    -   Select **Send to Log Analytics**.
    -   Choose the log destination workspace.
    -   Select the categories that you want to analyze ( Azure Firewall Network Rule, Azure Firewall Application Rule,Azure Firewall Nat Rule,Azure Firewall Threat Intelligence,Azure Firewall IDPS Signature,Azure Firewall DNS query,Azure Firewall FQDN Resolution Failure,Azure Firewall Fat Flow Log,Azure Firewall Flow Trace Log)
    -   Click **Save**.

[← Back to Connectors Index](../connectors-index.md)
