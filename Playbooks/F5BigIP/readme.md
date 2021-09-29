# F5 BIG-IP Playbook Templates

![F5 BIG-IP](./Playbooks/logo.jpg)


## Table of Contents

1. [Overview](#overview)
1. [Deploy 4 Playbook templates](#deploy)
1. [Authentication](#authentication)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [References](#references)


<a name="overview">

# Overview

F5 BIG-IP Advanced Firewall Manager protects network against incoming threats, including complex DDOS attacks.


<a name="deploy">

# Deploy 4 Playbook templates
This package includes:
* Four playbook templates leverage F5 BIG-IP's APIs.

You can choose to deploy the whole package : all four playbook templates, or each one seperately from it's specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2Fraw.githubusercontent.com/dharmaAccenture/Azure-Sentinel/F5BigIP/Playbooks/F5BigIP/azuredeploy.json)  [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2Fraw.githubusercontent.com/dharmaAccenture/Azure-Sentinel/F5BigIP/Playbooks/F5BigIP/azuredeploy.json)  


# F5 BIG-IP documentation 

<a name="authentication">

# Authentication
API Key Authentication

<a name="prerequisites">

# Prerequisites for using and deploying 4 playbooks
1. F5 BIG-IP Host url should be known.
2. F5 BIG-IP firewall username and password should be known.
3. F5 BIG-IP environment should be accessible with the credentials.
4. A Firewall policy rule should be created for blocking of IP.
5. An address list should be created for blocking IP and the address list should be a part of Firewall policy rule.
7. URL Blocklist Category should be created for blocking URLs.

<a name="deployment">

# Deployment instructions 
1. Deploy the playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying custom connector and playbooks

| Parameter  | Description |
| ------------- | ------------- |
|**For Playbooks**|                 |
| **Block IP Playbook Name**|Enter the name of Block IP playbook without spaces |
| **Block URL Playbook Name**|Enter the name of Block URL playbook without spaces |
| **Enrichment IP Playbook Name**|Enter the name of Enrichment IP playbook without spaces |
| **IP Address List Name** | Enter IP Address List name to block IP |
| **URL Blocklist Category Name** | Enter URL Blocklist Category name to block URL |
|**For Base Playbook**|                             |
|**Base Playbook Name**|Enter name for F5 BIG-IP base Playbook without spaces.|
|**Host URL**|Enter value for F5 BIG-IP Host URL.|
|**Username**|Enter the F5 BIG-IP username.|
|**Password**|Enter the F5 BIG-IP password.|

<a name="postdeployment">

# Post-Deployment Instructions 
## Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky IP address, URL or Hosts. 
2. Configure the automation rules to trigger the playbooks.


<a name="references">

#  References

Base Playbook
* [BasePlaybook-F5 BIG-IP](/Playbooks/BasePlaybook-F5BigIP/readme.md)

Playbooks
* [BlockIP-F5 BIG-IP](/Playbooks/BlockIP-F5BigIP/readme.md)
* [BlockURL-F5 BIG-IP](/Playbooks/BlockURL-F5BigIP/readme.md)
* [EnrichmentIP-F5 Big-IP](/Playbooks/EnrichmentIP-F5BigIP/readme.md)


