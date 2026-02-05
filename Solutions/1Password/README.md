# 1Password (Preview)

## Overview

The key function of this Solution is to retrieve sign-in attempts, item usage, and audit events logs from your 1Password Business account using the 1Password Events Reporting API, and store it in an Azure Log Analytics Workspace using Microsoft cloud native features.

## Azure services needed

### Required

- [1Password Business account](https://1password.com/business)
- [1Password Events API key](https://support.1password.com/events-reporting/#appendix-issue-or-revoke-bearer-tokens)
- [Microsoft Azure](https://azure.microsoft.com/free)
- [Microsoft Sentinel](https://azure.microsoft.com/products/microsoft-sentinel/)
- Contributor role with User Access Administrator role on the Microsoft Sentinel Resource Group <br>
**or**
- Owner on the Microsoft Sentinel Resource Group 

## Automated Installation

Installing the 1Password Solution for Microsoft Sentinel is easy and can be completed in only a few minutes. 
Just click the button below to get started with the deployment wizard. <br>

[![Deploy To Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg?sanitize=true)](https://aka.ms/sentinel-OnePassword-azuredeploy)

> NOTE: To deploy the solution, the Azure user account executing the deployment needs to have `Owner` permissions on the Microsoft Sentinel `Resource Group` in Azure.<br>
> This is required to assign the correct RBAC role to the managed identity of the FunctionApp!  

## Manual Installation using the ARM template

<details>

<summary>Deployment steps</summary>
<br/>

## Manual Installation using the ARM template

1. Install the data connector using the ARM template or use this link to skip the steps below

![Alt text](https://github.com/Azure/Azure-Sentinel/blob/f3655ba6a4891acdda67c3c3bf2414401de323b6/Solutions/1Password/images/image.png)

2. After the deployment of the template has completed open the Microsoft Sentinel portal and select the data connector

![Alt text](https://github.com/Azure/Azure-Sentinel/blob/f3655ba6a4891acdda67c3c3bf2414401de323b6/Solutions/1Password/images/dataconnector.png)

3. Select the `Open connector page` button to open the data connector configuration
4. click on the `Deploy to Azure` button<br>
This will open a new browser page containing a deployment wizard in Microsoft Azure.<br>
Fill in all the required fields and select `create` on the last page.

![Alt text](https://github.com/Azure/Azure-Sentinel/blob/fd9527ab432fa3e4e6115e4ee823ed5c2a92c163/Solutions/1Password/images/summary.png)

The required resources for the deployment will now be created.

</details>

## Deployed Resources

The 1Password Solution for Microsoft Sentinel is comprised of following Azure resources:

> Click on the topics below to fold them out.

<details>

<summary>Resource Group</summary>
<br/>

### **Resource Group**

The Azure resource group is used as a container to group a set of Azure resources that share the same lifecycle.
> NOTE: Known limitation is that the Solution can only be deployed within the same `resourcegroup` as where Microsoft Sentinel is hosted.

</details>

<details>

<summary>Function App</summary>
<br/>

### **FunctionApp**

The Azure FunctionApp runs on top of an Azure App Service and is used to host the _PowerShell_ function to query the 1Password API endpoint. The Azure FunctionApp has the following components:

```powershell
|- WWWROOT
|-|- Modules
|-|-|- HelperFunctions.psm1
|-|- function
|-|-|- function.json
|-|-|- run.ps1
|-|- host.json
|-|- profile.ps1
|-|- requirements.psd1
```

The ```HelperFunctions.psm1``` module is used to simplify the FunctionApp code and handles security related tasks like:

- Query the 1Password Events API endpoint
- Send the data to the Data Collection Rule endpoint
- Set and retrieve the cursor and timestamp to a storage account

</details>

<details>

<summary>Key Vault</summary>
<br/>

### **Key Vault**

The Azure Key Vault resource is used to securely store certain sensitive or secret values used in the 1Password Solution for Microsoft Sentinel. 
Because of the sensitivity of the secrets in the Key Vault, access is restricted to the Managed Identity (MSI) of the FunctionApp.
Secrets that reside in the vault are:

- APIKey (1password)
- functionAppPackage (location to zip package hosting the function)
- dataCollectionEndpoint (endpoint for uploading 1Password logs)

</details>

<details>

<summary>Storage Account</summary>
<br/>

### **Storage Account**

The Storage Account resources is used to store logs and properties of the Azure FunctionApp.

</details>

<details>

<summary>Application Insights</summary>
<br/>

### **Application Insights**

The Application Insights instance is used for collecting telemetry of the Azure FunctionApp.
This provides visibility into the availability, performance, and usage patterns of the FunctionApp.

</details>

<details>

<summary>Data Collection Rule</summary>
<br/>

### **Data Collection Rule (DCR)**

The Data Collection Rule is attached to a _data collection endpoint_ and a Log Analytics table.
The Managed Identity (MSI) of the FunctionApp is used to authenticate against the data collection endpoint.

</details>

<details>

<summary>Custom Table</summary>
<br/>

## **Custom Table**

During deployment, a custom table with the name "OnePasswordEventLogs_CL" is created in the Log Analytics workspace.

</details>

<details>

<summary>Role Assignment</summary>
<br/>

### **Role Assignment**

The identity used to send the data to the Data Collection Endpoint needs to have the _Monitoring Metrics Publisher_ role on the Data Collection Rule (DCR). 
> NOTE: I can take up to 30 minutes after deployment before the first data is received by the table. <br>

</details>

## Implementation resources

The 1Password Solution for Microsoft Sentinel is deployed from the Data Connector in sentinel. You must create the Data Connector in order to deploy the 1Password Solution. 
> Note: In the 1Password (Preview) Solution the installation in done using an ARM (Azure Resource Manager) template.<br>Once the Solution is in GA (general availability) it will be installed from the Microsoft Sentinel content hub.


## Post Deployment steps

- N/A
