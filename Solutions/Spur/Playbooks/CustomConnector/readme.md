# Spur Context API Logic Apps custom connector

## Table of Contents

1. [Overview](#overview)
2. [Actions supported by Spur Context API Custom Connector](#actions)
3. [Deployment](#deployment)
4. [Authentication](#Authentication)
5. [Grant Permissions](#grantpermissions)
6. [DCR and DCE Configuration](#dcrdceconfig)

<a name="overview"></a>

## Overview
The Spur Context API custom connector allows access to Spur Context API. Spur Context API provides hosted high-performance IP enrichment lookups of the highest-fidelity IP intelligence available. With pre-built integrations into the most common threat analysis platforms and services, Spur ensures that security teams can instantly leverage data to protect their environments from the latest evasion and obfuscation methods, such as VPNs, residential proxies, and bot automation.


<a name="actions"></a>

## Actions supported by SpyCloud Enterprise Custom Connector

| Action | Description |
| --------- | -------------- |
| **Get IP Context** | Returns intelligence and risk context for a given IP address. |
| **Get Tag Metadata** | Returns metadata information for a provider or service tag. |
| **Check API Token Status** | Retrieves the status of your API token, the number of queries remaining for the billing period, and service tier. |


<a name="deployment"></a>

## Deployment Instructions 

1. Deploy the custom connector by clicking on "Deploy to Azure" button. This will take you to deploy an ARM Template wizard.
2. Fill in the required parameters:
    * SpurConnectorName: The name for the custom connector (default: Spur-Context-Connector)
    * location: Azure region for deployment (default: resource group location)
    * subscriptionId: Azure subscription ID (default: current subscription ID)
    * resourceGroup: Resource group name (default: current resource group name)
    * workspaceName: Log Analytics workspace name (default: spur-log-workspace)
    * DCRName: Data Collection Rule name (default: Spur-DCR)
    * DCEName: Data Collection Endpoint name (default: Spur-DCE)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSpur%2FPlaybooks%2FCustomConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSpur%2FPlaybooks%2FCustomConnector%2Fazuredeploy.json)


<a name="authentication"></a>

## Authentication
Spur Context API Key

<a name="grantpermissions"></a>

## Grant Permissions for Log Ingestion API

After creating the App Registration, you need to grant it permissions to access the Data Collection Rule for log ingestion:

1. **Navigate to Data Collection Rules**
   - Go to Azure Portal
   - Search for "Data Collection Rules" in the search bar
   - Click on "Data Collection Rules" from the results

2. **Select your DCR**
   - Click on the Data Collection Rule you created during deployment (e.g., "Spur-DCR")

3. **Add Role Assignment**
   - Click on "Access control (IAM)" in the left menu
   - Click the "Add" button
   - Click on "Add role assignment"

4. **Configure Role Assignment**
   - **Role**: Search and select "Monitoring Metrics Publisher"
   - **Assign access to**: Select "User, group, or service principal"
   - **Select members**: Click to search and select your App Registration (e.g., "Spur-Context-Connector")
   - Click "Review + assign"
   - Click "Assign" to save the changes

5. **Wait for Propagation**
   - The role assignment may take up to 5 minutes to take effect
   - After the waiting period, you can proceed with making API calls

<a name="dcrdceconfig"></a>

## DCR and DCE Configuration

After granting permissions, you need to copy the DCR immutable ID and DCE log ingestion URL for log ingestion configuration later in the Playbooks:

1. **Copy DCR Immutable ID**
   - In the DCR overview page, look for the "JSON View" button in the top menu
   - Click on "JSON View" to see the JSON representation of the DCR
   - Copy the "immutableId" value (this is a unique identifier for the DCR)
   - Save this ID as it will be needed for log ingestion configuration in playbooks

2. **Copy DCE Log Ingestion URL**
   - Go to Azure Portal and search for "Data Collection Endpoints"
   - Click on "Data Collection Endpoints" from the results
   - Select the Data Collection Endpoint you created during deployment (e.g., "Spur-DCE")
   - In the overview page, copy the "Logs ingestion endpoint" URL
   - Save this URL as it will be needed for log ingestion configuration in playbooks

