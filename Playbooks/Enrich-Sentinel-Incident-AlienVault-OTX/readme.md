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

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FEnrich-Sentinel-Incident-AlienVault-OTX%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FEnrich-Sentinel-Incident-AlienVault-OTX%2Fazuredeploy.json)

## Prerequisites

- You will need to authorize the API Connection that is created by this deployment to update Azure Sentinel Incidents.  To do this locate the API connection in the resource group and under **Edit API connection** click **Authorize**
                                                                                                                                     
## Screenshot
![Designer](./images/designer.jpg)
