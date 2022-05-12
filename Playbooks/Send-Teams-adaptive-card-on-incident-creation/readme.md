#  Send-Teams-adaptive-card-on-incident-creation

Author: Benjamin Kovacevic
<br><br>
This playbook will send Microsoft Teams Adaptive Card on incident creation, with the option to change the incident's severity and/or status.
 <br><br>

# Prerequisites

1. Get Teams Gorup ID and Teams Channel ID. (instructions available on - https://www.linkedin.com/pulse/3-ways-locate-microsoft-team-id-christopher-barber-/). It is possible to choose Teams group and channel after deployment as well.<br><br>

# Quick Deployment
**Deploy with incident trigger**

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSend-Teams-adaptive-card-on-incident-creation%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSend-Teams-adaptive-card-on-incident-creation%2Fazuredeploy.json)
<br><br>

# Post-deployment
1. Assign Microsoft Sentinel Responder role to the Playbook's Managed Identity
2. Authorize Microsoft Teams connector

<br><br>

## Screenshots
**Incident Trigger**<br>
![Incident Trigger](./images/incidentTrigger-light.png)<br>
![Incident Trigger](./images/incidentTrigger-dark.png)<br><br><br>
**Teams Notification**<br>
![Teams Notification](./images/Teams_Notification_dark.jpg)<br>
![Teams Notification](./images/Teams_Notification_light.jpg)<br><br><br>