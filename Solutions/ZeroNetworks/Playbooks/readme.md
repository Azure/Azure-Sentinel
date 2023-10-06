# Zero Networks Logic Apps connector and playbook templates

![Zero Networks](./Images/ZeroNetworks.png)<br>

## Table of Contents

1. [Overview](#overview)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [References](#references)


<a name="overview"></a>

# Overview
This integration allows automated response to Microsoft Sentinel incidents. It contains the basic connector component, with which you can create your own playbooks that interact with Zero Networks.  It also contains 3 playbook templates, ready to quick use, that allow direct response.

<a name="prerequisites"></a>

# Prerequisites

### Authentication
The custom connector supports **api authentication**. In Zero Networks Segment create an api token. Depending on the playbook used the the token may need Admin privleges.

<br><br>
### Options to establish a connection with Zero Networks Segment
The connector needs to be able to reach the Zero Networks Segment REST API over the internet.

<a name="deployment"></a>

# Deployment instructions

## 1. Deploy the custom connector

Custom connector should be deployed in the Resource Group where the playbooks that will include it are located.
<br>

1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Connector name: Please enter the custom connector(ex:ZNSegmentConnector)
    * Uri: The URL to the REST API (you should not have to change this)

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZeroNetworks%2FPlaybooks%2FCustomConnector%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZeroNetworks%2FPlaybooks%2FCustomConnector%2Fazuredeploy.json" target="_blank">
   <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>    
</a>
<br><br>

## 2. Deploy the required playbook template (or create your own playbook from scratch)
This integration offers 3 playbook templates. Each one has it's own documentation an quick deployment button:
* [ZeroNetworksSegment-EnrichIncident](./ZeroNetworksSegment-EnrichIncident#deployment-instructions)
* [ZeroNetworksSegment-AddAssettoProtection](./ZeroNetworksSegment-AddAssettoProtection#deployment-instructions)
* [ZeroNetworksSegment-AddBlockOutboundRule](./ZeroNetworksSegment-AddBlockOutboundRule#deployment-instructions)
