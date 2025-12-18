# Illumio Saas

| | |
|----------|-------|
| **Connector ID** | `IllumioSaasCCFDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`IllumioFlowEventsV2_CL`](../tables-index.md#illumiofloweventsv2_cl) |
| **Used in Solutions** | [IllumioSaaS](../solutions/illumiosaas.md) |
| **Connector Definition Files** | [IllumioSaasLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Data%20Connectors/IllumioSaasLogs_ccf/IllumioSaasLogs_ConnectorDefinition.json) |

The Illumio Saas Cloud data connector provides the capability to ingest Flow logs into Microsoft Sentinel using the Illumio Saas Log Integration through AWS S3 Bucket. Refer to [Illumio Saas Log Integration](https://product-docs-repo.illumio.com/Tech-Docs/CloudSecure/out/en/administer-cloudsecure/connector.html#UUID-c14edaab-9726-1f23-9c4c-bc2937be39ee_section-idm234556433515698) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Illumio Saas to Microsoft Sentinel**
>**NOTE:** This connector fetches the Illumio Saas Flow logs from AWS S3 bucket
To gather data from Illumio, you need to configure the following resources
#### 1. AWS Role ARN 
 To gather data from Illumio, you'll need AWS Role ARN.
#### 2. AWS SQS Queue URL 
 To gather data from Illumio, you'll need AWS SQS Queue URL.


For detailed steps to retrieve the AWS Role ARN, SQS Queue URL, and configure Illumio log forwarding to the Amazon S3 bucket, refer to the [Connector Setup Guide](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Data%20Connectors/IllumioSaasLogs_ccf/Readme.md).
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **AWS Role ARN**
- **AWS SQS Queue URL**
- **Table Name**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add Account**

*Add Account*

When you click the "Add Account" button in the portal, a configuration form will open. You'll need to provide:

- **Role ARN** (optional): Enter Role ARN
- **Flow Log Queue URL** (optional): Enter Flow log SQL Queue URL

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
