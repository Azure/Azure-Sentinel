# TenableIO

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Tenable |
| **Support Tier** | Partner |
| **Support Link** | [https://www.tenable.com/support/technical-support](https://www.tenable.com/support/technical-support) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableIO](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableIO) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Tenable.io Vulnerability Management](../connectors/tenableioapi.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Tenable_IO_Assets_CL`](../tables/tenable-io-assets-cl.md) | [Tenable.io Vulnerability Management](../connectors/tenableioapi.md) | Playbooks |
| [`Tenable_IO_Vuln_CL`](../tables/tenable-io-vuln-cl.md) | [Tenable.io Vulnerability Management](../connectors/tenableioapi.md) | Playbooks |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 3 |
| Parsers | 2 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Tenable.io - Enrich incident with asset info](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableIO/Playbooks/Playbooks/Tenable-EnrichIncidentWithAssetsInfo/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | [`Tenable_IO_Assets_CL`](../tables/tenable-io-assets-cl.md) *(read)* |
| [Tenable.io - Enrich incident with vulnerability info](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableIO/Playbooks/Playbooks/Tenable-EnrichIncidentWithVulnInfo/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | [`Tenable_IO_Vuln_CL`](../tables/tenable-io-vuln-cl.md) *(read)* |
| [Tenable.io - Launch Scan](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableIO/Playbooks/Playbooks/Tenable-LaunchScan/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [TenableIOAssets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableIO/Parsers/TenableIOAssets.yaml) | - | - |
| [TenableIOVulnerabilities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableIO/Parsers/TenableIOVulnerabilities.yaml) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
