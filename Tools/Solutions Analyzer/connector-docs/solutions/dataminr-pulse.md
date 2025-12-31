# Dataminr Pulse

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Dataminr Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.dataminr.com/dataminr-support#support](https://www.dataminr.com/dataminr-support#support) |
| **Categories** | domains |
| **First Published** | 2023-04-12 |
| **Last Updated** | 2023-04-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Dataminr Pulse Alerts Data Connector](../connectors/dataminrpulsealerts.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`DataminrPulse_Alerts_CL`](../tables/dataminrpulse-alerts-cl.md) | [Dataminr Pulse Alerts Data Connector](../connectors/dataminrpulsealerts.md) | Analytics, Workbooks |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Watchlists | 5 |
| Parsers | 2 |
| Analytic Rules | 1 |
| Workbooks | 1 |
| Playbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Dataminr - urgent alerts detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Analytic%20Rules/DataminrSentinelAlerts.yaml) | Medium | Persistence | [`DataminrPulse_Alerts_CL`](../tables/dataminrpulse-alerts-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [DataminrPulseAlerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Workbooks/DataminrPulseAlerts.json) | [`DataminrPulse_Alerts_CL`](../tables/dataminrpulse-alerts-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [DataminrPulseAlertEnrichment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Playbooks/DataminrPulseAlertEnrichment/azuredeploy.json) | This playbook provides an end-to-end example of how alert enrichment works. This will extract the IP... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [DataminrPulseAlerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Parsers/DataminrPulseAlerts.yaml) | - | - |
| [DataminrPulseCyberAlerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Parsers/DataminrPulseCyberAlerts.yaml) | - | - |

### Watchlists

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [DataminrPulseAsset](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Watchlists/DataminrPulseAsset.json) | - | - |
| [DataminrPulseVulnerableDomain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Watchlists/DataminrPulseVulnerableDomain.json) | - | - |
| [DataminrPulseVulnerableHash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Watchlists/DataminrPulseVulnerableHash.json) | - | - |
| [DataminrPulseVulnerableIp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Watchlists/DataminrPulseVulnerableIp.json) | - | - |
| [DataminrPulseVulnerableMalware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Watchlists/DataminrPulseVulnerableMalware.json) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.5       |     16-09-2025                 | Updated Python version to 3.12 and Added Log Ingestion API support             |
| 3.0.4       |     12-09-2025                 | Added support for Azure GovCloud |
| 3.0.3       |     03-05-2024                 | Repackaged for parser issue fix on reinstall |
| 3.0.2       |     14-12-2023                 | Updated **Data Connector** code                    |
| 3.0.1       |     06-12-2023                 | Updated steps in **DataConnector** UI and **README.md** file.                     |
| 3.0.0       |     14-07-2023                 | Initial Solution Release                     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
