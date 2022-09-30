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
This alert leverages Defender for IoT to detect unauthorized firmware updates that may indicate malicious activity on the network such as a cyber threat that attempts to manipulate PLC firmware to compromise PLC function.
### 4) High Bandwidth in the network (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect an unusually high bandwidth which may be an indication of a new service/process or malicious activity on the network. An example scenario is a cyber threat attempting to manipulate the SCADA network.
### 5) Illegal Function Codes for ICS traffic (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect Illegal function codes in SCADA equipment indicating improper application configuration or malicious activity such using illegal values within a protocol to exploit a PLC vulnerability.
### 6) PLC unsecure key state (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect PLC operating mode changes indicating the PLC is potentially insecure. If the PLC is compromised, devices that interact with it may be impacted. This may affect overall system security and safety.
### 7) Internet Access (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect an OT device communicating with Internet which is possibly an indication of improper configuration of an application or malicious activity on the network.
### 8) Suspicious malware found in the network (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect IoT/OT malware found on the network indicating possible attempts to compromise production systems.
### 9) Multiple scans in the network (Microsoft Defender for IoT)
his alert leverages Defender for IoT to detect multiple scans on the network indicating new devices, functionality, application misconfiguration, or malicious reconnaissance activity on the network.
### 10) PLC Stop Command (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect PLC stop commands which could indicate improper configuration or malicious activity on the network such as a threat manipulating PLC programming to affect the function of the network.
### 11) Unauthorized device in the network (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect a new device indicating a legitimate device recently installed on the network or an indication of malicious activity such as a cyber threat attempting to manipulate the SCADA network.
### 12) Unauthorized DHCP configuration in the network (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect an unauthorized DHCP configuration indicating a possible unauthorized device configuration.
### 13) Unauthorized PLC changes (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect unauthorized changes to PLC ladder logic code indicating new functionality in the PLC, improper configuration of an application, or malicious activity on the network.
### 14) Unauthorized remote access to the network (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect unauthorized remote access to network devices, if another device on the network is compromised, target devices can be accessed remotely, increasing the attack surface.
### 15) No traffic on sensor detected (Microsoft Defender for IoT)
This alert leverages Defender for IoT to detect that a sensor can no longer detect the network traffic, which indicates that the system is potentially insecure.

## Playbooks
### 1) Auto Close Incidents
In some cases, maintenance activities generate alerts in Sentinel which distracts the SOC team from handling the real problems. This playbook allows to input the time period in which the maintenance is expected and the assets IP (Excel file can be found). The playbook requires a watchlist which includes all the IP addresses of the assets on which alerts will handled automatically. This playbook parses explicitly the IoT device entity fields. For more information, see [AD4IoT-AutoCloseIncidents](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AD4IoT-AutoCloseIncidents)
### 2) Mail by Production Line
The following playbook will send mail to notify specific stake holders. One example can be in the case of specific security team per product line or per physical location. This playbook requires a watchlist which maps between the sensors name and the mail addresses of the alerts stockholders. For more information, see [AD4IoT-MailbyProductionLine](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AD4IoT-MailbyProductionLine)
### 3) New Asset ServiceNow Ticket
Normally, the authorized entity to program a PLC is the Engineering Workstation, to program a PLC attackers might create a new Engineering Workstation to create malicious programing. The following playbook will open a ticket in ServiceNow each time a new Engineering Workstation is detected. This playbook parses explicitly the IoT device entity fields. For more information, see [AD4IoT-NewAssetServiceNowTicket](https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/AD4IoT-NewAssetServiceNowTicket/readme.md)
### 4) Update alert statuses in Defender for IoT
This playbook updates alert statuses in Defender for IoT whenever a related alert in Microsoft Sentinel has a Status update.
### 5) Send Email to IoT/OT Device Owner
The playbooks automate the SOC workflow by automatically emailing the incident details to the right IoT/OT device owner (based on Defender for IoT dafinition) and allowing him to respond by email. The incident is automatically updated based on the email response from the device owner.
### 6) Triage incidents involving Crown Jewels devices automatically
SOC and OT engineers can stream their workflows using the playbook, which automatically updates the incident severity based on the devices involved in the incident and their importance.
### 7) Incident with active CVEs: Auto Workflow 
The playbook automates the SOC workflow by automatically enriching incident comments with the CVEs of the involved devices based on Defender for IoT data.
An automated triage is performed if the CVE is critical, and the asset owner is automatically notified by email
