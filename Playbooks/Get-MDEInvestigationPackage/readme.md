# Get-MDEInvestigationPackage
author: Nicholas DiCola

This playbook will call the collect investigation package in MDE.  It will then loop until thats complete, once complete it will add a comment to the incident and post a message in teams with the URL to download the package.

## Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-MDEInvestigationPackage%2Fazuredeploy_incident.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-MDEInvestigationPackage%2Fazuredeploy_incident.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-MDEInvestigationPackage%2Fazuredeploy_alert.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-MDEInvestigationPackage%2Fazuredeploy_alert.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>


## Prerequisites

- You will grant permissions for the managed identity to the Graph Application. There is a good blog [here](https://laurakokkarinen.com/authenticating-to-azure-ad-protected-apis-with-managed-identity-no-key-vault-required/). You will need to grant at least "ChatMessage.Send" for the managedid in the Graph Application.
- [This](https://www.linkedin.com/pulse/3-ways-locate-microsoft-team-id-christopher-barber-/) blog shows some simple methods to get the Team Id.  You will need the Team Id and Channel Id.

## Screenshots
**Incident Trigger**
![Incident Trigger](./images/Get-MDEInvestigationPackage_incident.png)

**Alert Trigger**
![Alert Trigger](./images/Get-MDEInvestigationPackage_alert.png)