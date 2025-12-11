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
