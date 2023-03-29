# Enrich-Sentinel-Incident-AlienVault-OTX

author: Brian Delaney

This playbook will enrich a Sentinel Incident with pulse information from AlienVault OTX.  If any pulses are found the Incident will also be tagged and the severity raised to High.

The following entity types will be enriched with this playbook:

- IP
- URL
- File hash
- DNS

## Quick Deployment

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FEnrich-Sentinel-Incident-AlienVault-OTX%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FEnrich-Sentinel-Incident-AlienVault-OTX%2Fazuredeploy.json)

## Prerequisites

- After deploying the the playbook you will need to grant the playbook's Managed Identity **Microsoft Sentinel Responder** (or greater) access to the resource group where Microsoft Sentinel is installed. This gives the Managed Identity the necessary permissions to add comments, tags, and change incident severity.
    
## Screenshots
![Designer](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Playbooks/Enrich-Sentinel-Incident-AlienVault-OTX/images/designerLight.jpg)

![Incident Comments](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Playbooks/Enrich-Sentinel-Incident-AlienVault-OTX/images/comment-light.jpg)
