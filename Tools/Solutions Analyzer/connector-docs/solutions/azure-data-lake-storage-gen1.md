# Azure Data Lake Storage Gen1

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-06-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Data%20Lake%20Storage%20Gen1](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Data%20Lake%20Storage%20Gen1) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Data Lake Storage Gen1](../connectors/azuredatalakestoragegen1-ccp.md)

**Publisher:** Microsoft

Azure Data Lake Storage Gen1 is an enterprise-wide hyper-scale repository for big data analytic workloads. Azure Data Lake enables you to capture data of any size, type, and ingestion speed in one single place for operational and exploratory analytics. This connector lets you stream your Azure Data Lake Storage Gen1 diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2223812&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Policy**: owner role assigned for each policy assignment scope

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect your Azure Data Lake Storage Gen1 diagnostics logs into Sentinel.**

This connector uses Azure Policy to apply a single Azure Data Lake Storage Gen1 log-streaming configuration to a collection of instances, defined as a scope. Follow the instructions below to create and apply a policy to all current and future instances. Note, you may already have an active policy for this resource type.
**Stream diagnostics logs from your Azure Data Lake Storage Gen1 at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.**

    >    1. In the **Basics** tab, click the button with the three dots under **Scope** to select your subscription.<br />2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log categories you want to ingest.<br />3. To apply the policy on your existing resources, mark the **Create a remediation task** check box in the **Remediation** tab.</value>
    > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `PolicyAssignment`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureDataLakeStorageGen1_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Data%20Lake%20Storage%20Gen1/Data%20Connectors/AzureDataLakeStorageGen1_CCP.JSON) |

[→ View full connector details](../connectors/azuredatalakestoragegen1-ccp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Data Lake Storage Gen1](../connectors/azuredatalakestoragegen1-ccp.md) |

[← Back to Solutions Index](../solutions-index.md)
