# Create-IBMResilientIncident
author: Nicholas DiCola

This playbook will create an IBM Resilient incident from an Azure Sentinel incident.  It will also
add the Azure Sentinel Incident Entities as IBM Resilient Incident Artifacts.

## Custom Connector
This playbook uses a custom connector in Logic Apps. The template is set to not need a gateway, but if IBM Resilient is on-prem you can deploy a Logic Apps gateway and set the connector to use that gateway. You will need to update the connector and delete/re-add the API connection.

**If you want to deploy just the customer connector:**

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2Fazuredeploy-customconnector.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2Fazuredeploy-customconnector.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>


## Quick Deployment
**Deploy with incident trigger (and custom connector)** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2Fazuredeploy_incident.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2Fazuredeploy_incident.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

**Deploy with alert trigger (and custom connector)**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2Fazuredeploy_alert.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2Fazuredeploy_alert.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

## Prerequisites

None

## Screenshots

**Incident Trigger**
![Incident Trigger](./images/Create-IBMResilientIncident_incident.png)

**Alert Trigger**
![Alert Trigger](./images/Create-IBMResilientIncident_alert.png)