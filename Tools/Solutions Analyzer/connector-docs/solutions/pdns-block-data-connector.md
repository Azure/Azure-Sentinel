# PDNS Block Data Connector

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Nominet PDNS Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.protectivedns.service.ncsc.gov.uk/pdns](https://www.protectivedns.service.ncsc.gov.uk/pdns) |
| **Categories** | domains |
| **First Published** | 2023-03-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PDNS%20Block%20Data%20Connector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PDNS%20Block%20Data%20Connector) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [PDNS Block Data Connector](../connectors/pdnsblockdataconnector.md)

**Publisher:** Nominet

This application enables you to ingest your PDNS block data into your SIEM tool

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Credentials/permissions**: **AWSAccessKeyId** and **AWSSecretAccessKey** are required for making AWS API calls.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to pull logs into Microsoft Sentinel. This might result in additional costs for data ingestion. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

**STEP 1 - To configure access to the S3 Bucket containing your PDNS Data Blocks, use the Access Key ID, Secret Access Key, and Role ARN that were provided to you.**

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `PDNSBlockData_CL` |
| **Connector Definition Files** | [PDNSBlockDataConnector_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PDNS%20Block%20Data%20Connector/Data%20Connectors/PDNSBlockDataConnector_API_FunctionApp.json) |

[→ View full connector details](../connectors/pdnsblockdataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `PDNSBlockData_CL` | [PDNS Block Data Connector](../connectors/pdnsblockdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
