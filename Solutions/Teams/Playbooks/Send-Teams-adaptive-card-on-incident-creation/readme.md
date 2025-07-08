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
3. Make the playbook selectable in Sentinel Automation Rules
After assigning the required role, the playbook might still appear unavailable (grayed out) when you try to attach it to an automation rule. This is due to Sentinel not having explicit access yet, even though the role was assigned.
To fix this:
    a. Go to **Microsoft Sentinel → Automation → Playbooks**
    b. Locate your playbook (e.g., `Send-Teams-adaptive-card-on-incident-creation`)
    c. Click the **three dots (...) → Manage playbook permissions**
    d. In the side panel that opens, select the **Resource Group** where your playbook is deployed
    e. Click **Apply**
This allows Sentinel to explicitly recognize the playbook's permissions. After completing this step, the playbook will become selectable when configuring automation rules.
Note: When selecting a playbook in the Automation rule, you may see a note saying:  
“**Only playbooks configured for the incident trigger can be selected. If a playbook appears unavailable, it means Microsoft Sentinel does not have explicit permissions to run it.**”  
Click **“Manage playbook permissions”** from there if needed.

## Screenshots
**Incident Trigger**
![Incident Trigger](./images/incidentTrigger-light.png)

![Incident Trigger](./images/incidentTrigger-dark.png)

**Teams Notification**
![Teams Notification](./images/Teams_Notification_dark.jpg)

![Teams Notification](./images/Teams_Notification_light.jpg)