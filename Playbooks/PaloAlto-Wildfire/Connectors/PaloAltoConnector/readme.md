# PaloAlto PAN-OS Logic Apps Custom Connector

![PAN-OS](./PAN-OS_CustomConnector.png)

# Overview
This custom connector connects to PAN-OS service end point and performs defined automated actions on the PAN-OS firewall.

# Authentication
*  API Key authentication

# Actions supported by PaloAlto PAN-OS custom connector
| Component | Description |
| --------- | -------------- |
| **List security rules** | Retrieves a list of all security rules within a specified location in the firewall|
| **Create a security policy rule** | Creates a new security policy rule in the firewall|
| **Update a security policy rule** | References/Unreferences the address object in the security rule as a source or a destination member |
| **List custom url categories** | Retrieves a list of all URL filtering category information within a specified location in the firewall|
| **List address objects** | Retrieves a list of all address objects within a specified location in the firewall|
| **Create an address object** |Creates an address object depending on type : IP address or URL address|
| **Updates an address object** |Updates an address object depending on type : IP address or URL address|
| **List address groups** | Retrieves a list of all address object groups within a specified location in the firewall|
| **Create an address object group** | Creates a new address object group in the firewall|
| **Updates an address object group** | Updates an address object group in the firewall |
| **List URL filtering security profiles** | Retrieves a list of all URL filtering security profiles in the firewall|
| **Update URL filtering security profiles** | Updates URL filtering security profiles in the firewall|

# Prerequisites for deploying PAN-OS Custom Connector
1. PAN-OS service end point should be known. (e.g.  https://{paloaltonetworkdomain})


# Deploy PAN-OS Custom Connector
Click on the below button to deploy PAN-OS Custom Connector in your Azure subscription.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPaloAlto-Wildfire%2FConnectores%2FPaloAltoConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPaloAlto-Wildfire%2FConnectores%2FPaloAltoConnector%2Fazuredeploy.json)

# Deployment Instructions 
1. Deploy the PAN-OS custom connector by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying PAN-OS custom connector.

## Deployment Parameters

| Parameter  | Description |
| ------------- | ------------- |
| **Custom Connector Name** | Enter the name of PAN-OS custom connector |
| **Service End Point** | Enter the PAN-OS Service End Point |