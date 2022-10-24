# Zero Networks Segment - Enrich Incident

## Summary

This playbook will take each Host entity and get its Asset status from Zero Network Segment. The playbook will then write a comment to the Microsoft Sentinel incident with a table of assets and protection statuses.

When a new Microsoft Sentinel incident is created,this playbook gets triggered and performs below actions
1. For the hosts, we get their asset satus from the REST API.
2. A comment is added to Microsoft Sentinel incident.

**Playbook overview:**

![playbook overview](./images/designerLight.png)



### Prerequisites
1. Zero Networks custom connector needs to be deployed prior to the deployment of this playbook, in the same resource group and region. Relevant instructions can be found in the connector doc page.

### Deployment instructions 
1. Deploy the playbook by clicking on "Depoly to Azure" button. This will take you to deplyoing an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FZeroNetworks%2FZeroNetworksSegment-EnrichIncident%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FZeroNetworks%2FZeroNetworksSegment-EnrichIncident%2Fazuredeploy.json)

2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here (ex:ZeroNetworksSegment-EnrichIncident)
    * Zero Networks Connector name : Enter the name of the Zero Networks custom connector (default value:ZeroNetworksConnector)

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Microsoft Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Zero Networks 

#### c. Configurations in Microsoft Sentinel
1. In Microsoft Sentinel, analytical rules should be configured to trigger an incident with Hosts Entity.
2. Configure the automation rules to trigger this playbook
