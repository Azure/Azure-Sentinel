# Okta Single Sign-On

| | |
|----------|-------|
| **Connector ID** | `OktaSSOv2` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`OktaV2_CL`](../tables-index.md#oktav2_cl), [`Okta_CL`](../tables-index.md#okta_cl), [`signIns`](../tables-index.md#signins) |
| **Used in Solutions** | [Okta Single Sign-On](../solutions/okta-single-sign-on.md) |
| **Connector Definition Files** | [OktaSSOv2_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Data%20Connectors/OktaNativePollerConnectorV2/OktaSSOv2_DataConnectorDefinition.json) |

The [Okta Single Sign-On (SSO)](https://www.okta.com/products/single-sign-on/) data connector provides the capability to ingest audit and event logs from the Okta Sysem Log API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform and uses the Okta System Log API to fetch the events. The connector supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Okta API Token**: An Okta API token. Follow the [following instructions](https://developer.okta.com/docs/guides/create-an-api-token/main/) to create an See the [documentation](https://developer.okta.com/docs/reference/api/system-log/) to learn more about Okta System Log API.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

To enable the Okta Single Sign-On for Microsoft Sentinel, provide the required information below and click on Connect.
>
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Endpoint**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add domain**

*Add domain*

When you click the "Add domain" button in the portal, a configuration form will open. You'll need to provide:

- **Okta Domain Name** (optional): Okta Domain Name (e.g., myDomain.okta.com)
- **API Key** (optional): API Key

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
