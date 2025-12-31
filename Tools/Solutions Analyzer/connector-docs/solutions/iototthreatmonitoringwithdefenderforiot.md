# IoTOTThreatMonitoringwithDefenderforIoT

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Microsoft Defender for IoT](../connectors/iot.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`iotsecurityresources`](../tables/iotsecurityresources.md) | - | Workbooks |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | [Microsoft Defender for IoT](../connectors/iot.md) | Analytics, Playbooks |
| [`SecurityIncident`](../tables/securityincident.md) | - | Workbooks |

## Content Items

This solution includes **24 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 15 |
| Playbooks | 8 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Denial of Service (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTDenialofService.yaml) | High | InhibitResponseFunction | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Excessive Login Attempts (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTExcessiveLoginAttempts.yaml) | High | ImpairProcessControl | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Firmware Updates (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTFirmwareUpdates.yaml) | Medium | Persistence | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [High bandwidth in the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTHighBandwidth.yaml) | Low | Discovery | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Illegal Function Codes for ICS traffic (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTIllegalFunctionCodes.yaml) | Medium | ImpairProcessControl | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Internet Access (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTInternetAccess.yaml) | High | LateralMovement | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Multiple scans in the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTNetworkScanning.yaml) | High | Discovery | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [No traffic on Sensor Detected (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTINoSensorTrafficDetected.yaml) | High | InhibitResponseFunction | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [PLC Stop Command (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTPLCStopCommand.yaml) | Medium | DefenseEvasion | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [PLC unsecure key state (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTInsecurePLC.yaml) | Low | Execution | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Suspicious malware found in the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTMalware.yaml) | High | Impact | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Unauthorized DHCP configuration in the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTUnauthorizedNetworkConfiguration.yaml) | Medium | Discovery | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Unauthorized PLC changes (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTUnauthorizedPLCModifications.yaml) | Medium | Persistence | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Unauthorized device in the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTUnauthorizedDevice.yaml) | Medium | Discovery | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Unauthorized remote access to the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTUnauthorizedRemoteAccess.yaml) | Medium | InitialAccess | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [IoTOTThreatMonitoringwithDefenderforIoT](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Workbooks/IoTOTThreatMonitoringwithDefenderforIoT.json) | [`iotsecurityresources`](../tables/iotsecurityresources.md)<br>*Internal use:*<br>[`SecurityIncident`](../tables/securityincident.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [AD4IoT-AutoAlertStatusSync](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Playbooks/AutoAlertStatusSync/AutoAlertStatusSync.json) | This playbook updates alert statuses in Defender for IoT whenever a related alert in Microsoft Senti... | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) *(read)* |
| [AD4IoT-AutoCloseIncidents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Playbooks/AutoCloseIncidents/AutoCloseIncidents.json) | In some cases, maintenance activities generate alerts in Microsoft Sentinel which distracts the SOC ... | - |
| [AD4IoT-AutoTriageIncident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Playbooks/AutoTriageIncident/AutoTriageIncident.json) | SOC and OT engineers can stream their workflows using the playbook, which automatically updates the ... | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) *(read)* |
| [AD4IoT-CVEAutoWorkflow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Playbooks/CVEAutoWorkflow/CVEAutoWorkflow.json) | The playbook automates the SOC workflow by automatically enriching incident comments with the CVEs o... | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) *(read)* |
| [AD4IoT-MailByProductionLine](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Playbooks/MailBySensor/MailBySensor.json) | The following playbook will send mail to notify specific stake holders. One example can be in the ca... | - |
| [AD4IoT-NewAssetServiceNowTicket](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Playbooks/NewAssetServiceNowTicket/NewAssetServiceNowTicket.json) | Normally, the authorized entity to program a PLC is the Engineering Workstation, to program a PLC at... | - |
| [AD4IoT-SendEmailtoIoTOwner](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Playbooks/SendEmailToIoTOwner/SendEmailToIoTOwner.json) | The playbooks automate the SOC workflow by automatically emailing the incident details to the right ... | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) *(read)* |
| [Get-AD4IoTDeviceCVEs - Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Playbooks/GetD4IoTDeviceCVEs/GetD4IoTDeviceCVEs.json) | For each IoT device entity included in the alert, this playbook will get CVEs from the Azure Defende... | - |

## Additional Documentation

> 📄 *Source: [IoTOTThreatMonitoringwithDefenderforIoT/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/README.md)*

# Overview
There has been a long-standing split between ICS/SCADA (OT) and Corporate (IT) cybersecurity. This split was often driven by significant differences in technology/tooling. Microsoft Defender for IoT's integration with Microsoft Sentinel drives convergency by providing a single pane for coverage of both D4IOT (OT) and Microsoft Sentinel (IT) alerting. This solution includes Workbooks and Analytics rules providing a guide OT detection and Analysis.

## Try on Portal
You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FIoTOTThreatMonitoringwithDefenderforIoT%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FIoTOTThreatMonitoringwithDefenderforIoT%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Workbooks/Images/IoTOTThreatMonitoringwithDefenderforIoTBlack.png?raw=true)

## Getting Started
1️⃣ [Onboard Microsoft Defender for IoT](https://docs.microsoft.com/azure/defender-for-iot/device-builders/quickstart-onboard-iot-hub)
2️⃣ [Onboard Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard) 
3️⃣ [Enable Microsoft Defender for IoT Connector to Microsoft Sentinel](https://docs.microsoft.com/azure/defender-for-iot/organizations/how-to-configure-with-sentinel)
4️⃣ View the Workbook: Microsoft Sentinel > Workbooks > My Workbooks > IoT/OT Threat Monitoring with Defender for IoT > View
5️⃣ View the Analytics Rules: Navigate to Microsoft Sentinel > Analytics > Search "IOT"

## Workbook
The OT Threat Monitoring with Defender for IoT Workbook features OT filtering for Security Alerts, Incidents, Vulnerabilities and Asset Inventory. The workbook features a dynamic assessment of the MITRE ATT&CK for ICS matrix across your environment to analyze and respond to OT-based threats. This workbook is designed to enable SecOps Analysts, Security Engineers, and MSSPs to gain situational awareness for IT/OT security posture.

## Analytics Rules
### 1) Denial of Service (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect attacks that would prevent the use or proper operation of a DCS system including Denial of Service events.
### 2) Excessive Login Attempts (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect excessive login attempts that may indicate improper service configuration, human error, or malicious activity on the network such as a cyber threat attempting to manipulate the SCADA network.
### 3) Firmware Updates (Microsoft Defender for IoT)

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 29-01-2025                     | Corrected Entity Mappings structure of **Analytic Rules**			|
| 3.0.1       | 10-01-2025                     | Reverted Entity Mappings of **Analytic Rules** to earlier version  |
| 3.0.0       | 30-11-2023                     | Added new Entity Mapping to **Analytic Rules**                     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
