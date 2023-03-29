# GeoIP-GetFromIpAndTagIncident-Nested
author: Nicholas DiCola

This playbook will take the IP address entities from the Incident and query a Geo-IP API to geo-locate the IP Address.  It will write the City and Country to a tag on the Incident and more details to the comments.

## Custom Connector
This playbook uses a custom connector in Logic Apps.

**If you want to deploy just the customer connector:**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fmaster%2FMasterPlaybooks%2FIP-Enrichment%2FGeoIP-IP-Enrichment%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fmaster%2FMasterPlaybooks%2FIP-Enrichment%2FGeoIP-IP-Enrichment%2Fazuredeploy.json)

## Quick Deployment



[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-GeoFromIpAndTagIncident%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-GeoFromIpAndTagIncident%2Fincident-trigger%2Fazuredeploy.json)

## Prerequisites
None

## Screenshots

![HTTP Trigger](./Images/Get-GeoFromIpAndTagIncident.png)<br>
