# Okta Single Sign-On (Polling CCP)

| | |
|----------|-------|
| **Connector ID** | `OktaSSO_Polling` |
| **Publisher** | Okta |
| **Tables Ingested** | [`OktaNativePoller_CL`](../tables-index.md#oktanativepoller_cl) |
| **Used in Solutions** | [Okta Single Sign-On](../solutions/okta-single-sign-on.md) |
| **Connector Definition Files** | [azuredeploy_Okta_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Data%20Connectors/OktaNativePollerConnector/azuredeploy_Okta_native_poller_connector.json) |

The [Okta Single Sign-On (SSO)](https://www.okta.com/products/single-sign-on/) connector provides the capability to ingest audit and event logs from the Okta API into Microsoft entinel. The connector provides visibility into these log types in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect OktaSSO**

Please insert your APIKey
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
