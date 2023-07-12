# SlashNext Web log & Incident Investigation Connector and Playbook Templates


<img src="./logo/slashnext-logo.png" alt="drawing" width="50%"/><br>

## Table of Contents

1. [Overview](#overview)
   1. [SlashNext URL Investigation Connector + Playbook Templates](#logic-apps-connector--playbook-templates)
2. [SlashNext URL Investigation Connector + Playbook Templates](#slashnext-logic-apps-connector-and-playbook-templates-deployment)
   1. [Prerequisites](#prerequisites)
   2. [Deployment Instructions](#deployment-instructions)
   3. [Post-Deployment Instructions](#post-deployment-instructions)

## Overview

**SlashNext URL Investigation Connector** is based upon its Real-time Phishing Defense (RPD) APIs which are connected to SlashNext real-time threat intelligence database, continuously updated with the latest phishing threats. SlashNext RPD APIs are designed to be very fast and give accurate binary verdict on each enrichment request to ease its integration in any phishing Incident Response (IR) or SOAR environment.

### SlashNext URL Investigation Connector + Playbook Templates

This package contains two sample playbook templates to demonstrate the power and simplicity of SlashNext Logic Apps Connector usage.

* [SlashNext URL Investigation Connector](./Playbook/SlashNextVerdictCustomconnector) - Makes use of the SlashNext Real-time Phishing Defense APIs (URL reputation) for fast, accurate and binary verdicts.
* These two playbook templates leverage SlashNext Logic Apps Connector to achieve following:
    * [Web Access log Assessment](./Playbooks/SlashNextLogAssessment) - Designed to be used for the analysis of different kinds of weblogs which are suspected to contain phishing URLs. The playbook shall extract all the URLs from the weblogs and perform their analysis using SlashNext Logic Apps Connector and create an incident for each unique malicious URL found in the weblogs.
    * [Phishing Incident Investigation](./Playbooks/SlashNextIncident) - Designed to be used for the confirmation of suspicious incidents as malicious or benign. The playbook shall perform the analysis of all URL entities attached to an existing incident using SlashNext Logic Apps Connector and add comment to each malicious incident

You can choose to deploy the whole package (logic apps connector + both playbook templates) or each one separately from its specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSlashNext%2FPlaybooks%2Fdeploy.json) 
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSlashNext%2FPlaybooks%2Fdeploy.json)

## SlashNext Logic Apps Connector and Playbook Templates

Follow the steps given below to deploy the **SlashNext Logic Apps Connector** and sample playbook templates.

### Prerequisites

**SlashNext Logic Apps Connector** supports **Basic** authentication, while creating connection you will be asked to provide API key. 
To acquire SlashNext API key, please contact us at [support@slashnext.com](mailto:support@slashnext.com) or visit [SlashNext.com](www.slashnext.com)

### Deployment Instructions

1. To deploy Logic App Connector and playbook templates, click the **Deploy to Azure** button. This will launch the ARM Template
   deployment wizard.
2. Fill in the required parameters for deploying Logic App Connector and playbook templates.


| Deployment Parameters                           | Description                                                      |
|-------------------------------------------------|------------------------------------------------------------------|
| **Web Access log Assessment Playbook** Name   | Enter the playbook name here (e.g. SlashNext-WebLogAssessment)   |
| **Phishing Incident Investigation Playbook** Name | Enter the playbook name here (e.g. SlashNext-IncidentEnrichment) |

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize SlashNext Logic Apps Connector connection.

1. Click on the SlashNext connection resource
2. Click **Edit** API connection
3. Enter API key acquired from SlashNext
4. Click **Save**

#### b. Configure Logic App Permissions

1. Click on **Identity**
2. Select **Azure role assignment** from system assigned tab
3. Click on **Add role assignment**
4. Select relevant permission and save
5. Repeat above steps for the following permissions
    1. Log Analytics Reader
    2. Microsoft Sentinel Contributor

#### c. Set following Variables in Logic App as per the Environment

1. Subscription Id
2. Workspace Id
3. Resource Group
4. Workspace Name
