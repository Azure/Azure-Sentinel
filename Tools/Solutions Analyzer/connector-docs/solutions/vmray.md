# VMRay

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | VMRay |
| **Support Tier** | Partner |
| **Support Link** | [https://www.vmray.com/contact/customer-support/](https://www.vmray.com/contact/customer-support/) |
| **Categories** | domains |
| **First Published** | 2025-07-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [VMRayThreatIntelligence](../connectors/vmray.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | [VMRayThreatIntelligence](../connectors/vmray.md) | - |

## Content Items

This solution includes **13 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 13 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [VMRay Email Attachment Analyis](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/VMRay-Sandbox_Outlook_Attachment/azuredeploy.json) | Submits a attachment or set of attachment associated with an office 365 email to VMRay for Analyis. | - |
| [VMRay URL Analyis](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/Submit-URL-VMRay-Analyzer/azuredeploy.json) | Submits a url or set of urls associated with an incident to VMRay for Analyis. | - |
| [VMRayEnrichment_FunctionAppConnector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/CustomConnector/VMRayEnrichment_FunctionAppConnector/azuredeploy.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/CustomConnector/VMRayEnrichment_FunctionAppConnector/GetAnalysisBySampleID/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/CustomConnector/VMRayEnrichment_FunctionAppConnector/GetVMRayIOCs/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/CustomConnector/VMRayEnrichment_FunctionAppConnector/GetVMRaySample/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/CustomConnector/VMRayEnrichment_FunctionAppConnector/GetVMRaySampleByHash/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/CustomConnector/VMRayEnrichment_FunctionAppConnector/GetVMRaySubmission/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/CustomConnector/VMRayEnrichment_FunctionAppConnector/GetVMRayThreatIndicator/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/CustomConnector/VMRayEnrichment_FunctionAppConnector/GetVMRayVTIs/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/CustomConnector/VMRayEnrichment_FunctionAppConnector/UplaodURL/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/CustomConnector/VMRayEnrichment_FunctionAppConnector/VMRayUploadSample/function.json) | - | - |
| [host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Playbooks/CustomConnector/VMRayEnrichment_FunctionAppConnector/host.json) | - | - |

## Additional Documentation

> 📄 *Source: [VMRay/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/README.md)*

# VMRay Threat Intelligence Feed and Enrichment Integration - Microsoft Sentinel

**Latest Version:** **3.0.1** - **Release Date:** **2025-11-07**

## Overview


## Requirements
- Microsoft Sentinel.
- VMRay Analyzer, VMRay FinalVerdict, VMRay TotalInsight.
- Microsoft Azure
  1. Azure functions with Flex Consumption plan.
     Reference: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
     
	 **Note:** Flex Consumption plans are not available in all regions, please check if the region your are deploying the function is supported, if not we suggest you to deploy the function app with premium plan.
	 Reference: https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-how-to?tabs=azure-cli%2Cvs-code-publish&pivots=programming-language-python#view-currently-supported-regions
  3. Azure functions Premium plan.
	 Reference: https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan
  4. Azure Logic App with Consumption plan.
     Reference: https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-pricing#consumption-multitenant
  5. Azure storage with Standard general-purpose v2.

## VMRay Configurations

- In VMRay Console, you must create a Connector API key.Create it by following the steps below:
  
  1. Create a user dedicated for this API key (to avoid that the API key is deleted if an employee leaves)
  2. Create a role that allows to "View shared submission, analysis and sample" and "Submit sample, manage own jobs, reanalyse old analyses and regenerate analysis reports".
  3. Assign this role to the created user
  4. Login as this user and create an API key by opening Settings > Analysis > API Keys.
  5. Please save the keys, which will be used in configuring the Azure Function.

     
## Microsoft Sentinel

### Creating Application for API Access

- Open [https://portal.azure.com/](https://portal.azure.com) and search `Microsoft Entra ID` service.

![01](Images/01.png)

- Click `Add->App registration`.

![02a](Images/02a.png)

- Enter the name of application and select supported account types and click on `Register`.

![02](Images/02.png)

- In the application overview you can see `Application Name`, `Application ID` and `Tenant ID`.
 
![03](Images/03.png)

- After creating the application, we need to set API permissions for connector. For this purpose,
  - Click `Manage->API permissions` tab
  - Click `Microsoft Graph` button
  - Search `indicator` and click on the `ThreatIndicators.ReadWrite.OwnedBy`, click `Add permissions` button below.
  - Click on `Grant admin consent`

 ![app_per](Images/app_per.png) 

- We need secrets to access programmatically. For creating secrets
  - Click `Manage->Certificates & secrets` tab
  - Click `Client secrets` tab
  - Click `New client secret` button
  - Enter description and set expiration date for secret

![10](Images/10.png)

- Use Secret `Value` to configure connector.
  
 ![11](Images/11.png)


*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 07-11-2025                     | Fixed Premium ARM template                  |
| 3.0.0       | 23-07-2025                     | Initial Solution Release                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
