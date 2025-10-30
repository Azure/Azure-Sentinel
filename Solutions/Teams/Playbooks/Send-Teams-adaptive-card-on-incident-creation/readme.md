#  Send-Teams-adaptive-card-on-incident-creation

Author: Benjamin Kovacevic

This playbook will send Microsoft Teams Adaptive Card on incident creation, with the option to change the incident's severity and/or status.


# Prerequisites

1. Get Teams Group ID and Teams Channel ID. (instructions available on - https://www.linkedin.com/pulse/3-ways-locate-microsoft-team-id-christopher-barber-/). It is possible to choose Teams group and channel after deployment as well.

# Quick Deployment
**Deploy with incident trigger**

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTeams%2FPlaybooks%2FSend-Teams-adaptive-card-on-incident-creation%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTeams%2FPlaybooks%2FSend-Teams-adaptive-card-on-incident-creation%2Fazuredeploy.json)


# Post-deployment
1. Assign Microsoft Sentinel Responder role to the Playbook's Managed Identity
2. Authorize Microsoft Teams connector
# If the Playbook is Grayed Out, Follow These Steps
1. Navigate to `Microsoft Sentinel → Settings → Settings `
2. Scroll down to the **Playbook permissions** section
3. Click the **Configure permissions** button
4. In the **Manage permissions** side panel:
   - Under the **Browse** tab, search and select the **Resource Group** that contains your Logic App Playbook
5. Click **Apply**
6. Return to your **Automation Rule** and try adding the playbook again – it should now be selectable (no longer grayed out)
## Screenshots
**Incident Trigger**
![Incident Trigger](./images/incidentTrigger-light.png)

![Incident Trigger](./images/incidentTrigger-dark.png)

**Teams Notification**
![Teams Notification](./images/Teams_Notification_dark.jpg)

![Teams Notification](./images/Teams_Notification_light.jpg)