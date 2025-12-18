# Sophos Endpoint Protection

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2021-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20Endpoint%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20Endpoint%20Protection) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Sophos Endpoint Protection](../connectors/sophosep.md)

**Publisher:** Sophos

### [Sophos Endpoint Protection (using REST API)](../connectors/sophosendpointprotectionccpdefinition.md)

**Publisher:** Microsoft

The [Sophos Endpoint Protection](https://www.sophos.com/en-us/products/endpoint-antivirus.aspx) data connector provides the capability to ingest [Sophos events](https://developer.sophos.com/docs/siem-v1/1/routes/events/get) and [Sophos alerts](https://developer.sophos.com/docs/siem-v1/1/routes/alerts/get) into Microsoft Sentinel. Refer to [Sophos Central Admin documentation](https://docs.sophos.com/central/Customer/help/en-us/central/Customer/concepts/Logs.html) for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Sophos Endpoint Protection API access**: Access to the Sophos Endpoint Protection API through a service principal is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect to Sophos Endpoint Protection API to start collecting event and alert logs in Microsoft Sentinel**

Follow [Sophos instructions](https://developer.sophos.com/getting-started-tenant) to create a service principal with access to the Sophos API. It will need the Service Principal ReadOnly role.
 Through those instructions, you should get the Client ID, Client Secret, Tenant ID and data region.
 Fill the form bellow with that information.
- **Sophos Tenant ID**: Sophos Tenant ID
- **Sophos Tenant Data Region**: eu01, eu02, us01, us02 or us03
- **OAuth Configuration**:
  - Client ID
  - Client Secret
  - Click 'Connect' to authenticate
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Name**
- **ID**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

| | |
|--------------------------|---|
| **Tables Ingested** | `SophosEPAlerts_CL` |
| | `SophosEPEvents_CL` |
| **Connector Definition Files** | [SophosEP_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20Endpoint%20Protection/Data%20Connectors/SophosEP_ccp/SophosEP_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/sophosendpointprotectionccpdefinition.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SophosEPAlerts_CL` | [Sophos Endpoint Protection (using REST API)](../connectors/sophosendpointprotectionccpdefinition.md) |
| `SophosEPEvents_CL` | [Sophos Endpoint Protection (using REST API)](../connectors/sophosendpointprotectionccpdefinition.md) |
| `SophosEP_CL` | [Sophos Endpoint Protection](../connectors/sophosep.md) |

[← Back to Solutions Index](../solutions-index.md)
