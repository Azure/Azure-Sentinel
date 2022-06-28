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

Palo Alto XDR playbook is used in Alert triaging and executing the automated response towards issue, and it also helps in evidence collection.

<a name="prerequisites">

# Prerequisites 
- This playbook uses Microsoft Teams connector and VirusTotal connector to enrich the investigation, so you will have to set up your account if not already to use the Microsoft ID to authorize the teams connector. You will also have to visit this VT site create your free account and once you do, you shall get a  standard free public API Key, this key will be required to authorize the connector. Reference link - https://www.virustotal.com/
- To do so all you have to go to API connections blade after deployment and click on properties and supply the your Virus Total Public free API Key to Authorize the connector.

  
<a name="deployall">

# Deploy the Playbook
- You may copy the JSON file and deploy the custom template in azure with variables of own choice or do single click deploy from below tab.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FPalo%2520Alto%2520-%2520XDR%2520(Cortex)%2FPlaybook%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FPalo%2520Alto%2520-%2520XDR%2520(Cortex)%2FPlaybook%2Fazuredeploy.json)


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
* For Log analytics workspace action you will have to configure the desired query which your analysts should receive prior to their investigation as a kick starter.



<a name="references">

# References
https://docs.microsoft.com/power-automate/create-adaptive-cards-teams 
