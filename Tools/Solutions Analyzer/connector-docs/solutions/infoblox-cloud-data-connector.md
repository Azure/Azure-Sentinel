# Infoblox Cloud Data Connector

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Infoblox |
| **Support Tier** | Partner |
| **Support Link** | [https://support.infoblox.com/](https://support.infoblox.com/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Infoblox Cloud Data Connector via Legacy Agent](../connectors/infobloxclouddataconnector.md)
- [[Deprecated] Infoblox Cloud Data Connector via AMA](../connectors/infobloxclouddataconnectorama.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Infoblox Cloud Data Connector via AMA](../connectors/infobloxclouddataconnectorama.md), [[Deprecated] Infoblox Cloud Data Connector via Legacy Agent](../connectors/infobloxclouddataconnector.md) | Analytics, Workbooks |
| [`Syslog`](../tables/syslog.md) | - | Analytics |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | - | Analytics |

## Content Items

This solution includes **21 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 11 |
| Analytic Rules | 8 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Infoblox - Data Exfiltration Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Analytic%20Rules/Infoblox-DataExfiltrationAttack.yaml) | Medium | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Infoblox - High Threat Level Query Not Blocked Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Analytic%20Rules/Infoblox-HighThreatLevelQueryNotBlockedDetected.yaml) | Medium | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Infoblox - Many High Threat Level Queries From Single Host Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Analytic%20Rules/Infoblox-ManyHighThreatLevelQueriesFromSingleHostDetected.yaml) | Medium | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Infoblox - Many High Threat Level Single Query Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Analytic%20Rules/Infoblox-ManyHighThreatLevelSingleQueryDetected.yaml) | Medium | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Infoblox - Many NXDOMAIN DNS Responses Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Analytic%20Rules/Infoblox-ManyNXDOMAINDNSResponsesDetected.yaml) | Medium | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Infoblox - TI - CommonSecurityLog Match Found - MalwareC2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Analytic%20Rules/Infoblox-TI-CommonSecurityLogMatchFound-MalwareC2.yaml) | Medium | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [Infoblox - TI - InfobloxCDC Match Found - Lookalike Domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Analytic%20Rules/Infoblox-TI-InfobloxCDCMatchFound-LookalikeDomains.yaml) | Medium | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [Infoblox - TI - Syslog Match Found - URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Analytic%20Rules/Infoblox-TI-SyslogMatchFound-URL.yaml) | Medium | Impact | [`Syslog`](../tables/syslog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [InfobloxCDCB1TDWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Workbooks/InfobloxCDCB1TDWorkbook.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Infoblox Import AISCOMM Weekly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Playbooks/Infoblox-Import-AISCOMM-Weekly/azuredeploy.json) | Leverages the Infoblox TIDE API to automatically import threat indicators into the ThreatIntelligenc... | - |
| [Infoblox Import Emails Weekly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Playbooks/Infoblox-Import-Emails-Weekly/azuredeploy.json) | Leverages the Infoblox TIDE API to automatically import threat indicators into the ThreatIntelligenc... | - |
| [Infoblox Import Hashes Weekly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Playbooks/Infoblox-Import-Hashes-Weekly/azuredeploy.json) | Leverages the Infoblox TIDE API to automatically import threat indicators into the ThreatIntelligenc... | - |
| [Infoblox Import Hosts Daily Lookalike Domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Playbooks/Infoblox-Import-Hosts-Daily-LookalikeDomains/azuredeploy.json) | Leverages the Infoblox TIDE API to automatically import threat indicators into the ThreatIntelligenc... | - |
| [Infoblox Import Hosts Daily MalwareC2DGA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Playbooks/Infoblox-Import-Hosts-Daily-MalwareC2DGA/azuredeploy.json) | Leverages the Infoblox TIDE API to automatically import threat indicators into the ThreatIntelligenc... | - |
| [Infoblox Import Hosts Daily Phishing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Playbooks/Infoblox-Import-Hosts-Daily-Phishing/azuredeploy.json) | Leverages the Infoblox TIDE API to automatically import threat indicators into the ThreatIntelligenc... | - |
| [Infoblox Import Hosts Hourly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Playbooks/Infoblox-Import-Hosts-Hourly/azuredeploy.json) | Leverages the Infoblox TIDE API to automatically import threat indicators into the ThreatIntelligenc... | - |
| [Infoblox Import IPs Hourly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Playbooks/Infoblox-Import-IPs-Hourly/azuredeploy.json) | Leverages the Infoblox TIDE API to automatically import threat indicators into the ThreatIntelligenc... | - |
| [Infoblox Import URLs Hourly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Playbooks/Infoblox-Import-URLs-Hourly/azuredeploy.json) | Leverages the Infoblox TIDE API to automatically import threat indicators into the ThreatIntelligenc... | - |
| [Infoblox Incident Enrichment Domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Playbooks/Infoblox-Incident-Enrichment-Domains/azuredeploy.json) | Leverages the Infoblox TIDE API to enrich Microsoft Sentinel incidents with detailed TIDE data. This... | - |
| [Infoblox Incident Send Email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Playbooks/Infoblox-Incident-Send-Email/azuredeploy.json) | Sends a detailed email when an incident occurs. Optionally enriches an applicable entity within the ... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [InfobloxCDC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Parsers/InfobloxCDC.yaml) | - | - |

## Release Notes

| **Version**   | **Date Modified**              | **Change History**                                                     |
|---------------|--------------------------------|------------------------------------------------------------------------|
| 3.0.5         | 06-01-2025                     | Removed Deprecated **Data Connector**                                  |
| 3.0.4         | 12-07-2024                     | Deprecating data connectors                                            |
| 3.0.3         | 30-04-2024                     | Updated package for parser issue fix while reinstall   |
| 3.0.2         | 05-03-2024                     | Updated InfobloxCDC parser to manually parse with extract() rather than dynamically due to slowness   |
| 3.0.1         | 11-09-2023                     | Addition of new Infoblox Cloud Data Connector AMA **Data Connector**   |
| 3.0.0         | 01-08-2023                     | Updated Infoblox logo, **Analytic Rules** Optimization updates. 5 new rules,**Playbooks** 11 new playbooks|
| 2.0.10        | 01-06-2023                     | Bug fixes, Documentation updates                                       |
| 1.0.0         | 01-04-2021                     | Initial Solution Release                                               |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
