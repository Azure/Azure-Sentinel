# Send-basic-email

author: Benjamin Kovacevic

## Summary
This playbook sends an email with basic incident details (such as incident title, severity, tactics, and a direct link) when an incident is created in Microsoft Sentinel.

## Prerequisites
- A Microsoft 365 account to send email notifications (the user account will be used in the O365 connector for sending emails).

## Deployment instructions

1. To deploy the playbook, click the Deploy to Azure button below. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - Playbook Name
    - M365 Email Address

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FSend-basic-email%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FSend-basic-email%2Fazuredeploy.json)
<br><br>

## Post-deployment Instructions

### a. Authorize connections
Once deployment is complete, authorize each connection.

1. Open the Logic App in the Azure portal.
1. Click O365 connector resource 
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

> Note: The email will be sent from the user who creates the connection.

### b. Attach the playbook
1. In Microsoft Sentinel, configure an automation rule to trigger this playbook when an incident is created.
   - [Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)
2. Enable the playbook if it is disabled by default before assigning it to the automation rule.

## Screenshots

**Playbook**<br>
![Playbook](./images/LightPlaybook_Send-basic-email.png)
![Playbook](./images/DarkPlaybook_Send-basic-email.png)

**Email**<br>
![Email](./images/LightEmail_Send-basic-email.png)
![Email](./images/DarkEmail_Send-basic-email.png)