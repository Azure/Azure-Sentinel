# Microsoft Business Applications

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-04-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Dynamics 365 Finance and Operations](../connectors/dynamics365finance.md)

**Publisher:** Microsoft

Dynamics 365 for Finance and Operations is a comprehensive Enterprise Resource Planning (ERP) solution that combines financial and operational capabilities to help businesses manage their day-to-day operations. It offers a range of features that enable businesses to streamline workflows, automate tasks, and gain insights into operational performance.



The Dynamics 365 Finance and Operations data connector ingests Dynamics 365 Finance and Operations admin activities and audit logs as well as user business process and application activities logs into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `FinanceOperationsActivity_CL` |
| **Connector Definition Files** | [DynamicsFinOps_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Data%20Connectors/DynamicsFinOpsPollerConnector/DynamicsFinOps_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/dynamics365finance.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `FinanceOperationsActivity_CL` | [Dynamics 365 Finance and Operations](../connectors/dynamics365finance.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                  |
|-------------|--------------------------------|---------------------------------------------------------------------|
| 3.2.2       | 22-04-2025                     |<ul><li>Updated solution description.</li></ul> |
| 3.2.1       | 11-04-2025                     |<ul><li>Move solution and content to GA.</li><li>Minor analytic rule update.</li></ul> |
| 3.2.0       | 15-11-2024                     | <ul><li>Renamed solution from Power Platform to Microsoft Business Applications.</li><li>Merge Dynamics 365 CE Apps and Dynamics 365 Finance & Operations into a unified solution.</li><li>New analytics rules, playbooks and hunting queries.</li><li>Replace Dynamics 365 Finance and Operations function app using Codeless Connector.</li><li>Retire PPInventory function app.</li></ul>|
| 3.1.3       | 12-07-2024                     |<ul><li>Removal of Power Apps, Power Platform Connectors, Power Platform DLP data connectors. Associated logs are now ingested via Power Platform Admin Activity data connector.</li><li>Update of analytics rules to utilize PowerPlatfromAdminActivity table.</li><li>Update data connectors DCR properties.</li></ul> |

[← Back to Solutions Index](../solutions-index.md)
