# SlashNext Security Events for Microsoft Sentinel
<img src="./logo/slashnext-logo.png" alt="drawing" width="50%"/><br>

## Overview

The Playbook will get list of events occurred to a customer and log them in Log Analytic Workspace.

## SlashNext Security Events for Microsoft Sentinel Playbook 


### Pre-Deployment Instructions
1. Log analytic workspace is required. If your specified resource group does not have log analytic workspace, then create one.
2. Storage account is required for the playbook. If your specified resource group does not have any storage account, then create one.
3. In storage account create a container named as **offset**.

### Deployment Instructions 
1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter playbook name.
    * Storage Account Name: Enter storage account name.
    * Process X weeks Data: Previous weeks to start logging from.
    * Workspace ID: Enter ID of workspace for logging.
    * WorkSpace Name: Enter name of workspace for logging.
    * Enable Email Incidents: To enable email incidents logging.
    * Enable Web Incidents: To enable web incidents logging.
    * Enable SMS Incidents: To enable SMS/Mobile incidents logging.



### Post-Deployment Instructions - Deployment from market place
It will deploy two Template Spec
1. Click on **workspace-siem-lc-*** & deploy template.
2. Click on **workspace-siem-pl*** & deploy template using **Deployment Instructions** defined above.

### Post-Deployment Instructions
Open Playbook design.
1. Click on **API Connection** to provide connections info.
#### a. Authorize SlashNext connections

Once deployment is complete, authorize SlashNext Logic Apps Connector connection.<br><br>
**API key acquired from SlashNext**
1. Click on the SlashNext-CMS connection resource.
2. Click **Edit** API connection.
3. Enter SlashNext api key.
4. Click **Save**.

#### b. Authorize Storage connections

1. Click on **Storage** connection.
2. Enter/validate **Storage Account Name** and **Access Key** of storage account.
3. Click **Save**.


#### c. Authorize Log Analytic Workspace connections

1. Click on **Log Analytic Workspace** connection.
2. Enter/validate **Workspace ID** and **Primary/Secondary Key** of workspace to log events.
3. Click **Save**.

#### d. Save Logic app

1. Click on Designer.
2. Click **Save**.