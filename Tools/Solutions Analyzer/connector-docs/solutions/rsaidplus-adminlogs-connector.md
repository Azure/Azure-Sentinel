# RSAIDPlus_AdminLogs_Connector

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | RSA Support Team |
| **Support Tier** | Partner |
| **Support Link** | [https://community.rsa.com/](https://community.rsa.com/) |
| **Categories** | domains,verticals |
| **First Published** | 2025-10-14 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSAIDPlus_AdminLogs_Connector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSAIDPlus_AdminLogs_Connector) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [RSA ID Plus Admin Logs Connector](../connectors/rsaidplus-adminglogs-connector.md)

**Publisher:** RSA

The RSA ID Plus AdminLogs Connector provides the capability to ingest [Cloud Admin Console Audit Events](https://community.rsa.com/s/article/Cloud-Administration-Event-Log-API-5d22ba17) into Microsoft Sentinel using Cloud Admin APIs.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **RSA ID Plus API Authentication**: To access the Admin APIs, a valid Base64URL encoded JWT token, signed with the client's Legacy Administration API key is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Codeless Connector Framework (CCF) to connect to the RSA ID Plus Cloud Admin APIs to pull logs into Microsoft Sentinel.

**1. **STEP 1** - Create Legacy Admin API Client in Cloud Admin Console.**

Follow steps mentioned in this [page](https://community.rsa.com/s/article/Manage-Legacy-Clients-API-Keys-a89c9cbc#).

**2. **STEP 2** - Generate the Base64URL encoded JWT Token.**

Follow the steps mentioned in this [page](https://community.rsa.com/s/article/Authentication-for-the-Cloud-Administration-APIs-a04e3fb9) under the header 'Legacy Administration API'.

**3. **STEP 3** - Configure the Cloud Admin API to start ingesting Admin event logs into Microsoft Sentinel.**

Provide the required values below:
- **Admin API URL**: https://<tenantName>.access.securid.com/AdminInterface/restapi/v1/adminlog/exportLogs
- **JWT Token**: (password field)

**4. **STEP 4** - Click Connect**

Verify all the fields above were filled in correctly. Press Connect to start the connector.
- Click 'Connect' to establish connection

| | |
|--------------------------|---|
| **Tables Ingested** | `RSAIDPlus_AdminLogs_CL` |
| **Connector Definition Files** | [RSAIDPlus_AdminLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSAIDPlus_AdminLogs_Connector/Data%20Connectors/RSIDPlus_AdminLogs_Connector_CCP/RSAIDPlus_AdminLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/rsaidplus-adminglogs-connector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `RSAIDPlus_AdminLogs_CL` | [RSA ID Plus Admin Logs Connector](../connectors/rsaidplus-adminglogs-connector.md) |

[← Back to Solutions Index](../solutions-index.md)
