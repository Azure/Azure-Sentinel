# Notify-IncidentClosed
author: Benjamin Kovacevic

This playbook is utilizing new update trigger to notify person/group on Microsoft Teams/Outlook when incident is closed.

# Prerequisites

1. Email address to where notification will be sent to.
2. Microsoft Teams Team ID and Channel ID (Instructions to get IDs - https://www.linkedin.com/pulse/3-ways-locate-microsoft-team-id-christopher-barber-/) or choose Team and Channel after the deployment

# Quick Deployment
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FNotify-IncidentClosed%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FNotify-IncidentClosed%2Fazuredeploy.json)
<br><br>

# Post-deployment
1. Authorize Microsoft Teams and Microsoft Office 365 Outlook connectors
2. Choose Microsoft Teams Team and Channel where to send the adaptive card (only if Team ID and Channel ID were not added during the deployment)
3. Add playbook as an action to the automation rule 
- Trigger = When incident is updated;  
- Condition = Staus > Changed To > Closed;.<br>
**Automation rule example**<br>
![Automation Rule Example](./images/AutomationRuleExample.jpg)
4. If you want to receive notifications only on Microsoft Teams or only on Microsoft Office 365 Outlook, please remove unneeded connection. To remove, click on 3 dots on top right side of connector, and choose "Delete".<br><br>
**Delete connection example**<br>
![Delete Connection Example](./images/DeleteConnectionExample.jpg)

# Screenshots

**Playbook** <br>
![playbook screenshot](./images/playbookDark.png)<br>
![playbook screenshot](./images/playbookLight.png)<br><br>

**Teams** <br>
![teams notification](./images/TeamsNotification.jpg)<br><br>

**Outlook** <br>
![outlook notification](./images/OutlookNotification.jpg)<br><br>