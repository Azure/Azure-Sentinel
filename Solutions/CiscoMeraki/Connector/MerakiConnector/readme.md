# Cisco Meraki Logic Apps Custom Connector

![Meraki](logo.jpg)

# Overview
This custom connector connects to Cisco Meraki Dashboard API service endpoint and programmatically manages and monitors Meraki networks at scale.

# Authentication
*  API Key Authentication

# Actions supported by Cisco Meraki custom connector
| Component | Description |
| --------- | -------------- |
| **Get Organizations** |Gets organizations associated with the account.|
| **Get Networks** |Gets networks associated with the organization.|
| **Get Network Devices** | Gets the list of devices in a network. |
| **Get Network Clients** | Gets the list of clients that have used the network in the timespan. |
| **Get Network Appliance Content Filtering** | Gets content filtering settings for an MX network. |
| **Update Network Appliance Content Filtering** | Updates content filtering settings for an MX network.|
| **Get Network Appliance L3 firewall rules** | Gets the L3 firewall rules for an MX network.|
| **Update Network Appliance L3 firewall rule** | Updates a L3 firewall rule of an MX network. |
| **Get Network Appliance L7 firewall rules** | Gets the L7 firewall rules for an MX network. |
| **Update Network Appliance L7 firewall rule**| Updates a L7 firewall rule of an MX network. |
| **Get Network Client Policy**| Gets the policy assigned to a client on the network.|
| **Update Network Client Policy**| Updates the policy assigned to a client on the network.|
| **Get Network Group Policies**|Gets the list of group policies in a network.|
| **Get Network Group Policy**|Returns a group policy in a network.|


# Prerequisites for deploying Cisco Meraki Custom Connector
 * Cisco Meraki Dashboard API service endpoint should be known. (e.g. https://{CiscoMerakiDomain}/api/{versionNumber}) [Refer here](https://developer.cisco.com/meraki/api-v1/#!schema)


# Deploy Cisco Meraki Custom Connector
Click on the below button to deploy Cisco Meraki Custom Connector in your Azure subscription.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoMeraki%2FConnector%2FMerakiConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoMeraki%2FConnector%2FMerakiConnector%2Fazuredeploy.json)


# Deployment Instructions 
1. Deploy the Cisco Meraki custom connector by clicking on the "Deploy to Azure" button. This will take you to deploy an ARM Template wizard.
2. Fill in the required parameters for deploying Cisco Meraki custom connector.

## Deployment Parameters

| Parameter  | Description |
| ------------- | ------------- |
| **Custom Connector Name** | Enter the name of Cisco Meraki custom connector without spaces |
| **Service End Point** | Enter the Cisco Meraki Service End Point |