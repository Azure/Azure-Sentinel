# Microsoft Business Applications

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `FinanceOperationsActivity_CL` |
| **Connector Definition Files** | [DynamicsFinOps_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Data%20Connectors/DynamicsFinOpsPollerConnector/DynamicsFinOps_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/dynamics365finance.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `FinanceOperationsActivity_CL` | [Dynamics 365 Finance and Operations](../connectors/dynamics365finance.md) |

[← Back to Solutions Index](../solutions-index.md)
