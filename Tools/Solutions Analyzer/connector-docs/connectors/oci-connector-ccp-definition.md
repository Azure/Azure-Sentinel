# Oracle Cloud Infrastructure (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `OCI-Connector-CCP-Definition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`OCI_LogsV2_CL`](../tables-index.md#oci_logsv2_cl) |
| **Used in Solutions** | [Oracle Cloud Infrastructure](../solutions/oracle-cloud-infrastructure.md) |
| **Connector Definition Files** | [OCI_DataConnector_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Oracle%20Cloud%20Infrastructure/Data%20Connectors/Oracle_Cloud_Infrastructure_CCP/OCI_DataConnector_DataConnectorDefinition.json) |

The Oracle Cloud Infrastructure (OCI) data connector provides the capability to ingest OCI Logs from [OCI Stream](https://docs.oracle.com/iaas/Content/Streaming/Concepts/streamingoverview.htm) into Microsoft Sentinel using the [OCI Streaming REST API](https://docs.oracle.com/iaas/api/#/streaming/streaming/20180418).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **OCI Streaming API access**: Access to the OCI Streaming API through a API Signing Keys is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect to OCI Streaming API to start collecting Event logs in Microsoft Sentinel**

1) Log in to the OCI console and access the navigation menu.
2) In the navigation menu, go to "Analytics & AI" -> "Streaming".
3) Click "Create Stream".
4) Select an existing "Stream Pool" or create a new one.
5) Enter the following details:
   - "Stream Name"
   - "Retention"
   - "Number of Partitions"
   - "Total Write Rate"
   - "Total Read Rate" (based on your data volume)
6) In the navigation menu, go to "Logging" -> "Service Connectors".
7) Click "Create Service Connector".
8) Enter the following details:
   - "Connector Name"
   - "Description"
   - "Resource Compartment"
9) Select the "Source": "Logging".
10) Select the "Target": "Streaming".
11) (Optional) Configure "Log Group", "Filters", or use a "custom search query" to stream only the required logs.
12) Configure the "Target" by selecting the previously created stream.
13) Click "Create".
14) Follow the documentation to create a [Private Key and API Key Configuration File](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm).
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Tenant Id**
- **Stream**
- **Partition**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add Oracle Cloud Infrastructure Data Stream**

*Connect to Oracle Cloud Infrastructure Data*

When you click the "Add stream" button in the portal, a configuration form will open. You'll need to provide:

- **Stream OCID** (required): Provide the OCI Stream OCID (E.g. ocid1.stream.oc1..xxxxxxEXAMPLExxxxxx)
- **Public Message Endpoint of the stream (Service Endpoint Base URL)** (required): Provide the Service Endpoint Base URL: (https://cell-1.streaming.ap-hyderabad-1.oci.oraclecloud.com)
- **Cursor Type** (required): Select from available options
  - Individual Cursor
- **Partition Id** (required): Provide the Partition Id. (E.g. 0 or 1 or 2)
- **Tenant ID** (required): OCI Tenant ID (E.g. ocid1.tenancy.oc1..xxxxxxEXAMPLExxxxxx)
- **User ID** (required): Provide the User Id. (E.g. ocid1.user.oc1..xxxxxxEXAMPLExxxxxx)
- **Pem File Content** (required): Provide the Pem File content.
- **Fingerprint** (required): Provide the fingerprint for the Pem File Content. (E.g. 12:34:56:78:90:AB:CD:EF:GH:IJ:KL:MN:OP)
- **Pem File Pass Phrase** (optional): Just Leave blank If not encrypted)

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
