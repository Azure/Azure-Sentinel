# SpyCloud Enterprise Protection Logic Apps custom connector

![SpyCloud Enterprise](images/logo.png)<br>
## Table of Contents

1. [Overview](#overview)
2. [Actions supported by SpyCloud Enterprise Protection Custom Connector](#actions)
3. [Deployment](#deployment)
4. [Authentication](#Authentication)

<a name="overview"></a>

## Overview
The SpyCloud Enterprise Protection connector allows access to SpyCloud’s Enterprise Protection API. The connector is organized around the SpyCloud Enterprise Protection API endpoints. JSON is returned by all API responses, including those with errors. <br>


<a name="actions"></a>

## Actions supported by SpyCloud Enterprise Custom Connector

| Action | Description |
| --------- | -------------- |
| **List or Query the Breach Catalogs** | List or Query the Breach Catalog |
| **Get Catalog** | Retrieve Breach Catalog Information by ID |
| **Get Breach Data by Domain Search** | Get Breach Data by Domain Search |
| **Get Breach Data by Email Search** | Get Breach Data by Email Search |
| **Get Breach Data by IP Address** | Get Breach Data by IP Address |
| **Get Breach Data by Password Search** | Get Breach Data by Password Search |
| **Get Breach Data by Username Search** | Get Breach Data by Username Search  |
| **Get Breach Data for Entire Watchlist** | Get Breach Data for Entire Watchlist |
| **Get Compass Devices List** | Get Compass Devices List |
| **Get Compass Devices Data** | Get Compass Devices Data |
| **Get Compass Applications Data** | Get Compass Applications Data |
| **Get Compass Data** | Get Compass Data |


<a name="deployment"></a>

## Deployment Instructions 
Prior to using this custom connector, it should be deployed in the resource group where the playbooks that will include it are located.
<br>

1. Deploy the custom connector by clicking on "Deploy to Azure" button. This will take you to deploy an ARM Template wizard.
2. Fill in the required parameters:
    * Connector name: Please enter the custom connector(ex:SpyCloudEnterprise)
    * Service Endpoint: The URL to the SpyCloud Enterprise REST API

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSpyCloud%20Enterprise%20Protection%2FCustom%20Connector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSpyCloud%20Enterprise%20Protection%2FCustom%20Connector%2Fazuredeploy.json)


<a name="authentication"></a>

## Authentication
SpyCloud Enterprise API Key
