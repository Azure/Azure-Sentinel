# Cisco Firepower Logic Apps connector and playbook templates

![Cisco Firepower](./Images/CiscoFirepowerCustomConnector.png)<br>

## Table of Contents

1. [Overview](#overview)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [References](#references)


<a name="overview"></a>

# Overview
The Cisco Firepower Management Center (formerly FireSIGHT Management Center) is the administrative nerve center for select Cisco security products running on a number of different platforms. It provides complete and unified management of firewalls, application control, intrusion prevention, URL filtering, and advanced malware protection.<br><br>
This integration allows to automate response to Azure Sentinel incidents which contain IPs or URLs. It contains the basic connector component, with which you can create your own playbooks that interact with Cisco Firepower. It also contains 3 playbook templates, ready to quick use, 2 directly modify the Cisco Firepower configuration and 1 allows direct response on Cisco Firepower from Microsoft Teams.

<a name="prerequisites"></a>

# Prerequisites

### Authentication
In Cisco Firepower create a user and give it the appropriate user role in the domain you want the playbooks to modify network group objects in.
<br><br>

### Options to establish a connection with Cisco Firepower
The connector needs to be able to reach the Cisco Firepower REST API. A few options are:
1. Over the internet
1. Using Logic Apps gateway
1. Secure tunnel between your network and Azure

#### Over the internet
You can make the Cisco Firepower REST API available to the internet. You can use IP filtering to restrict access. To find
the IP addresses that need access, go to your Logic App instance and go to properties. The field 'Connector outgoing IP
addresses' contains the IP addresses Azure uses for your Logic App to call the connector. Logic Apps also needs to be
able to validate the SSL certificate used.

#### Using Logic Apps gateway
On a server in your network install the on-premises data gateway, see [Install on-premises data gateway for Azure Logic Apps](https://docs.microsoft.com/azure/logic-apps/logic-apps-gateway-install).
The server on which the data gateway is installed needs to be able to reach the Cisco Firepower REST API. Also the SSL
certificate used by the Cisco Firepower REST API needs to be able to be validated on the server, including the
certificate chain.
When deploying the Cisco Firepower connector choose the option via on-premises data gateway.
When using the connector you will be asked to select the data gateway you want to use.

#### Secure tunnel between your network and Azure
Create an Azure Virtual Network and connect it to your on-premise network using Azure VPN, for information see [Overview of partner VPN device configurations](https://docs.microsoft.com/azure/vpn-gateway/vpn-gateway-3rdparty-device-config-overview). When creating the Logic App make sure to select the option 'Associate with integration service environment'. When the Logic App is created you can connect it to the Azure Virtual Network. See (Connect to Azure virtual networks from Azure Logic Apps by using an integration service environment [Connect to Azure virtual networks from Azure Logic Apps by using an integration service environment (ISE)](https://docs.microsoft.com/azure/logic-apps/connect-virtual-network-vnet-isolated-environment)] and [Access to Azure Virtual Network resources from Azure Logic Apps by using integration service environments (ISEs)](https://docs.microsoft.com/azure/logic-apps/connect-virtual-network-vnet-isolated-environment-overview) for documentation.

<a name="deployment"></a>

# Deployment instructions

## 1. Deploy the custom connector

Custom connector should be deployed in the Resource Group where the playbooks that will include it are located. There are two options for the custom connector, one not connecting via on-premises data gateway and one connecting via on-premises data gateway.
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

<br><br>

## 2. Deploy the required playbook template (or create your own playbook from scratch)
This integration offers 3 playbook templates that blocks IP in 3 different methods. Each one has it's own documentation and quick deployment button:
* [Cisco Firepower - Add FQDN to a Network Group object](./CiscoFirepower-BlockFQDN-NetworkGroup#deployment-instructions)
* [Cisco Firepower - Add IP Addresses to a Network Group object](./CiscoFirepower-BlockIP-NetworkGroup#deployment-instructions)
* [Cisco Firepower - Add IP Addresses to a Network Group object with Teams](./CiscoFirepower-BlockIP-Teams#deployment-instructions)


<a name="references"></a>

## Learn more
*  [Firepower Management Center REST API Quick Start Guide, Version 6.7.0](https://www.cisco.com/c/en/us/td/docs/security/firepower/670/api/REST/firepower_management_center_rest_api_quick_start_guide_670.html)
*  [About the Firepower Management Center REST API](https://www.cisco.com/c/en/us/td/docs/security/firepower/670/api/REST/firepower_management_center_rest_api_quick_start_guide_670/About_The_Firepower_Management_Center_REST_API.html)
