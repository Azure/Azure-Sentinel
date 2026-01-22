# Infoblox-SOC-Import-Indicators-TI

* [Summary](#Summary)
* [Prerequisites](#Prerequisites)
* [Deployment instructions](#Deployment-instructions)
* [Post-Deployment instructions](#Post-Deployment-instructions)

## Summary<a name="Summary"></a>

This playbook imports each Indicator of an SOC Insight Incident into the ```ThreatIntelligenceIndicator``` table you can use as **threat intelligence**. 

*You must run the **Infoblox-SOC-Get-Insight-Details** playbook on the SOC Insight Incident before running this playbook.*

This playbook can be configured to run automatically when a SOC Insight Incident occurs or run on demand.

### Prerequisites<a name="Prerequisites"></a>

1. Workspace Name
2. Entra ID Application Secret
3. Client ID
4. Tenant ID

### Deployment instructions<a name="Deployment-instructions"></a>

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here
    * Workspace Name: Enter workspace name in which Incident is created
    * Entra ID Application Secret: Enter value for Entra ID Application Secret
    * Client ID: Enter value for Application (Client) ID
    * Tenant ID: Enter value for Directory (Tenant) ID

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2FPlaybooks%2FInfoblox%20SOC%20Import%20Indicators%20TI%2Fazuredeploy.json)[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FInfoblox%2FPlaybooks%2FInfoblox%20SOC%20Import%20Indicators%20TI%2Fazuredeploy.json)

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

1. Go to Log Analytics Workspace → *select your workspace* → Access Control → Add
2. Add role assignment
3. Assignment type: Job function roles -> Add 'Microsoft Sentinel Contributor' as a Role
4. Members: select managed identity for assigned access to and add your logic app as member
5. Click on review+assign
