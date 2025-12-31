# SecurityBridge App

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | SecurityBridge |
| **Support Tier** | Partner |
| **Support Link** | [https://securitybridge.com/contact/](https://securitybridge.com/contact/) |
| **Categories** | domains,verticals |
| **First Published** | 2022-02-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [SecurityBridge Solution for SAP](../connectors/securitybridge.md)
- [SecurityBridge Threat Detection for SAP](../connectors/securitybridgesap.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ABAPAuditLog`](../tables/abapauditlog.md) | [SecurityBridge Solution for SAP](../connectors/securitybridge.md) | - |
| [`SecurityBridgeLogs`](../tables/securitybridgelogs.md) | - | Analytics, Workbooks |
| [`SecurityBridgeLogs_CL`](../tables/securitybridgelogs-cl.md) | [SecurityBridge Threat Detection for SAP](../connectors/securitybridgesap.md) | - |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [SecurityBridge: A critical event occured](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App/Analytic%20Rules/CriticalEventTriggered.yaml) | Medium | InitialAccess | [`SecurityBridgeLogs`](../tables/securitybridgelogs.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SecurityBridgeThreatDetectionforSAP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App/Workbooks/SecurityBridgeThreatDetectionforSAP.json) | [`SecurityBridgeLogs`](../tables/securitybridgelogs.md) |

## Additional Documentation

> 📄 *Source: [SecurityBridge App/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge App/README.md)*

# Deployment of Sentinel Connector for SecurityBridge Threat Detection for SAP through Content Hub
This ARM template will deploy a connecter for "SecurityBridge Threat Detection for SAP" with the following elements:
* Connector
* Workbook
* Parser Function

Follow the below steps to deploy this solution in your environment:
* Log on to Azure Portal
* Navigate to Azure Sentinel and select your workspace
* Select `Content Hub`
* Search for `SecurityBridge Threat Detection for SAP`
* Click on `Install` and then click on `Create`
* Follow the steps to install the connector

# Deployment of Sentinel Connector for SecurityBridge Threat Detection for SAP through ARM template

This ARM template will deploy a connecter for "SecurityBridge Threat Detection for SAP" with the following elements:
* Connector
* Workbook
* Parser Function

This is only a temporary solution to deploy the connector manually until the official connector is available on the content hub.

### Pre-reqs
* Log in: You should be logged into the Azure Sentinel Environment
* Workspace Name: Workspace id of the azure sentinel.
* Workspace Location: You can get that from Sentinel > Settings > Workspace Settings > Properties > Location.  For example `southcentralus`
* Installation of Azure Sentinel Agent on the SAP Machine
* Path of logs file generation
* Cron job to be added to the machine to append the newly created logs into an already existing file
* Logs reception in a custom table named "SecurityBridgeLogs_CL"

### Installation Steps 
* Click on the Deploy to Azure button below
* Select the **Resource Group** where Azure Sentinel is deployed
* Add the name of the **Azure Sentinel Workspace** in the Workspace box
* Leave rest of the items intact 
* Click on **Review + create** button
* Wait for the validation to complete
* Click on **Create**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Ffrozenstrawberries%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSecurityBridge%2FPackage%2FmainTemplate.json)

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                      |
|-------------|--------------------------------|-----------------------------------------|
| 3.2.1       | 22-09-2025                     | adding SecurityBridge_CL table          |
| 3.2.0       | 15-07-2025                     | adding push API data connector          |
| 3.1.0       | 12-02-2025                     | Adjusted contact and support            |
| 3.0.1       | 07-01-2025                     | Removed Deprecated **Data connector**   |
| 3.0.0       | 08-08-2024                     | Deprecating data connectors             |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
