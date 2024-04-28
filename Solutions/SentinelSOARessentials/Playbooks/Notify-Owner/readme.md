# Notify Incident Owner in Microsoft Teams
author: Lior Tamir

This playbook sends a Teams message to the new incident owner.

# Prerequisites

Microsoft Teams account that allows to send messages.

# Quick Deployment
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FNotify-Owner%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FNotify-Owner%2Fazuredeploy.json)
<br><br>

# Post-deployment
Add playbook as an action to the automation rule 
- Trigger = When incident is updated;  
- Condition = Owner changed.<br>


# Screenshots

**Playbook** <br>
![playbook screenshot](./images/designerLight.png)<br>

**Teams message** <br>
![teams notification](./images/ownerTeamsMessage.png)<br><br>
