# Azure SQL Databases

| | |
|----------|-------|
| **Connector ID** | `AzureSql` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AzureDiagnostics`](../tables-index.md#azurediagnostics) |
| **Used in Solutions** | [Azure SQL Database solution for sentinel](../solutions/azure-sql-database-solution-for-sentinel.md) |
| **Connector Definition Files** | [template_AzureSql.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Data%20Connectors/template_AzureSql.JSON) |

Azure SQL is a fully managed, Platform-as-a-Service (PaaS) database engine that handles most database management functions, such as upgrading, patching, backups, and monitoring, without necessitating user involvement. This connector lets you stream your Azure SQL databases audit and diagnostic logs into Microsoft Sentinel, allowing you to continuously monitor activity in all your instances.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **Policy​**: owner role assigned for each policy assignment scope.​
- **Auditing**: read and write permissions to Azure SQL Server audit settings.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect your Azure SQL databases diagnostics logs into Sentinel.**

This connector uses Azure Policy to apply a single Azure SQL Database log-streaming configuration to a collection of instances, defined as a scope.   
Follow the instructions below to create and apply a policy to all current and future instances. **Note**, you may already have an active policy for this resource type.
**Stream diagnostics logs from your Azure SQL Databases at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.​**

    >1. In the **Basics** tab, click the button with the three dots under **Scope** to select your resources assignment scope.
        >2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log and metric types you want to ingest.
        >3. To apply the policy on your existing resources, select the **Remediation tab** and mark the **Create a remediation task** checkbox.
    - **Configure policy assignment**
**Stream audit logs from your Azure SQL Databases at the server level at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.​**

    >1. In the **Basics** tab, click the button with the three dots under **Scope** to select your resources assignment scope.
        >2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log and metric types you want to ingest.
        >3. To apply the policy on your existing resources, select the **Remediation tab** and mark the **Create a remediation task** checkbox.
    - **Configure policy assignment**

[← Back to Connectors Index](../connectors-index.md)
