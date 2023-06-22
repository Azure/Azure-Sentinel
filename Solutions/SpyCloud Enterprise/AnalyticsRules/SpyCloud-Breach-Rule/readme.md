# SpyCloud Enterprise Breach Analytic Rule

![SpyCloud Enterprise](images/logo.png)

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment](#deployment)
4. [Post Deployment Steps](#postdeployment)


<a name="overview">

## Overview
This analytic rule will monitor the SpyCloud watchlist custom log table. This rule will trigger an incident when a record with severity 2o is found. All the details of the breach record are saved in entities and custom details of the rule, which can be used in the playbooks for further investigation.


<a name="prerequisites">

## Prerequisites
- SpyCloud Enterprise Monitor Watchlist Data playbook needs to be deployed, in the same resource group and region. Relevant instructions can be found on the playbook document page.
- SpyCloud Enterprise Monitor Watchlist Data playbook needs to be succesfully completed and it should create the custom log table in the Log Analytics Workaspace.
- SpyCloud Enterprise Breach playbook needs to be deployed before the deployment of this analytic rule, in the same resource group and region. Relevant instructions can be found on the playbook document page.

<a name="deployment">

## Deployment Instructions
- Deploy the analytic rule by clicking on the "Deploy to Azure" button. This will take you to deploy an ARM Template wizard.
- Fill in the required parameters for deploying the playbook.
  ![deployment](images/deployment.png)
- Click "Review + create". Once the validation is successful, click on "Create".
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRamboV%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSpyCloud%20Enterprise%2FAnalyticsRules%2FSpyCloud-Breach-Rule%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRamboV%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSpyCloud%20Enterprise%2FAnalyticsRules%2FSpyCloud-Breach-Rule%2Fazuredeploy.json)

<a name="postdeployment">

## Post-Deployment Instructions
### Automate Response 
- In the automated response of this analytic rule, please add an automation rule to trigger "SpyCloud Breach Playbook".

