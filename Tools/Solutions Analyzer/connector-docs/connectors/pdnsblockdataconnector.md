# PDNS Block Data Connector

| | |
|----------|-------|
| **Connector ID** | `PDNSBlockDataConnector` |
| **Publisher** | Nominet |
| **Used in Solutions** | [PDNS Block Data Connector](../solutions/pdns-block-data-connector.md) |
| **Connector Definition Files** | [PDNSBlockDataConnector_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PDNS%20Block%20Data%20Connector/Data%20Connectors/PDNSBlockDataConnector_API_FunctionApp.json) |

This application enables you to ingest your PDNS block data into your SIEM tool

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`PDNSBlockData_CL`](../tables/pdnsblockdata-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **AWSAccessKeyId** and **AWSSecretAccessKey** are required for making AWS API calls.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to pull logs into Microsoft Sentinel. This might result in additional costs for data ingestion. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

**STEP 1 - To configure access to the S3 Bucket containing your PDNS Data Blocks, use the Access Key ID, Secret Access Key, and Role ARN that were provided to you.**

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
