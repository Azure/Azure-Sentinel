# Palo Alto Cortx XDR Logic App and Playbook Template

## Table of Contents

1. [Overview](#overview)
1. [Prerequisites](#prerequisites)
1. [Deploy Palo Alot XDR playbook](#deployall) 
1. [Deployment Instructions](#instructions)
1. [Post-Deployment Instructions](#postdeployment)
1. [References](#references)

<a name="overview">

# Overview 

Palo Alto XDR playbook is used in Alert triaging and executing the automatd response towards issue, and it also helps in evidence collection.

<a name="prerequisites">

# Prerequisites 
- This playbook uses Teams connector and VirusTotal external connector to enrich the investigation, so please configure your account if not already and keep the authorized API key handy.


<a name="deployall">

# Deploy the Playbook
- You may copy the JSON file and deploy the custom template in azure with variables of own choice or do single click deploy from below tab.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fc03vikas%2FAzure-Sentinel-1%2Fc03vikas%2FPlaybooks%2FPaloAltoXDR%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fc03vikas%2FAzure-Sentinel-1%2Fc03vikas%2FPlaybooks%2FPaloAltoXDR%2Fazuredeploy.json)


<a name="instructions">

# Deployment Instructions 
- Deploy the Palo Alto XDR Playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
- Fill in the required parameters and then proceed with review and create.


<a name="postdeployment">

# Post Deployment Instructions 
## Authorize Connections
* Once deployment is complete, you will need to authorize each connection.
  - Click the Teams connection resource
  - Click edit API connection
  - Click Authorize
  - Sign in
  - Click Save
  - Repeat steps for other connections as well.
* In Logic App designer authorize Teams channel connection as well, for playbooks posting adaptive cards.
* For VirusTotal connector please enter the valid API key to activate the connector.
* For Log analytics workspace action you will have to configure the desired query which your analysts should received prior to their investigation as a kick starter.



<a name="references">

# References
https://docs.microsoft.com/en-us/power-automate/create-adaptive-cards-teams 
