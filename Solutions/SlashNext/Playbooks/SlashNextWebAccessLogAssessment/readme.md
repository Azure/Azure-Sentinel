# SlashNext Web Access Log Assessment Playbook 
<img src="../logo/slashnext-logo.png" alt="drawing" width="50%"/><br>

## Overview

Designed to analyze Web Access logs from Web Gateways and Firewalls. 
Scan your logs for continuous detection of phishing and malicious threat URLs clicked by end users.
Identify threats missed by current security layers

The playbook shall extract all the URLs from the logs to perform analysis using SlashNext Connector
and create an incident for each unique malicious URL found in the web logs.

## SlashNext Web Access Log Assessment Playbook 

### Prerequisites

**SlashNext Logic Apps Connector** supports **Basic** authentication, while creating connection you will be asked to provide API key. 
To acquire SlashNext API key, please contact us at [support@slashnext.com](mailto:support@slashnext.com) or visit [SlashNext.com](www.slashnext.com)

### Deployment Instructions 
1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter playbook name here

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSlashNext%2FPlaybooks%2FSlashNextWebAccessLogAssessment%2Fdeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSlashNext%2FPlaybooks%2FSlashNextWebAccessLogAssessment%2Fdeploy.json)

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
