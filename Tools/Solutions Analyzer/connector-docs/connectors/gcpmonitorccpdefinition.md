# Google Cloud Platform Cloud Monitoring (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `GCPMonitorCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`GCPMonitoring`](../tables-index.md#gcpmonitoring) |
| **Used in Solutions** | [Google Cloud Platform Cloud Monitoring](../solutions/google-cloud-platform-cloud-monitoring.md) |
| **Connector Definition Files** | [GCPCloudMonitoringLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Monitoring/Data%20Connectors/GCPMonitoringLogs_CCP/GCPCloudMonitoringLogs_ConnectorDefinition.json) |

The Google Cloud Platform Cloud Monitoring data connector ingests Monitoring logs from Google Cloud into Microsoft Sentinel using the Google Cloud Monitoring API. Refer to [Cloud Monitoring API](https://cloud.google.com/monitoring/api/v3) documentation for more details.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Google Cloud Platform Cloud Monitoring to Microsoft Sentinel**
#### 1. Setup GCP Monitoring Integration
 To fetch logs from GCP Cloud Monitoring to Sentinel **Project ID** of Google cloud is required.
#### 2. Chose the **Metric Type**
 To collect logs from Google Cloud Monitoring provide the required Metric type.

For more details, refer to [Google Cloud Metrics](https://cloud.google.com/monitoring/api/metrics_gcp).
#### 3. OAuth Credentials
 To Fetch Oauth client id and client secret refer to this [documentation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Monitoring/Data%20Connectors/Readme.md).
#### 4. Connect to Sentinel
 Click on **Connect** to start pulling monitoring logs from Google Cloud into Microsoft Sentinel.
- **GCP Project ID**
- **Metric Type**
- **OAuth Configuration**:
  - Client ID
  - Client Secret
  - Click 'Connect' to authenticate
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Metric Type**
- **Project ID**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

[← Back to Connectors Index](../connectors-index.md)
