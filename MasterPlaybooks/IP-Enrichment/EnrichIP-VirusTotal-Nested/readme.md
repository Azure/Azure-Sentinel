# VirusTotal-GetIPReport-Nested
# author: Nicholas DiCola

This playbook will take each IP entity and query VirusTotal for IP Address Report (https://developers.virustotal.com/v3.0/reference#ip-info). It will write the results to Log Analytics and add a comment to the incident.

## Quick Deployment
**Deploy with HTTP trigger** 



[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fmaster%2FMasterPlaybooks%2FIP-Enrichment%2FVirusTotal-IP-Enrichment%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2master%2FMasterPlaybooks%2FIP-Enrichment%2FVirusTotal-IP-Enrichment%2Fazuredeploy.json)

## Prerequisites

- You will need to register to Virus Total community for an API key

## Screenshots
**HTTP Trigger**<br>
![Incident Trigger](./Images/designerLight.png)<br>
