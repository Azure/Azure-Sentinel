# Zero Networks Logic Apps connector

![Zero Networks](./Images/ZeroNetworks.png)<br>
## Table of Contents

1. [Overview](#overview)
1. [Actions supported by Zero Networks custom connector](#actions)
1. [Deployment](#deployment)
1. [Authentication](#Authentication)

<a name="overview"></a>

## Overview
General info about this product and the core values of this integration. <br>


<a name="actions"></a>

## Actions supported by Cisco ASA custom connector

| Component | Description |
| --------- | -------------- |
| **Search for an Asset** | Action used to get an asset by name |
| **Get AssetId by FQDN** | Action used to get the assetId for a machine using the FQDN |
| **Add asset to protection** | Action used to add an asset to learning or protection |
| **Remove asset from protection** | Action used to remove an asset from learning or protection |
| **Create Inbound Block rule** | Action used to create an inbound blocking rule |
| **Create Outbound Block rule** | Action used to create an outbound blocking rule |


<a name="deployment"></a>

## Deployment instructions 
Prior using this custom connector, it should be deployed in the Resource Group where the playbooks that will include it are located.
<br>

### Connector 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Connector name: Please enter the custom connector(ex:Cisco ASA connector)
    * Service Endpoint: The URL to the Zero Networks REST API

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZeroNetworks%2FPlaybooks%2FCustomConnector%2Fazuredeploy.json)

[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPSolutions%2FZeroNetworks%2FPlaybooks%2FCustomConnector%2Fazuredeploy.json)

<a name="authentication"></a>

## Authentication
In Zero Networks prtal, create an API token to use the REST API. Depending on the playbook the API token may need admin priviledges.
