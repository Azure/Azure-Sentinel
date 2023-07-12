# SlashNext Phishing Incident Investigation Playbook

<img src="../logo/slashnext-logo.png" alt="drawing" width="50%"/><br>

## Overview

Enhance your security with threat hunting and incident investigation using this playbook. Scan with world’s largest, real-time phishing intelligence database for accurate, definitive binary verdicts on suspicious URLs and download phishing forensics including webpage screenshots, HTML and text. The playbook shall perform the analysis of all URL entities attached to an existing incident using SlashNext Logic Apps Connector and add threat information to each malicious incident.

## SlashNext Phishing Incident Investigation Playbook

### Prerequisites

**SlashNext Logic Apps Connector** supports **Basic** authentication, while creating connection you will be asked to provide API key. 
To acquire SlashNext API key, please contact us at [support@slashnext.com](mailto:support@slashnext.com) or visit [SlashNext.com](www.slashnext.com)

### Deployment Instructions

**Deploy with Incident Trigger** (recommended) - After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinekl%2Fmaster%2FSolutions%2FSlashNext%2FPlaybooks%2FSlashNextPhishingIncidentInvestigation%2Fdeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSlashNext%2FPlaybooks%2FSlashNextPhishingIncidentInvestigation%2Fdeploy.json)

### Post-Deployment Instructions 

#### a. Authorize Connection

Once deployment is complete, authorize SlashNext Logic Apps Connector connection.

1. Click on the SlashNext connection resource
2. Click **Edit** API connection
3. Enter API key acquired from SlashNext
4. Click **Save**


