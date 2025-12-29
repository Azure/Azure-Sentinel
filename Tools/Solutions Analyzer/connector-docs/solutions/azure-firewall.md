# Azure Firewall

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

| Attribute | Value |
|:-------------------------|:---|
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

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                       |
|-------------|--------------------------------|------------------------------------------------------------------------------------------|
| 3.0.6       | 28-10-2025                     | Enhanced the Azure Firewall analytic rule to extend Fqdn from DestinationIp for improved detection of Multiple Sources Affected by the Same TI Destination. |
| 3.0.5       | 26-07-2024                     | Updated **Analytical Rule** for missing TTP	                                          |
| 3.0.4       | 12-02-2024                     | Updated **Analytical Rule**	                                          |
| 3.0.3       | 17-01-2024                     | Updated Azure Firewall **Data Connector**  to support resource specific logs.            |
| 3.0.2       | 15-12-2023                     | Updated query  in  **Analytical Rule** (Port Scan)                                       |
| 3.0.1       | 21-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.                | 
| 3.0.0       | 20-07-2023                     | Updated **Workbook** template to remove unused variables.                                |

[← Back to Solutions Index](../solutions-index.md)
