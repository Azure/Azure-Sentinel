# SlashNext Security Events for Microsoft Sentinel
<img src="./logo/slashnext-logo.png" alt="drawing" width="50%"/><br>

## Overview

The PlayBook will get list of events occured to a customer and log them in Log Analytic Workspace.

## SlashNext Security Events for Microsoft Sentinel Playbook 


### Deployment Instructions 
1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter playbook name here
    * Storage Account Name: Account to be created for storage.
    * Process X weeks Data: previous weeks to start logging from.
    * Workspace ID: ID of workspace for logging.
    * WorkSpace Name: Name of workspace for logging.
    * Enable Email Incidents: To enable email incidents logging.
    * Enable Web Incidents: To enable web incidents logging.
    * Enable SMS Incidents: To enable SMS/Mobile incidents logging.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSlashNext%20SIEM%2FPlayBook%2Fdeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSlashNext%20SIEM%2FPlayBook%2Fdeploy.json)

### Post-Deployment Instructions
Open PlayBook design.
1. Click on **API Connection** to provide connections info.
#### a. Authorize SlashNext connections

Once deployment is complete, authorize SlashNext Logic Apps Connector connection.

1. Click on the SlashNext-CMS connection resource
2. Click **Edit** API connection
3. Enter API key acquired from SlashNext
4. Click **Save**

#### b. Authorize Storage connections

1. Click on **Storage** connection.
2. Enter **Storage Account Name** and **Access Key** of storage created while deployement for SIEM application.
3. Click **Save**


#### c. Authorize Log Analytic Workspace connections

1. Click on **Log Analytic Workspace** connection.
2. Enter **Workspace ID** and **Primary/Secondary Key** of workspace to log events.
3. Click **Save**

#### d. Save Logic app

1. Click on Designer.
2. Click **Save**