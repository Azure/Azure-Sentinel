# Infoblox-SOC-Get-Open-Insights-API

* [Summary](#Summary)
* [Prerequisites](#Prerequisites)
* [Deployment instructions](#Deployment-instructions)
* [Post-Deployment instructions](#Post-Deployment-instructions)

## Summary<a name="Summary"></a>

This playbook uses the Infoblox SOC Insights REST API to ingest all Open/Active SOC Insights at time of run into the custom ```InfobloxInsight``` table. 

This playbook is an alternative to using the **Infoblox SOC Insight Data Connectors via the Microsoft forwarding agent**, which require the **Infoblox Cloud Data Connector (CDC)**. Instead, this playbook **ingests the same type of data via REST API**. This way, you do not need to set up and deploy and Infoblox CDC in your environment. 

You can use both methods in the same workspace, but **beware of duplicate data**.

Simply input your **Infoblox API Key** into the playbook parameters and it will ingest every open SOC Insight at runtime.

The Analytic Query **Infoblox - SOC Insight Detected - API Source** will read this data for insights and create an Incident when one is found. It is OK to run the playbook multiple times, as the Analytic Queries will group SOC Insight Incidents into one that have the same Infoblox Insight ID in the underlying data tables.

This playbook is scheduled to run on a daily basis. You can increase or decrease recurrence.

### Prerequisites<a name="Prerequisites"></a>

1. User must have a valid Infoblox API Key.

### Deployment instructions<a name="Deployment-instructions"></a>

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here
    * Infoblox API Key: Enter valid value for API Key
    * Workspace ID: Enter value for Workspace ID,use same Workspace ID for Authorization
    * Workspace Key: Enter value for Workspace Key,use same Workspace Key for Authorization

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2FPlaybooks%2FInfoblox%20SOC%20Get%20Open%20Insights%20API%2Fazuredeploy.json)[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2FPlaybooks%2FInfoblox%20SOC%20Get%20Open%20Insights%20API%2Fazuredeploy.json)

### Post-Deployment instructions<a name="Post-Deployment-instructions"></a>

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Go to your logic app -> API connections -> Select connection resource
2. Go to General -> edit API connection
3. Provide Workspace Id and Workspace Key of Log Analytics Workspace where Table will be created
4. Click Save
