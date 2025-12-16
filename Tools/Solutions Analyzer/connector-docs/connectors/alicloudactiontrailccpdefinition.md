# Alibaba Cloud ActionTrail (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `AliCloudActionTrailCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AliCloudActionTrailLogs_CL`](../tables-index.md#alicloudactiontraillogs_cl) |
| **Used in Solutions** | [Alibaba Cloud ActionTrail](../solutions/alibaba-cloud-actiontrail.md) |
| **Connector Definition Files** | [AliCloudActionTrail_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alibaba%20Cloud%20ActionTrail/Data%20Connectors/AliCloudCloudTrailConnector_CCP/AliCloudActionTrail_DataConnectorDefinition.json) |

The [Alibaba Cloud ActionTrail](https://www.alibabacloud.com/product/actiontrail) data connector provides the capability to retrieve actiontrail events stored into [Alibaba Cloud Simple Log Service](https://www.alibabacloud.com/product/log-service) and store them into Microsoft Sentinel through the [SLS REST API](https://www.alibabacloud.com/help/sls/developer-reference/api-sls-2020-12-30-getlogs). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **SLS REST API Credentials/permissions**: **AliCloudAccessKeyId** and **AliCloudAccessKeySecret** are required for making API calls. RAM policy statement with action of atleast `log:GetLogStoreLogs` over resource `acs:log:{#regionId}:{#accountId}:project/{#ProjectName}/logstore/{#LogstoreName}` is needed to grant a RAM user the permissions to call this operation.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure access to AliCloud SLS API**

Before using the API, you need to prepare your identity account and access key pair to effectively access the API.
1. We recommend that you use a Resource Access Management (RAM) user to call API operations. For more information, see [create a RAM user and authorize the RAM user to access Simple Log Service](https://www.alibabacloud.com/help/sls/create-a-ram-user-and-authorize-the-ram-user-to-access-log-service).
2. Obtain the access key pair for the RAM user. For details see [get Access Key pair](https://www.alibabacloud.com/help/ram/user-guide/create-an-accesskey-pair).

Note the access key pair details for the next step.

**2. Add ActionTrail Logstore**

To enable the Alibaba Cloud ActionTrail connector for Microsoft Sentinel, click upon add ActionTrail Logstore, fill the form with the Alibaba Cloud environment configuration and click Connect.
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **AliCloud SLS Logstore Endpoint URL**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add ActionTrail Logstore**

*Add SLS Logstore linked to Alibaba Cloud ActionTrail*

When you click the "Add Logstore" button in the portal, a configuration form will open. You'll need to provide:

- **Alibaba Cloud SLS Public Endpoint** (optional): <sls-region>.log.aliyuncs.com
- **Project** (optional): <project>
- **Logstore** (optional): <logstore>
- **Access Key ID** (optional): Access Key ID
- **Access Key Secret** (optional): Access Key Secret

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
