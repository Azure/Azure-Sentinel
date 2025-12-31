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

This solution provides **1 data connector(s)**:

- [Azure Firewall](../connectors/azurefirewall.md)

## Tables Reference

This solution uses **12 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AZFWApplicationRule`](../tables/azfwapplicationrule.md) | [Azure Firewall](../connectors/azurefirewall.md) | Analytics, Workbooks |
| [`AZFWDnsQuery`](../tables/azfwdnsquery.md) | [Azure Firewall](../connectors/azurefirewall.md) | Workbooks |
| [`AZFWFatFlow`](../tables/azfwfatflow.md) | [Azure Firewall](../connectors/azurefirewall.md) | - |
| [`AZFWFlowTrace`](../tables/azfwflowtrace.md) | [Azure Firewall](../connectors/azurefirewall.md) | - |
| [`AZFWIdpsSignature`](../tables/azfwidpssignature.md) | [Azure Firewall](../connectors/azurefirewall.md) | Workbooks |
| [`AZFWInternalFqdnResolutionFailure`](../tables/azfwinternalfqdnresolutionfailure.md) | [Azure Firewall](../connectors/azurefirewall.md) | - |
| [`AZFWNatRule`](../tables/azfwnatrule.md) | [Azure Firewall](../connectors/azurefirewall.md) | Workbooks |
| [`AZFWNetworkRule`](../tables/azfwnetworkrule.md) | [Azure Firewall](../connectors/azurefirewall.md) | Workbooks |
| [`AZFWThreatIntel`](../tables/azfwthreatintel.md) | [Azure Firewall](../connectors/azurefirewall.md) | - |
| [`AlertTimeSrcIpToDstIpPort`](../tables/alerttimesrciptodstipport.md) | - | Hunting |
| [`AlertTimeSrcIpToPort`](../tables/alerttimesrciptoport.md) | - | Hunting |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | [Azure Firewall](../connectors/azurefirewall.md) | Workbooks |

## Content Items

This solution includes **20 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 6 |
| Hunting Queries | 5 |
| Playbooks | 5 |
| Workbooks | 4 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Abnormal Deny Rate for Source IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Analytic%20Rules/Azure%20Firewall%20-%20Abnormal%20Deny%20Rate%20for%20Source%20IP.yaml) | Medium | InitialAccess, Exfiltration, CommandAndControl | - |
| [Abnormal Port to Protocol](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Analytic%20Rules/Azure%20Firewall%20-%20Abnormal%20Port%20to%20Protocol.yaml) | Medium | Exfiltration, CommandAndControl | - |
| [Multiple Sources Affected by the Same TI Destination](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Analytic%20Rules/Azure%20Firewall%20-%20Multiple%20Sources%20Affected%20by%20the%20Same%20TI%20Destination.yaml) | Medium | Exfiltration, CommandAndControl | - |
| [Port Scan](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Analytic%20Rules/Azure%20Firewall%20-%20Port%20Scan.yaml) | Medium | Discovery | [`AZFWApplicationRule`](../tables/azfwapplicationrule.md) |
| [Port Sweep](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Analytic%20Rules/Azure%20Firewall%20-%20Port%20Sweep.yaml) | Medium | Discovery | [`AZFWApplicationRule`](../tables/azfwapplicationrule.md) |
| [Several deny actions registered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Analytic%20Rules/SeveralDenyActionsRegistered.yaml) | Medium | Discovery, LateralMovement, CommandAndControl | [`AZFWApplicationRule`](../tables/azfwapplicationrule.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [First Time Source IP to Destination](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Hunting%20Queries/Azure%20Firewall%20-%20First%20time%20source%20IP%20to%20Destination.yaml) | Exfiltration, CommandAndControl | [`AlertTimeSrcIpToDstIpPort`](../tables/alerttimesrciptodstipport.md) |
| [First Time Source IP to Destination Using Port](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Hunting%20Queries/Azure%20Firewall%20-%20First%20Time%20Source%20IP%20to%20Destination%20Using%20Port.yaml) | Exfiltration, CommandAndControl | [`AlertTimeSrcIpToDstIpPort`](../tables/alerttimesrciptodstipport.md) |
| [Source IP Abnormally Connects to Multiple Destinations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Hunting%20Queries/Azure%20Firewall%20-%20Source%20IP%20Abnormally%20Connects%20to%20Multiple%20Destinations.yaml) | Execution, LateralMovement | - |
| [Uncommon Port for Organization](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Hunting%20Queries/Azure%20Firewall%20-%20Uncommon%20Port%20for%20Organization.yaml) | Defense Evasion, Exfiltration, CommandAndControl | [`AlertTimeSrcIpToPort`](../tables/alerttimesrciptoport.md) |
| [Uncommon Port to IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Hunting%20Queries/Azure%20Firewall%20-%20Uncommon%20Port%20to%20IP.yaml) | Exfiltration, CommandAndControl | [`AlertTimeSrcIpToPort`](../tables/alerttimesrciptoport.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Azure Firewall Workbook - Deployment Template](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Workbooks/Azure%20Firewall%20Workbook%20-%20Deployment%20Template.json) | - |
| [Azure Firewall Workbook - Structured Logs - Deployment Template](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Workbooks/Azure%20Firewall%20Workbook%20-%20Structured%20Logs%20-%20Deployment%20Template.json) | - |
| [AzureFirewallWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Workbooks/AzureFirewallWorkbook.json) | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [AzureFirewallWorkbook-StructuredLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Workbooks/AzureFirewallWorkbook-StructuredLogs.json) | [`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`AZFWDnsQuery`](../tables/azfwdnsquery.md)<br>[`AZFWIdpsSignature`](../tables/azfwidpssignature.md)<br>[`AZFWNatRule`](../tables/azfwnatrule.md)<br>[`AZFWNetworkRule`](../tables/azfwnetworkrule.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Azure Firewall - Add IP Address to Threat Intel Allow list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Playbooks/AzureFirewall-AddIPtoTIAllowList/azuredeploy.json) | This playbook allows the SOC to automatically response to Microsoft Sentinel incidents which include... | - |
| [Block IP - Azure Firewall IP groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Playbooks/AzureFirewall-BlockIP-addToIPGroup/azuredeploy.json) | This playbook allows blocking/allowing IPs in Azure Firewall. It allows to make changes on IP groups... | - |
| [Block IP - Azure Firewall IP groups - Entity trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Playbooks/AzureFirewall-BlockIP-addToIPGroup/entity-trigger/azuredeploy.json) | This playbook interacts with relevant stackholders, such incident response team, to approve blocking... | - |
| [BlockIP-Azure Firewall New Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Playbooks/AzureFirewall-BlockIP-addNewRule/azuredeploy.json) | This playbook uses the Azure Firewall connector to add IP Address to the Deny Network Rules collecti... | - |
| [BlockIP-Azure Firewall New Rule - Entity trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Playbooks/AzureFirewall-BlockIP-addNewRule/entity-trigger/azuredeploy.json) | This playbook uses the Azure Firewall connector to add IP Address to the Deny Network Rules collecti... | - |

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

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
