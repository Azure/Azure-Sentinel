# Azure Activity

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-04-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Azure Activity](../connectors/azureactivity.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AzureActivity`](../tables/azureactivity.md) | [Azure Activity](../connectors/azureactivity.md) | Analytics, Hunting, Workbooks |
| [`RareCustomScriptExecution`](../tables/rarecustomscriptexecution.md) | - | Hunting |
| [`RoleAssignedActivitywithRoleDetails`](../tables/roleassignedactivitywithroledetails.md) | - | Analytics |

## Content Items

This solution includes **31 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 15 |
| Analytic Rules | 14 |
| Workbooks | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Azure Machine Learning Write Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/Machine_Learning_Creation.yaml) | Low | InitialAccess, Execution, Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Creation of expensive computes in Azure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/Creation_of_Expensive_Computes_in_Azure.yaml) | Low | DefenseEvasion | [`AzureActivity`](../tables/azureactivity.md) |
| [Mass Cloud resource deletions Time Series Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/TimeSeriesAnomaly_Mass_Cloud_Resource_Deletions.yaml) | Medium | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Microsoft Entra ID Hybrid Health AD FS New Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/AADHybridHealthADFSNewServer.yaml) | Medium | DefenseEvasion | [`AzureActivity`](../tables/azureactivity.md) |
| [Microsoft Entra ID Hybrid Health AD FS Service Delete](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/AADHybridHealthADFSServiceDelete.yaml) | Medium | DefenseEvasion | [`AzureActivity`](../tables/azureactivity.md) |
| [Microsoft Entra ID Hybrid Health AD FS Suspicious Application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/AADHybridHealthADFSSuspApp.yaml) | Medium | CredentialAccess, DefenseEvasion | [`AzureActivity`](../tables/azureactivity.md) |
| [NRT Creation of expensive computes in Azure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/NRT_Creation_of_Expensive_Computes_in_Azure.yaml) | Medium | DefenseEvasion | [`AzureActivity`](../tables/azureactivity.md) |
| [NRT Microsoft Entra ID Hybrid Health AD FS New Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/NRT-AADHybridHealthADFSNewServer.yaml) | Medium | DefenseEvasion | [`AzureActivity`](../tables/azureactivity.md) |
| [New CloudShell User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/New-CloudShell-User.yaml) | Low | Execution | [`AzureActivity`](../tables/azureactivity.md) |
| [Rare subscription-level operations in Azure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/RareOperations.yaml) | Low | CredentialAccess, Persistence | [`AzureActivity`](../tables/azureactivity.md) |
| [Subscription moved to another tenant](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/SubscriptionMigration.yaml) | Low | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Suspicious Resource deployment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/NewResourceGroupsDeployedTo.yaml) | Low | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Suspicious granting of permissions to an account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/Granting_Permissions_To_Account_detection.yaml) | Medium | Persistence, PrivilegeEscalation | [`AzureActivity`](../tables/azureactivity.md)<br>[`RoleAssignedActivitywithRoleDetails`](../tables/roleassignedactivitywithroledetails.md) |
| [Suspicious number of resource creation or deployment activities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/Creating_Anomalous_Number_Of_Resources_detection.yaml) | Medium | Impact | [`AzureActivity`](../tables/azureactivity.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Anomalous Azure Operation Hunting Model](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AnomalousAzureOperationModel.yaml) | LateralMovement, CredentialAccess | [`AzureActivity`](../tables/azureactivity.md) |
| [Azure Machine Learning Write Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Machine_Learning_Creation.yaml) | InitialAccess, Execution, Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Azure Network Security Group NSG Administrative Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AzureNSG_AdministrativeOperations.yaml) | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Azure VM Run Command executed from Azure IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AzureRunCommandFromAzureIP.yaml) | LateralMovement, CredentialAccess | - |
| [Azure Virtual Network Subnets Administrative Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AzureVirtualNetworkSubnets_AdministrativeOperationset.yaml) | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Azure storage key enumeration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Anomalous_Listing_Of_Storage_Keys.yaml) | Discovery | [`AzureActivity`](../tables/azureactivity.md) |
| [AzureActivity Administration From VPS Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AzureAdministrationFromVPS.yaml) | InitialAccess | [`AzureActivity`](../tables/azureactivity.md) |
| [Common deployed resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Common_Deployed_Resources.yaml) | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Creation of an anomalous number of resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Creating_Anomalous_Number_Of_Resources.yaml) | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Granting permissions to account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Granting_Permissions_to_Account.yaml) | Persistence, PrivilegeEscalation | [`AzureActivity`](../tables/azureactivity.md) |
| [Microsoft Sentinel Analytics Rules Administrative Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AnalyticsRulesAdministrativeOperations.yaml) | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Microsoft Sentinel Connectors Administrative Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AzureSentinelConnectors_AdministrativeOperations.yaml) | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Microsoft Sentinel Workbooks Administrative Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AzureSentinelWorkbooks_AdministrativeOperation.yaml) | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Port opened for an Azure Resource](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/PortOpenedForAzureResource.yaml) | CommandAndControl, Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Rare Custom Script Extension](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Rare_Custom_Script_Extension.yaml) | Execution | [`AzureActivity`](../tables/azureactivity.md)<br>[`RareCustomScriptExecution`](../tables/rarecustomscriptexecution.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Workbooks/AzureActivity.json) | [`AzureActivity`](../tables/azureactivity.md) |
| [AzureServiceHealthWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Workbooks/AzureServiceHealthWorkbook.json) | [`AzureActivity`](../tables/azureactivity.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                         |
|-------------|--------------------------------|----------------------------------------------------------------------------|
| 3.0.3       | 19-02-2025                     | Added new **Workbook** Azure Service Health to the Solution and added new **Hunting query** Machine_Learning_Creation.yaml. <br/> Added new **Analytic Rule** Machine_Learning_Creation.yaml          |
| 3.0.2       | 21-02-2024                     | Modified Entity Mappings of **Analytic Rules**                             |
| 3.0.1       | 23-01-2024                     | Added subTechniques in Template                                            |
| 3.0.0       | 06-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID. <br/> Optimized the **Analytic Rule** query logic to achieve expected results    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
