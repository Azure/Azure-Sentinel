# Forcepoint FUID Logic Apps Custom Connector

![forcepoint](/Playbooks/logo.jpg)

# Overview
This custom connector connects to Forcepoint FUID i.e Forcepoint User ID service in SMC (Security Management Center) and performs defined automated action on the Forcepoint NGFW (Next Generation Firewall).

# Authentication
*  No Authentication

# Action supported by Forcepoint FUID custom connector
| Component | Description |
| --------- | -------------- |
| **Get IP Address by Domain and Username** | Gets the IP address associated by Username.|


# Prerequisites for deploying Forcepoint FUID Custom Connector
 * Forcepoint FUID service endpoint should be known. (e.g.  https://forcepointdomain:PortNumber/})
 

# Deploy Forcepoint FUID Custom Connector
Click on the below button to deploy ForcepointFUID Custom Connector in your Azure subscription.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FForcepointNGFW%2FForcepointFUIDConnector%2Fazuredeploy.json) 
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FForcepointNGFW%2FForcepointFUIDConnector%2Fazuredeploy.json) 

# Deployment Instructions 
1. Deploy the Forcepoint FUID custom connector by clicking on the "Deploy to Azure" button. This will take you to deploy an ARM Template wizard.
2. Fill in the required parameters for deploying Forcepoint FUID custom connector.

## Deployment Parameters

| Parameter  | Description |
| ------------- | ------------- |
| **Custom Connector Name** | Enter the name of Forcepoint FUID custom connector without spaces. |
| **Service End Point** | Enter the Forcepoint FUID Service End Point. |




