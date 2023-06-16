# SNOW-CreateAndUpdateIncident
author: Benjamin Kovacevic

This playbook will create or update incident in ServiceNow (SNOW). When incident is created, playbook will run and create incident in SNOW. When incident is updated, playbook will run and add update to comment section. When incident is closed, playbook will run and close incident in SNOW.

# Prerequisites

We will need following data to make Jira connector:<br>
1. SNOW instance (ex. xyz.service-now.com)
2. Username
3. Password
![SNOW connector requirements](./images/SNOW-connector-requirementsDark.png)<br>

# Quick Deployment
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FServicenow%2FPlaybooks%2FSNOW-CreateAndUpdateIncident%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FServicenow%2FPlaybooks%2FSNOW-CreateAndUpdateIncident%2Fazuredeploy.json)
<br><br>

# Post-deployment
1. Authorize SNOW connector
2. Assign Microsoft Sentinel Responder role to playbook's managed identity. To do so, choose Identity blade under Settings of the Logic App.
3. Add playbook as an action to the automation rule, ex.:
- Trigger = When incident is updated;  
- Condition = Staus > Changed To > Closed;.<br>
**Automation Rule Example**<br>
![Automation Rule Example](./images/AutomationRuleExampleDark.jpg)
**Automation Rule Condition Example**<br>
![Automation Rule Condition Example](./images/AutomationRuleExample2Dark.jpg)

# Screenshots

**Playbook** <br>
![playbook screenshot](./images/SnowPlaybookDark.jpg)<br>
![playbook screenshot](./images/SnowPlaybookLight.jpg)<br><br>

**SNOW New Incident** <br>
![snow screenshot new](./images/SNOWNewIncident.jpg)<br><br>

**SNOW Update Incident** <br>
![snow screenshot update](./images/SNOWTagAdded.jpg)<br>

**SNOW Incident closed** <br>
![snow screenshot closed](./images/SNOWIncidentClosed.jpg)<br><br>