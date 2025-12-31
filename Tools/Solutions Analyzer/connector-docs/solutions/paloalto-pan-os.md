# PaloAlto-PAN-OS

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-08-09 |
| **Last Updated** | 2021-09-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Palo Alto Networks (Firewall) via Legacy Agent](../connectors/paloaltonetworks.md)
- [[Deprecated] Palo Alto Networks (Firewall) via AMA](../connectors/paloaltonetworksama.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Palo Alto Networks (Firewall) via AMA](../connectors/paloaltonetworksama.md), [[Deprecated] Palo Alto Networks (Firewall) via Legacy Agent](../connectors/paloaltonetworks.md) | Analytics, Hunting, Workbooks |
| [`covidIndicators`](../tables/covidindicators.md) | - | Analytics |
| [`triggerBody`](../tables/triggerbody.md) | - | Playbooks |

## Content Items

This solution includes **16 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 7 |
| Analytic Rules | 5 |
| Hunting Queries | 2 |
| Workbooks | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Microsoft COVID-19 file hash indicator matches](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Analytic%20Rules/FileHashEntity_Covid19_CommonSecurityLog.yaml) | Medium | Execution | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`covidIndicators`](../tables/covidindicators.md) |
| [Palo Alto - possible internal to external port scanning](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Analytic%20Rules/PaloAlto-PortScanning.yaml) | Low | Discovery | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`fluentbit_CL`](../tables/fluentbit-cl.md) |
| [Palo Alto - possible nmap scan on with top 100 option](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Analytic%20Rules/PaloAlto-Top100_NmapScan.yaml) | Medium | Reconnaissance | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Palo Alto - potential beaconing detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Analytic%20Rules/PaloAlto-NetworkBeaconing.yaml) | Low | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`fluentbit_CL`](../tables/fluentbit-cl.md) |
| [Palo Alto Threat signatures from Unusual IP addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Analytic%20Rules/PaloAlto-UnusualThreatSignatures.yaml) | Medium | Discovery, Exfiltration, CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`fluentbit_CL`](../tables/fluentbit-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Palo Alto - high-risk ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Hunting%20Queries/PaloAlto-HighRiskPorts.yaml) | InitialAccess, Discovery | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`fluentbit_CL`](../tables/fluentbit-cl.md) |
| [Palo Alto - potential beaconing detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Hunting%20Queries/Palo%20Alto%20-%20potential%20beaconing%20detected.yaml) | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`fluentbit_CL`](../tables/fluentbit-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [PaloAltoNetworkThreat](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Workbooks/PaloAltoNetworkThreat.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAltoOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Workbooks/PaloAltoOverview.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Block IP - Palo Alto PAN-OS - Entity trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Playbooks/PaloAltoPlaybooks/PaloAlto-PAN-OS-BlockIP-EntityTrigger/azuredeploy.json) | This playbook interacts with relevant stakeholders, such incident response team, to approve blocking... | - |
| [Get System Info - Palo Alto PAN-OS XML API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Playbooks/PaloAltoPlaybooks/PaloAlto-PAN-OS-GetSystemInfo/azuredeploy.json) | This playbook allows us to get System Info of a Palo Alto device for a Microsoft Sentinel alert. | - |
| [Get Threat PCAP - Palo Alto PAN-OS XML API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Playbooks/PaloAltoPlaybooks/PaloAlto-PAN-OS-GetThreatPCAP/azuredeploy.json) | This playbook allows us to get a threat PCAP for a given PCAP ID. | [`triggerBody`](../tables/triggerbody.md) *(read)* |
| [PaloAlto-PAN-OS-BlockIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Playbooks/PaloAltoPlaybooks/PaloAlto-PAN-OS-BlockIP/azuredeploy.json) | This playbook allows blocking/unblocking IPs in PaloAlto, using **Address Object Groups**. This allo... | - |
| [PaloAlto-PAN-OS-BlockURL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Playbooks/PaloAltoPlaybooks/PaloAlto-PAN-OS-BlockURL/azuredeploy.json) | This playbook allows blocking/unblocking URLs in PaloAlto, using **predefined address group**. This ... | - |
| [PaloAlto-PAN-OS-BlockURL-EntityTrigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Playbooks/PaloAltoPlaybooks/PaloAlto-PAN-OS-BlockURL-EntityTrigger/azuredeploy.json) | This playbook allows blocking/unblocking URLs in PaloAlto, using **predefined address group**. This ... | - |
| [PaloAlto-PAN-OS-GetURLCategoryInfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Playbooks/PaloAltoPlaybooks/PaloAlto-PAN-OS-GetURLCategoryInfo/azuredeploy.json) | When a new sentinal incident is created, this playbook gets triggered and performs below actions: | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.10      | 13-11-2025                     |   Adding New Detection Rule for Nmap Top 100 Port Scan             |
| 3.0.9       | 06-01-2025                     |   Removing Custom Entity mappings from **Analytic Rule**           |
| 3.0.8       | 15-11-2024                     |   Corrected **Data Connector** count in CreateUiDefinition         |
| 3.0.7 	  | 11-11-2024 					   |   Removed Deprecated **Data Connector**                            |
|             |                                |   Updated **Analytic Rule** for entity mappings                    |
| 3.0.6 	  | 12-07-2024 					   |   Deprecated **Data Connector** 									|
| 3.0.5       | 30-04-2024                     |   Updated the **Data Connector** to fix conectivity criteria query |
| 3.0.4       | 16-04-2024                     |   Fixed existing rule for sites with private IP addresses other than 10/8 |
| 3.0.3       | 11-04-2024                     |   Enhanced the existing **Workbook** as per requirement            |
| 3.0.2       | 12-02-2024                     |   Addition of new PaloAlto-PAN-OS AMA **Data Connector**           |
| 3.0.1       | 22-01-2024                     |   Added subTechniques in Template                                  |
| 3.0.0       | 12-12-2023                     |   Fixed **Playbooks** issue                                        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
