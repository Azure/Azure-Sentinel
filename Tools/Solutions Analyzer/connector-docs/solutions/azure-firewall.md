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
| `AZFWApplicationRule` | Azure Firewall |
| `AZFWDnsQuery` | Azure Firewall |
| `AZFWFatFlow` | Azure Firewall |
| `AZFWFlowTrace` | Azure Firewall |
| `AZFWIdpsSignature` | Azure Firewall |
| `AZFWInternalFqdnResolutionFailure` | Azure Firewall |
| `AZFWNatRule` | Azure Firewall |
| `AZFWNetworkRule` | Azure Firewall |
| `AZFWThreatIntel` | Azure Firewall |
| `AzureDiagnostics` | Azure Firewall |

[← Back to Solutions Index](../solutions-index.md)
