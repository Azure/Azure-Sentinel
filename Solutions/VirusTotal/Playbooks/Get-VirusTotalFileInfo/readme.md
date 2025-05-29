# Get-VirusTotalFileInfo
Author: Nicholas DiCola

This playbook processes each File Hash entity to query VirusTotal for detailed file information. For more details, visit the [VirusTotal File Info API documentation](https://developers.virustotal.com/v3.0/reference#file-info).

## Prerequisites
- Obtain a VirusTotal API key by registering with the VirusTotal community. [Register here](https://www.virustotal.com/gui/join-us)

## Quick Deployment
**Deploy with Incident Trigger** (Recommended)

Deploy this playbook and attach it to an **automation rule** to ensure it runs automatically whenever an incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVirusTotal%2FPlaybooks%2FGet-VirusTotalFileInfo%2Fincident-trigger%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVirusTotal%2FPlaybooks%2FGet-VirusTotalFileInfo%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with Alert Trigger**

Deploy this playbook to run manually on alerts or attach it to an **analytics rule** to execute automatically when an alert is generated.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVirusTotal%2FPlaybooks%2FGet-VirusTotalFileInfo%2Falert-trigger%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVirusTotal%2FPlaybooks%2FGet-VirusTotalFileInfo%2Falert-trigger%2Fazuredeploy.json)

## Post Deployment Instructions

**Assign the Microsoft Sentinel Responder Role to the Playbook**

This playbook uses a managed identity, which must have the Microsoft Sentinel Responder role assigned in the Sentinel instances to enable adding comments.

1. Select the Playbook resource.
2. In the left menu, click Identity.
3. Under Permissions, click Azure role assignments.
4. Click Add role assignment (Preview).
5. Use the drop-down lists to select the resource group that your *Sentinel Workspace* is in. If multiple workspaces are used in different resource groups consider selecting subscription as a scope instead.
6. In the Role drop-down list, select the role 'Microsoft Sentinel Responder'.
7. Click Save to assign the role.

## Screenshots
**Incident Trigger**
![Incident Trigger](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalFileInfo/incident-trigger/images/designerLight.png)

**Alert Trigger**
![Alert Trigger](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalFileInfo/alert-trigger/images/Get-VirusTotalFileInfo_alert.png)