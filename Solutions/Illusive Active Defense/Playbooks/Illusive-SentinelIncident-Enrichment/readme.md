# Illusive Incident Enrichment Playbook

## Summary

Use this playbook to enrich Sentinel security incidents originating from Illusive with Illusive incident and forensics information. 
Illusive continues to enrich relevant Sentinel incidents as new events are detected. This is done using the Illusive API resource. 

![Azure Sentinel comment](./Images/SentinelIncidentCommentLight.png)

![Illusive Entities](./Images/IncidentTagsAndEntitiesLight.png)

**Plabook overview:**

![Playbook overview](./Images/DesignerOverviewLight.png)

![Playbook overview](./Images/DesignerOverviewDark.png)


### Prerequisites
1. Illusive custom connector needs to be deployed prior to the deployment of this playbook, in the same resource group and region. Relevant instructions can be found in the connector doc pages.

<a name="deployment-instructions"></a>
### Deployment instructions 
1. Deploy the playbook by clicking on "Depoly to Azure" button. This will take you to deplyoing an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoFirepower%2FCiscoFirepower-BlockFQDN-NetworkGroup%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoFirepower%2FCiscoFirepower-BlockFQDN-NetworkGroup%2Fazuredeploy.json)

2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here (ex:IllusiveSentinelIncidentEnrichment)

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Illusive (For authorizing the Illusive API connection, the username and password needs to be provided)

#### b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with URL Entity.
2. Configure the automation rules to trigger this playbook