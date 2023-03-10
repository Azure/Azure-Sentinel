# Zscaler - Add IP to category

<img src="../Images/Zscaler.png" width="200"><br>
## Table of Contents

1. [Summary](#overview)
1. [Prerequisites](prerequisites)
1. [Deployment](#deployment)
1. [postdeployment](postdeployment)
1. [Authentication](#Authentication)
1. [References](#references)

<a name="summary"></a>

## Summary

This folder contains 1 playbook: 
* Add IP to category: Add one or more IP addresses to an existing Zscaler category

![Playbook](../Images/Add-IP-To-Category.png)

The playbook is used to respond to an incident in Azure Sentinel and uses the Zscaler API. The playbook leverages the [authentication playbook](../authentication/readme.md).  The results of the scan are shown in the related Azure Sentinel Incident:

![Sentinel](../Images/Sentinel_Add_IP_To_Category.png)

<a name="Prerequisites"></a>

## Prerequisites

1. Playbook templates leverage the Zscaler API. To use the Zscaler capabilities, you need a Zscaler API key. Refer this link: [API Developers Guide: Getting Started](https://help.zscaler.com/zia/api-getting-started)

<a name="deployment"></a>

## Deployment instructions 

You can choose to deploy one ore more playbooks.

1. Deploy a playbook by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required parameters:
    * Resource group
    * Region
    * Playbook name
    * Storage account name (newly created storage account, which is used by the playbook)
    * Zscaler Admin Url
    * Zscaler Key
    * Zscaler Username
    * Zscaler Password
    * Zscaler block category (Name of an existing Zscaler block category)

### Deploy Add IP to category playbook

Deploy both the Authentication Playbook as well as the Add IP to category playbook:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FZscaler%2FAdd-IP-To-Category%2Fdeployboth.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FZscaler%2FAdd-IP-To-Category%2Fdeployboth.json)

<br/><br/>

Deploy only the Add IP to category playbook:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FZscaler%2FAdd-IP-To-Category%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FZscaler%2FAdd-IP-To-Category%2Fazuredeploy.json)

Please note: The [authentication playbook](../authentication/) is a mandatory prerequisite for this playbook and must be deployed first within the same resource group. The name of the authentication playbook is used as a parameter for the playbook.


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
The default Zscaler block category is configured during the deployment. It can be changed in the playbook using the following steps:
1. Edit the playbook
1. Edit the 'Set Zscaler Category' action
1. Update the value to an existing Zscaler block category
1. Save the playbook



<a name="references"></a>

## Learn more
* <a href="https://help.zscaler.com/zia/api" target="_blank">Zscaler API</a>