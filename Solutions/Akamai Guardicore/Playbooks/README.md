# Guardicore Incident Enrichment
author: Akamai Guardicore

This playbook automatically processes Microsoft Sentinel incidents to import and analyze Guardicore connection data related to incident entities. When a new incident is created, the playbook extracts IP addresses from the incident entities and uses Azure Functions to fetch relevant Guardicore connection data for enhanced security analysis.

## Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAkamai%20Guardicore%2FPlaybooks%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAkamai%20Guardicore%2FPlaybooks%2Fazuredeploy.json)

## Prerequisites
1. **Azure Function App**: Deploy the Azure Function App with the ProcessIncident function that handles Guardicore connection data processing
2. **Permissions**: The playbook's managed identity needs appropriate permissions to:
   - Access the Azure Function App
   - Read incident data from Microsoft Sentinel

## Screenshots
**Incident Trigger Workflow**<br>
![Incident Trigger](./images/Guardicore-ProcessIncidentConnections_incident.png)
