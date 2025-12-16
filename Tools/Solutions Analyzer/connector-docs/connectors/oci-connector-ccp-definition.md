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
2) In the navigation menu, go to "Analytics & AI" → "Streaming".
3) Click "Create Stream".
4) Select an existing "Stream Pool" or create a new one.
5) Enter the following details:
   - "Stream Name"
   - "Retention"
   - "Number of Partitions"
   - "Total Write Rate"
   - "Total Read Rate" (based on your data volume)
6) In the navigation menu, go to "Logging" → "Service Connectors".
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
 Note : The connector only supports ingesting data from one partition ID at a time, and that ID must be a single-digit number (e.g., 0, 1, or 2).
- **Stream OCID**: Provide the OCI Stream OCID (E.g. ocid1.stream.oc1..xxxxxxEXAMPLExxxxxx)
- **Service Endpoint Base URL**: Provide the Service Endpoint Base URL: (https://cell-1.streaming.ap-hyderabad-1.oci.oraclecloud.com)
- **Cursor Type** (select)
  - Individual Cursor
- **Partition Id**: Provide the Partition Id. (E.g. 0 or 1 or 2)
- **Tenant ID**: OCI Tenant ID (E.g. ocid1.tenancy.oc1..xxxxxxEXAMPLExxxxxx)
- **User ID**: Provide the User Id. (E.g. ocid1.user.oc1..xxxxxxEXAMPLExxxxxx)
- **Pem File Content**: (password field)
- **Pass Phrase**: (password field)
- **Fingerprint**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
