# Infoblox SOC Get Insight Details

* [Summary](#Summary)
* [Prerequisites](#Prerequisites)
* [Deployment instructions](#Deployment-instructions)
* [Post-Deployment instructions](#Post-Deployment-instructions)

## Summary<a name="Summary"></a>

This playbook uses the Infoblox SOC Insights API to **get all the details** about an SOC Insight Incident. These Incidents are triggered by the **Infoblox - SOC Insight Detected** analytic queries packaged as part of this solution. These queries will read your data for insights and create an Incident when one is found, hereby known as a **SOC Insight Incident**.

Then, you can run this playbook on those incidents to **ingest many details about the Insight**, placed in several custom tables prefixed with ```InfobloxInsight```. This data also builds the **Infoblox SOC Insight Workbook** you can use to richly visualize and drilldown your Insights.

It will also add **several tags** to the SOC Insight Incident.

This playbook can be configured to run automatically when a SOC Insight Incident occurs or run on demand.

### Prerequisites<a name="Prerequisites"></a>

1. User must have a valid Infoblox API Key.
2. User must have a valid Workspace ID.
3. User must have a valid Workspace Key.

### Deployment instructions<a name="Deployment-instructions"></a>

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here
    * Infoblox API Key: Enter valid value for API Key
    * Workspace ID: Enter value for Workspace ID,use same Workspace ID for Authorization
    * Workspace Key: Enter value for Workspace Key,use same Workspace Key for Authorization

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2FPlaybooks%2FInfoblox%20SOC%20Get%20Insight%20Details%2Fazuredeploy.json)[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2FPlaybooks%2FInfoblox%20SOC%20Get%20Insight%20Details%2Fazuredeploy.json)

### Post-Deployment instructions<a name="Post-Deployment-instructions"></a>

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Go to your logic app -> API connections -> Select azuremonitorlogs connection resource
2. Go to General -> edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Assign Role to Update in incident

Assign role to this playbook

1. Go to Log Analytics Workspace → <your workspace> → Access Control → Add","2. Add role assignment
3. Assignment type: Job function roles -> Add 'Microsoft Sentinel Contributor' as a Role
4. Members: select managed identity for assigned access to and add your logic app as member
5. Click on review+assign