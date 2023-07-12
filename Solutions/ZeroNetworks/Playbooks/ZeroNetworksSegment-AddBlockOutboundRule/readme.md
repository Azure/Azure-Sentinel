# Zero Networks Segment - Add Block Outbound Rule

## Summary

This playbook allows blocking an IP outbound from protected assets in Zero Networks Segment.  

When a new Sentinel incident is created, this playbook gets triggered and performs below actions
1. For the IPs, we add them to a new outbound block rule in Segment.
2. A comment is added to Microsoft Sentinel incident.

**Playbook overview:**
![playbook overview](./images/designerDark.png)


### Prerequisites
1. Zero Networks custom connector needs to be deployed prior to the deployment of this playbook, in the same resource group and region. Relevant instructions can be found in the connector doc page.

### Deployment instructions 
1. Deploy the playbook by clicking on "Depoly to Azure" button. This will take you to deplyoing an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZeroNetworks%2FPlaybooks%2FZeroNetworksSegment-AddBlockOutboundRule%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZeroNetworks%2FPlaybooks%2FZeroNetworksSegment-AddBlockOutboundRule%2Fazuredeploy.json)

2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here (ex:ZNSegment-AddBlockOutboundRule)
    * Connector name : Enter the name of the Zero Networks custom connector (default value:ZeroNetworksConnector)

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
1. In Microsoft Sentinel, analytical rules should be configured to trigger an incident with IP Entity.
2. Configure the automation rules to trigger this playbook
