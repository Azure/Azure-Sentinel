# Create-IBMResilientIncident
author: Nicholas DiCola

This playbook will create an IBM Resilient incident from an Azure Sentinel incident.  It will also
add the Azure Sentinel Incident Entities as IBM Resilient Incident Artifacts.

## Custom Connector
This playbook uses a custom connector in Logic Apps. The template is set to not need a gateway, but if IBM Resilient is on-prem you can deploy a Logic Apps gateway and set the connector to use that gateway. You will need to update the connector and delete/re-add the API connection.

**If you want to deploy just the customer connector:**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2FcustomConnector%2Fazuredeployjson)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2FcustomConnector%2Fazuredeploy.json)


## Quick Deployment
**Deploy with incident trigger (and custom connector)** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with alert trigger (and custom connector)**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-IBMResilientIncident%2Falert-trigger%2Fazuredeploy.json)

## Prerequisites

None

## Screenshots

**Incident Trigger**<br>
![Incident Trigger](./incident-trigger/images/Create-IBMResilientIncident_incident.png)

**Alert Trigger**<br>
![Alert Trigger](./alert-trigger/images/Create-IBMResilientIncident_alert.png)