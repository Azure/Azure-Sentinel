# Cisco Firepower Logic Apps connector

![Cisco Firepower](../Images/CiscoFirepowerCustomConnector.png)<br>
## Table of Contents

1. [Overview](#overview)
1. [Actions supported by Cisco Firepower custom connector](#actions)
1. [Deployment](#deployment)
1. [Authentication](#Authentication)

<a name="overview"></a>

## Overview
General info about this product and the core values of this integration. <br>


<a name="actions"></a>

## Actions supported by Cisco Firepower custom connector

| Component | Description |
| --------- | -------------- |
| **Generate token** | Use the configured basic authentication to start a session and get a token for other actions |
| **Refresh token** | After 30 minutes a generated token expires and can be renewed with this action |
| **Revoke access** | This action ends a session and revokes access for a token |
| **Retrieves list of all FQDN objects** | Action used to get all FQDN objects |
| **Retrieves the FQDN object associated with the specified ID** | Action used to get a specific FQDN object |
| **Create the FQDN object** | Action used to create a FQDN object |
| **MModifies the FQDN object associated with the specified ID** | Action used to modify a specific FQDN object |
| **Deletes the FQDN object associated with the specified ID** | Action used to delete a specific FQDN object |
| **Retrieves list of all network objects** | Action used to get all network objects |
| **Retrieves the network object associated with the specified ID** | Action used to get a specific network object |
| **Create the network object** | Action used to create a network object |
| **Modifies the network object associated with the specified ID** | Action used to modify a specific network object |
| **Deletes the network object associated with the specified ID** | Action used to delete a specific network object |
| **Retrieves list of all network group objects** | Action used to get all network group objects |
| **Retrieves the network group object associated with the specified ID** | Action used to get a specific network group object |
| **Create the network group object** | Action used to create a network group object |
| **Modifies the network group object associated with the specified ID** | Action used to modify a specific network group object |
| **Deletes the network group object associated with the specified ID** | Action used to delete a specific network group object |
| **Retrieves list of all range objects** | Action used to get all range objects |
| **Retrieves the range object associated with the specified ID** | Action used to get a specific range object |
| **Create the range object** | Action used to create a range object |
| **Modifies the range object associated with the specified ID** | Action used to modify a specific range object |
| **Deletes the range object associated with the specified ID** | Action used to delete a specific range object |


<a name="deployment"></a>

## Deployment instructions 
Prior using this custom connector, it should be deployed in the Resource Group where the playbooks that will include it are located. There are two options for the custom connector, one not connecting via on-premises data gateway and one connecting via on-premises data gateway.
<br>

### Connector **not** via on-premises data gateway
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Connector name: Please enter the custom connector(ex:Cisco Firepower connector)
    * Service Endpoint: The URL to the Cisco Firepower REST API



[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoFirepower%2FCustomConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoFirepower%2FCustomConnector%2Fazuredeploy.json)

### Connector via on-premises data gateway
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Connector name: Please enter the custom connector(ex:Cisco Firepower connector)
    * Service Endpoint: The URL to the Cisco Firepower REST API

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoFirepower%2FCustomConnector%2Fazuredeploy-gateway.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoFirepower%2FCustomConnector%2Fazuredeploy-gateway.json)


<a name="authentication"></a>

## Authentication
In Cisco Firepower create a user and give it the appropriate user role in the domain you want the playbooks to modify network group objects in.
