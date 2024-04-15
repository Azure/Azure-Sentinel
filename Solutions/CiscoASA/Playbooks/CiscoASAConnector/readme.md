# Cisco ASA Logic Apps connector

![Cisco ASA](../Images/CiscoASACustomConnector.png)<br>
## Table of Contents

1. [Overview](#overview)
1. [Actions supported by Cisco ASA custom connector](#actions)
1. [Deployment](#deployment)
1. [Authentication](#Authentication)

<a name="overview"></a>

## Overview
General info about this product and the core values of this integration. <br>


<a name="actions"></a>

## Actions supported by Cisco ASA custom connector

| Component | Description |
| --------- | -------------- |
| **Fetch inbound access groups** | Action used to get the inbound action groups |
| **Fetch an inbound access group by interface name** | Action used to get the inbound action group for an interface |
| **Fetch inbound access rules on an interface** | Action used to get the inbound access rules for an interface |
| **Create an inbound access rule on an interface** | Action used to create an inbound access rule on an interface |
| **Fetch an inbound access rule on an interface** | Action used to get an inbound access rule for an interface |
| **Remove an inbound access rule on an interface** | Action used to remove an inbound access rule for an interface |
| **Get the connection statistics of the device** | Action used to get the connection statistics of the device,  |
| **Get the ipaddress details of the device** | Action used to get the connection statistics for an interface on the device |
| **Fetch ACEs on an interface** | Action used to get access control entries for an interface |
| **Add a new ACE on an interface** | Action used to add a bew access control entry to an interface |
| **Fetch an ACE on an interface** | Action used to get an access control entry for an interface |
| **Delete an ACE** | Action used to delete an access control entry for an interface |
| **Fetch network object groups** | Action used to get network object groups |
| **Add a new network object group** | Action used to add a new network object group |
| **Fetch a network object group** | Action used to get a network object group |
| **Patch members of a network object group** | Action used to edit the members of a network object group |
| **Fetch network objects** | Action used to get network objects |
| **Add a new network object** | Action used to add a new network object |
| **Fetch a network object** | Action used to get a network object |


<a name="deployment"></a>

## Deployment instructions 
Prior using this custom connector, it should be deployed in the Resource Group where the playbooks that will include it are located. There are two options for the custom connector, one not connecting via on-premises data gateway and one connecting via on-premises data gateway.
<br>

### Connector **not** via on-premises data gateway
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Connector name: Please enter the custom connector(ex:Cisco ASA connector)
    * Service Endpoint: The URL to the Cisco ASA REST API

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoASA%2FCustomConnector%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoASA%2FCustomConnector%2Fazuredeploy.json" target="_blank">
   <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>    
</a>

### Connector via on-premises data gateway
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Connector name: Please enter the custom connector(ex:Cisco ASA connector)
    * Service Endpoint: The URL to the Cisco ASA REST API

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoASA%2FCustomConnector%2Fazuredeploy-gateway.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoASA%2FCustomConnector%2Fazuredeploy-gateway.json" target="_blank">
   <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>    
</a>

<a name="authentication"></a>

## Authentication
In Cisco ASA create a local user and allow it to use the REST API. Depending on the playbook used the user needs to be able to add members to a network object group or create access control entries, by default that requires privilege level 15.
