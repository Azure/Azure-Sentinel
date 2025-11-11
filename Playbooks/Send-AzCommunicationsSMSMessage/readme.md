# Send-AzCommunicationsSMSMessage
author: Nicholas DiCola

This playbook will send an SMS Message using Azure Communications Services to alert of new incidents.

## Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSend-AzCommunicationsSMSMessage%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSend-AzCommunicationsSMSMessage%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSend-AzCommunicationsSMSMessage%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSend-AzCommunicationsSMSMessage%2Falert-trigger%2Fazuredeploy.json)

## Prerequisites
- The ARM template will create the playbook, Azure Communication Service and connections, you will need to add a telephone number to the ACS resource.  Then update the playbook with the source phone number.
![Telephone Number](./images/ACSTeleNumber.png)

## Screenshots
**Incident Trigger**<br>  
![Incident Trigger](./incident-trigger/images/Send-AzCommunicationsSMSMessage_incident.png)  
**Alert Trigger**<br>  
![Alert Trigger](./alert-trigger/images/Send-AzCommunicationsSMSMessage_alert.png)  
