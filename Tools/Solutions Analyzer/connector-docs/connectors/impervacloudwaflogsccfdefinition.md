# Imperva Cloud WAF

| | |
|----------|-------|
| **Connector ID** | `ImpervaCloudWAFLogsCCFDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ImpervaWAFCloudV2_CL`](../tables-index.md#impervawafcloudv2_cl) |
| **Used in Solutions** | [ImpervaCloudWAF](../solutions/impervacloudwaf.md) |
| **Connector Definition Files** | [ImpervaCloudWAFLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Data%20Connectors/ImpervaCloudWAFLogs_ccf/ImpervaCloudWAFLogs_ConnectorDefinition.json) |

The Imperva WAF Cloud data connector provides the capability to ingest logs into Microsoft Sentinel using the Imperva Log Integration through AWS S3 Bucket. Refer to [Imperva WAF Cloud Log Integration](https://docs.imperva.com/bundle/cloud-application-security/page/settings/log-integration.htm) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Imperva WAF Cloud to Microsoft Sentinel**
>**NOTE:** This connector fetches the Imperva Cloud WAF logs from AWS S3 bucket
To gather data from Imperva, you need to configure the following resources
#### 1. AWS Role ARN 
 To gather data from Imperva, you'll need AWS Role ARN.
#### 2. AWS SQS Queue URL 
 To gather data from Imperva, you'll need AWS SQS Queue URL.


For detailed steps to retrieve the AWS Role ARN, SQS Queue URL, and configure Imperva log forwarding to the Amazon S3 bucket, refer to the [Connector Setup Guide](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Data%20Connectors/Readme.md).
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **AWS Role ARN**
- **AWS SQS Queue URL**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add Account**

*Add Account*

When you click the "Add Account" button in the portal, a configuration form will open. You'll need to provide:

- **Role ARN** (optional): Enter Role ARN
- **Queue URL** (optional): Enter SQL Queue URL

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
