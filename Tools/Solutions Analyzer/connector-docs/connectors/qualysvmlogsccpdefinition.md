# Qualys Vulnerability Management (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `QualysVMLogsCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`QualysHostDetectionV3_CL`](../tables-index.md#qualyshostdetectionv3_cl) |
| **Used in Solutions** | [QualysVM](../solutions/qualysvm.md) |
| **Connector Definition Files** | [QualysVMHostLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/QualysVM/Data%20Connectors/QualysVMHostLogs_ccp/QualysVMHostLogs_ConnectorDefinition.json) |

The [Qualys Vulnerability Management (VM)](https://www.qualys.com/apps/vulnerability-management/) data connector provides the capability to ingest vulnerability host detection data into Microsoft Sentinel through the Qualys API. The connector provides visibility into host detection data from vulerability scans.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **API access and roles**: Ensure the Qualys VM user has a role of Reader or higher. If the role is Reader, ensure that API access is enabled for the account. Auditor role is not supported to access the API. For more details, refer to the Qualys VM [Host Detection API](https://docs.qualys.com/en/vm/qweb-all-api/mergedProjects/qapi-assets/host_lists/host_detection.htm#v_3_0) and [User role Comparison](https://qualysguard.qualys.com/qwebhelp/fo_portal/user_accounts/user_roles_comparison_vm.htm) document.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Qualys Vulnerability Management to Microsoft Sentinel**
>**NOTE:** To gather data for Detections based on Host, expand the **DetectionList** column in the table.
To gather data from Qualys VM, you need to provide the following resources
#### 1. API Credentials 
 To gather data from Qualys VM, you'll need Qualys API credentials, including your Username and Password.
#### 2. API Server URL 
 To gather data from Qualys VM, you'll need the Qualys API server URL specific to your region. You can find the exact API server URL for your region [here](https://www.qualys.com/platform-identification/#api-urls)
- **Qualys API User Name**: Enter UserName
- **Qualys API Password**: (password field)
- **Qualys API Server URL**: Enter API Server URL
#### 3. Truncation Limit 
 Configure the maximum number of host records to retrieve per API call (20-5000 range). Higher values may improve performance but could impact API response times.
- **Truncation Limit** (select)
  - 1000 - API default value
  - 20 - Minimal load, slower collection
  - 100 - Low load
  - 500 - Moderate load
  - 2500 - High load, faster collection
  - ... and 1 more options
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
