# MicrosoftDefenderForEndpoint

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Microsoft Defender for Endpoint](../connectors/microsoftdefenderadvancedthreatprotection.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`DeviceProcessEvents`](../tables/deviceprocessevents.md) | - | Hunting |

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | [Microsoft Defender for Endpoint](../connectors/microsoftdefenderadvancedthreatprotection.md) | Analytics |

## Content Items

This solution includes **27 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 22 |
| Hunting Queries | 2 |
| Parsers | 2 |
| Analytic Rules | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Aqua Blizzard AV hits - Feb 2022](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Analytic%20Rules/AquaBlizzardAVHits.yaml) | High | Persistence | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Probable AdFind Recon Tool Usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Hunting%20Queries/MDE_Usage.yaml) | Discovery | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [SUNBURST suspicious SolarWinds child processes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Hunting%20Queries/MDE_Process-IOCs.yaml) | Execution, Persistence | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Isolate MDE Machine - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Isolate-MDEMachine/Isolate-MDEMachine-alert-trigger/azuredeploy.json) | This playbook will isolate (full) the machine in Microsoft Defender for Endpoint. It is triggered by... | - |
| [Isolate MDE Machine using entity trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Isolate-MDEMachine/Isolate-MDE-Machine-entity-trigger/azuredeploy.json) | This playbook will isolate Microsoft Defender for Endpoint MDE device using entity trigger. It will ... | - |
| [Isolate endpoint - MDE - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Isolate-MDEMachine/Isolate-MDEMachine-incident-trigger/azuredeploy.json) | This playbook will isolate (full) the machine in Microsoft Defender for Endpoint. It is triggered by... | - |
| [Restrict MDE App Execution - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEAppExecution/Restrict-MDEAppExecution-alert-trigger/azuredeploy.json) | This playbook will restrict app execution on the machine in Microsoft Defender for Endpoint. | - |
| [Restrict MDE App Execution - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEAppExecution/Restrict-MDEAppExecution-incident-trigger/azuredeploy.json) | This playbook will restrict app execution on the machine in Microsoft Defender for Endpoint. | - |
| [Restrict MDE Domain - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEDomain/Restrict-MDEDomain-alert-trigger/azuredeploy.json) | This play book will take DNS entities and generate alert and block threat indicators for each domain... | - |
| [Restrict MDE Domain - Entity Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEDomain/Restrict-MDEDomain-entity-trigger/azuredeploy.json) | This playbook will take the triggering entity and generate an alert and block threat indicator for t... | - |
| [Restrict MDE Domain - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEDomain/Restrict-MDEDomain-incident-trigger/azuredeploy.json) | This play book will take DNS entities and generate alert and block threat indicators for each domain... | - |
| [Restrict MDE FileHash - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEFileHash/Restrict-MDEFileHash-alert-trigger/azuredeploy.json) | This playbook will take FileHash entities and generate alert and block threat indicators for each fi... | - |
| [Restrict MDE FileHash - Entity Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEFileHash/Restrict-MDEFileHash-entity-trigger/azuredeploy.json) | This playbook will take the triggering FileHash entity and generate an alert and block threat indica... | - |
| [Restrict MDE FileHash - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEFileHash/Restrict-MDEFileHash-incident-trigger/azuredeploy.json) | This playbook will take FileHash entities and generate alert and block threat indicators for each fi... | - |
| [Restrict MDE Ip Address - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEIPAddress/Restrict-MDEIPAddress-alert-trigger/azuredeploy.json) | This playbook will take IP entities and generate alert and block threat indicators for each IP in MD... | - |
| [Restrict MDE Ip Address - Entity Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEIPAddress/Restrict-MDEIPAddress-entity-trigger/azuredeploy.json) | This playbook will and generate alert and block threat indicators for the IP entity in MDE for 90 da... | - |
| [Restrict MDE Ip Address - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEIPAddress/Restrict-MDEIPAddress-incident-trigger/azuredeploy.json) | This playbook will take IP entities and generate alert and block threat indicators for each IP in MD... | - |
| [Restrict MDE URL - Entity Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEUrl/Restrict-MDEUrl-entity-trigger/azuredeploy.json) | This playbook will take the triggering entity and generate an alert and block threat indicator for t... | - |
| [Restrict MDE Url - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEUrl/Restrict-MDEUrl-alert-trigger/azuredeploy.json) | This playbook will take Url entities and generate alert and block threat indicators for each IP in M... | - |
| [Restrict MDE Url - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Restrict-MDEUrl/Restrict-MDEUrl-incident-trigger/azuredeploy.json) | This playbook will take Url entities and generate alert and block threat indicators for each IP in M... | - |
| [Run MDE Antivirus - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Run-MDEAntivirus/Run-MDEAntivirus-alert-trigger/azuredeploy.json) | This playbook will run a antivirus (full) scan on the machine in Microsoft Defender for Endpoint. It... | - |
| [Run MDE Antivirus - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Run-MDEAntivirus/Run-MDEAntivirus-incident-trigger/azuredeploy.json) | This playbook will run a antivirus (full) scan on the machine in Microsoft Defender for Endpoint. It... | - |
| [Unisolate MDE Machine - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Unisolate-MDEMachine/Unisolate-MDEMachine-alert-trigger/azuredeploy.json) | This playbook will release a machine from isolation in Microsoft Defender for Endpoint. It is trigge... | - |
| [Unisolate MDE Machine - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Unisolate-MDEMachine/Unisolate-MDEMachine-incident-trigger/azuredeploy.json) | This playbook will release a machine from isolation in Microsoft Defender for Endpoint. It is trigge... | - |
| [Unisolate MDE Machine using entity trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Playbooks/Unisolate-MDEMachine/Unisolate-MDE-Machine-entity-trigger/azuredeploy.json) | This playbook will unisolate Microsoft Defender for Endpoint (MDE) device using entity trigger. | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [AssignedIPAddress](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Parsers/AssignedIPAddress.yaml) | - | - |
| [Devicefromip](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Parsers/Devicefromip.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.6       | 24-09-2025                     | Updated MDE **Playbooks** Instructions to use Microsoft Graph SDK  |
| 3.0.5       | 06-08-2025                     | Updated MDE **Playbooks** with newer logic  |
| 3.0.4       | 07-04-2025                     | Updated ConnectivityCriteria Type in **Data Connector**.				   |
| 3.0.3       | 26-07-2024                     | Updated **Analytical Rule** for missing TTP |
| 3.0.2       | 08-07-2024                     | Corrected UI changes in **Playbook's** metadata  |
| 3.0.1       | 24-11-2023                     | Entities has been mapped for **Playbooks**  |
| 3.0.0       | 17-07-2023                     | Initial Solution Release                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
