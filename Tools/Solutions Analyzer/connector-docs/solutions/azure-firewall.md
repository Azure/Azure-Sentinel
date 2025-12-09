# Azure Firewall

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Firewall](../connectors/azurefirewall.md)

**Publisher:** Microsoft

Connect to Azure Firewall. Azure Firewall is a managed, cloud-based network security service that protects your Azure Virtual Network resources. It's a fully stateful firewall as a service with built-in high availability and unrestricted cloud scalability. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220124&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `AZFWApplicationRule` |
| | `AZFWDnsQuery` |
| | `AZFWFatFlow` |
| | `AZFWFlowTrace` |
| | `AZFWIdpsSignature` |
| | `AZFWInternalFqdnResolutionFailure` |
| | `AZFWNatRule` |
| | `AZFWNetworkRule` |
| | `AZFWThreatIntel` |
| | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureFirewall.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Data%20Connectors/AzureFirewall.JSON) |

[→ View full connector details](../connectors/azurefirewall.md)

## Tables Reference

This solution ingests data into **10 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AZFWApplicationRule` | [Azure Firewall](../connectors/azurefirewall.md) |
| `AZFWDnsQuery` | [Azure Firewall](../connectors/azurefirewall.md) |
| `AZFWFatFlow` | [Azure Firewall](../connectors/azurefirewall.md) |
| `AZFWFlowTrace` | [Azure Firewall](../connectors/azurefirewall.md) |
| `AZFWIdpsSignature` | [Azure Firewall](../connectors/azurefirewall.md) |
| `AZFWInternalFqdnResolutionFailure` | [Azure Firewall](../connectors/azurefirewall.md) |
| `AZFWNatRule` | [Azure Firewall](../connectors/azurefirewall.md) |
| `AZFWNetworkRule` | [Azure Firewall](../connectors/azurefirewall.md) |
| `AZFWThreatIntel` | [Azure Firewall](../connectors/azurefirewall.md) |
| `AzureDiagnostics` | [Azure Firewall](../connectors/azurefirewall.md) |

[← Back to Solutions Index](../solutions-index.md)
