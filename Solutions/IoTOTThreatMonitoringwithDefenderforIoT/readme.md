# Overview
There has been a long-standing split between SCADA (OT) and Corporate (IT) cybersecurity. This split was often driven by significant differences in technology/tooling. Azure Defender for IoT's integration with Azure Sentinel drives convergency by providing a single pane for coverage of both D4IOT (OT) and Azure Sentinel (IT) alerting. 
This solution includes (1) Workbook, (13) Analytics rules, and (3) Playbooks providing a guide OT/IoT Detection, Analysis, and Response. The solution features IoT/OT filtering for Security Alerts, Incidents, and Asset Inventory. The workbook features a dynamic assessment of the MITRE ATT&CK for ICS matrix across your environment to analyze and respond to IoT/OT-based threats. This solution is designed to enable SecOps Analysts, Security Engineers, and MSSPs to gain situational awareness for IT/OT security posture. This solution is enhanced when integrated with complimentary Microsoft Offerings such as ✳️ Azure Defender for IoT, ✳️ Azure Sentinel, and ✳️ Azure Security Center. This workbook augments staffing through automation, artificial intelligence, machine learning, query/alerting generation and visualizations.

# Getting Started
1)  [Onboard Azure Defender for IoT](https://docs.microsoft.com/azure/defender-for-iot/device-builders/quickstart-onboard-iot-hub)
2)  [Onboard Azure Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard) 
3)  [Enable Azure Defender for IoT Connector to Azure Sentinel](https://docs.microsoft.com/azure/defender-for-iot/organizations/how-to-configure-with-sentinel)
4)  View the Workbook: Navigate to Azure Sentinel > Workbooks > My Workbooks > IoT/OT Threat Monitoring with Defender for IoT > View 
5)  View the Analytics Rules: Navigate to Azure Sentinel > Analytics > Search "IOT"
6)  View the Playbooks: Navigate to Azure Sentinel> Automation > Playbooks > Search "IOT"

# Playbooks
## 1) AutoCloseIncidents
### Overview 
In some cases, maintenance activities generate alerts in Sentinel which distracts the SOC team from handling the real problems, the playbook allows to input the time period in which the maintenance is expected and the assets IP (Excel file can be found). The playbook requires a watchlist which includes all the IP addresses of the assets on which alerts will handled automatically. This playbook parses explicitly the IOT device entity fields. For more information, see [AD4IoT-AutoCloseIncidents](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AD4IoT-AutoCloseIncidents)
## 2) MailbyProductionLine
### Overview
The following playbook will send mail to notify specific stake holders.<br>
One example can be in the case of specific security team per product line or per physical location. The playbook requires a watchlist which maps between the sensors name and the mail addresses of the alerts stockholders. For more information, see [AD4IoT-MailbyProductionLine](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AD4IoT-MailbyProductionLine)
## 3) NewAssetServiceNowTicket
### Overview
Normally, the authorized entity to program a PLC is the Engineering Workstation, to program a PLC attackers might create a new Engineering Workstation to create malicious programing. The following playbook will open a ticket in ServiceNow each time a new Engineering Workstation is detected. This playbook parses explicitly the IOT device entity fields. For more information, see [AD4IoT-NewAssetServiceNowTicket](https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/AD4IoT-NewAssetServiceNowTicket/readme.md)
