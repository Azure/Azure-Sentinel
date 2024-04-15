# Zscaler - Playbooks

<img src="./Images/Zscaler.png" width="200"><br>
## Table of Contents

1. [Overview](#overview)
1. [Playbooks](#playbooks)
1. [Prerequisites](prerequisites)
1. [Authentication](#Authentication)
1. [Deployment](#deployment)
1. [Postdeployment](#postdeployment)
1. [References](#references)

<a name="overview"></a>

## Overview
General info about this product and the core values of this integration. <br>


<a name="playbooks"></a>

## Zscaler Playbooks

| Action | Description |
| --------- | -------------- |
| **Add IP to category** | Add an IP to a Zscaler block category |
| **Add Url to catogory** | Add an URL to a Zscaler block category |
| **Get sandbox report for hash** | Get a Zscaler sandbox report for a file hash |
| **Url category lookup** | Lookup for Zscaler blocking categories for a given url |
| **Authentication** | Playbook to support the Zscaler authentication process |

<a name="prerequisites"></a>

## Prerequisites for using and deploying the playbooks
All playbook templates leverage the Zscaler API. To use the Zscaler capabilities, you need a Zscaler API key. To obtain a key, please refer this link: [API Developers Guide: Getting Started](https://help.zscaler.com/zia/api-getting-started)

<a name="authentication"></a>

## Authentication

The playbooks are using the Zscaler authentication process. The output of that process is a JSessionID which can be used to do other API actions. Refer this link for the authentication process: [Authenticate and create an API session](https://help.zscaler.com/zia/api-getting-started#CreateSession) To support the authentication process a [authentication playbook](../authentication/readme.md) is added. The authentication playbook can be used as linked ARM template or, if deployed, as embedded playbook in other playbooks. 


<a name="deployment"></a>

## Deployment 

This package includes:

* Four functional playbooks
* One playbook to support the Zscaler authentication process

You can choose to deploy all the playbooks in once using the buttons below. You can also choose to deploy one playbook with or without the authentication playbook. In that case, please refer to the readme in the playbook's folder.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FZscaler%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FZscaler%2Fazuredeploy.json" target="_blank">
   <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>    
</a>

<a name="postdeployment"></a>

## Post-Deployment instructions 

### a. Authorize connections
Once the deployment is completed, you will need to authorize each connection. There are connection for Azure KeyVault and Azure Sentinel. For each connection complete the following steps:
 1. Click edit API connection
 1. Fill in the necessary information
 1. Click Authorize
 1. Sign in
 1. Click Save

### b. Configurations in Azure Sentinel
For Azure Sentinel some additional configuration is needed:
1. Enable Azure Sentinel Analytics rules that create alerts and incidents which includes the relevant entities.
1. Configure automation rule(s) to trigger the playbooks.

### c. Optional: Change Zscaler Block Category
Both the "Add IP to category" and the "Add Url to category" are using a Zscaler block category to add IP addresses or urls to it. The default Zscaler block category is set during deployment. It can be changed in the playbook using the following steps:
1. Edit the playbook
1. Edit the 'Set Zscaler Category' action
1. Update the value to an existing Zscaler block category
1. Save the playbook

<a name="references"></a>

## Learn more
* <a href="https://help.zscaler.com/zia/api" target="_blank">Zscaler API</a>