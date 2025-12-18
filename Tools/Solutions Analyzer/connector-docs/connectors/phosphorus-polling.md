# Phosphorus Devices

| | |
|----------|-------|
| **Connector ID** | `Phosphorus_Polling` |
| **Publisher** | Phosphorus Inc. |
| **Tables Ingested** | [`Phosphorus_CL`](../tables-index.md#phosphorus_cl) |
| **Used in Solutions** | [Phosphorus](../solutions/phosphorus.md) |
| **Connector Definition Files** | [PhosphorusDataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Phosphorus/Data%20Connectors/PhosphorusDataConnector.json) |

The Phosphorus Device Connector provides the capability to Phosphorus to ingest device data logs into Microsoft Sentinel through the Phosphorus REST API. The Connector provides visibility into the devices enrolled in Phosphorus. This Data Connector pulls devices information along with its corresponding alerts.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **REST API Credentials/permissions**: **Phosphorus API Key** is required. Please make sure that the API Key associated with the User has the Manage Settings permissions enabled.

 Follow these instructions to enable Manage Settings permissions.
 1. Log in to the Phosphorus Application
 2. Go to 'Settings' -> 'Groups'
 3. Select the Group the Integration user is a part of
 4. Navigate to 'Product Actions' -> toggle on the 'Manage Settings' permission.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**STEP 1 - Configuration steps for the Phosphorus API**

 Follow these instructions to create a Phosphorus API  key.
 1. Log into your Phosphorus instance
 2. Navigate to Settings -> API 
 3. If the API key has not already been created, press the **Add button** to create the API key
 4. The API key can now be copied and used during the Phosphorus Device connector configuration

**2. Connect the Phosphorus Application with Microsoft Sentinel**

**STEP 2 - Fill in the details below**

>**IMPORTANT:** Before deploying the Phosphorus Device data connector, have the Phosphorus Instance Domain Name readily available as well as the Phosphorus API  Key(s)
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
