# Jamf Protect

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Jamf Software, LLC |
| **Support Tier** | Partner |
| **Support Link** | [https://www.jamf.com/support/](https://www.jamf.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-10-10 |
| **Last Updated** | 2025-09-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Jamf Protect Push Connector](../connectors/jamfprotectpush.md)

**Publisher:** Jamf

The [Jamf Protect](https://www.jamf.com/products/jamf-protect/) connector provides the capability to read raw event data from Jamf Protect in Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Microsoft Entra**: Permission to create an app registration in Microsoft Entra ID. Typically requires Entra ID Application Developer role or higher.
- **Microsoft Azure**: Permission to assign Monitoring Metrics Publisher role on data collection rule (DCR). Typically requires Azure RBAC Owner or User Access Administrator role

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Create ARM Resources and Provide the Required Permissions**

This connector reads data from the tables that Jamf Protect uses in a Microsoft Analytics Workspace, if the [data forwarding](https://docs.jamf.com/jamf-protect/documentation/Data_Forwarding_to_a_Third_Party_Storage_Solution.html?hl=sentinel#task-4227) option is enabled in Jamf Protect then raw event data is sent to the Microsoft Sentinel Ingestion API.
#### Automated Configuration and Secure Data Ingestion with Entra Application 
Clicking on "Deploy" will trigger the creation of Log Analytics tables and a Data Collection Rule (DCR). 
It will then create an Entra application, link the DCR to it, and set the entered secret in the application. This setup enables data to be sent securely to the DCR using an Entra token.
Deploy Jamf Protect connector resources

**2. Push your logs into the workspace**

Use the following parameters to configure the your machine to send the logs to the workspace.
- **Tenant ID (Directory ID)**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra App Registration Application ID**: `ApplicationId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra App Registration Secret**: `ApplicationSecret`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Data Collection Endpoint Uri**: `DataCollectionEndpoint`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Data Collection Rule Immutable ID**: `DataCollectionRuleId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Unified Logs Stream Name**: `Custom-jamfprotectunifiedlogs`
- **Telemetry Stream Name**: `Custom-jamfprotecttelemetryv2`
- **Alerts Stream Name**: `Custom-jamfprotectalerts`

| | |
|--------------------------|---|
| **Tables Ingested** | `jamfprotectalerts_CL` |
| | `jamfprotecttelemetryv2_CL` |
| | `jamfprotectunifiedlogs_CL` |
| **Connector Definition Files** | [connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Data%20Connectors/JamfProtect_ccp/connectorDefinition.json) |

[→ View full connector details](../connectors/jamfprotectpush.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `jamfprotectalerts_CL` | [Jamf Protect Push Connector](../connectors/jamfprotectpush.md) |
| `jamfprotecttelemetryv2_CL` | [Jamf Protect Push Connector](../connectors/jamfprotectpush.md) |
| `jamfprotectunifiedlogs_CL` | [Jamf Protect Push Connector](../connectors/jamfprotectpush.md) |

[← Back to Solutions Index](../solutions-index.md)
