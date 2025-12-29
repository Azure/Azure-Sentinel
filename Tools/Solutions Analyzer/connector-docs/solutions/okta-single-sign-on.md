# Okta Single Sign-On

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-03-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On) |

## Data Connectors

This solution provides **4 data connector(s)**.

### [Okta Single Sign-On](../connectors/oktasso.md)

**Publisher:** Okta

The [Okta Single Sign-On (SSO)](https://www.okta.com/products/single-sign-on/) connector provides the capability to ingest audit and event logs from the Okta API into Microsoft Sentinel. The connector provides visibility into these log types in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Okta_CL` |
| **Connector Definition Files** | [Connector_REST_API_FunctionApp_Okta.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Data%20Connectors/OktaSingleSign-On/Connector_REST_API_FunctionApp_Okta.json) |

[→ View full connector details](../connectors/oktasso.md)

### [Okta Single Sign-On (Polling CCP)](../connectors/oktasso-polling.md)

**Publisher:** Okta

The [Okta Single Sign-On (SSO)](https://www.okta.com/products/single-sign-on/) connector provides the capability to ingest audit and event logs from the Okta API into Microsoft entinel. The connector provides visibility into these log types in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `OktaNativePoller_CL` |
| **Connector Definition Files** | [azuredeploy_Okta_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Data%20Connectors/OktaNativePollerConnector/azuredeploy_Okta_native_poller_connector.json) |

[→ View full connector details](../connectors/oktasso-polling.md)

### [Okta Single Sign-On](../connectors/oktassov2.md)

**Publisher:** Microsoft

The [Okta Single Sign-On (SSO)](https://www.okta.com/products/single-sign-on/) data connector provides the capability to ingest audit and event logs from the Okta Sysem Log API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform and uses the Okta System Log API to fetch the events. The connector supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `OktaV2_CL` |
| | `Okta_CL` |
| | `signIns` |
| **Connector Definition Files** | [OktaSSOv2_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Data%20Connectors/OktaNativePollerConnectorV2/OktaSSOv2_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/oktassov2.md)

### [Okta Single Sign-On (using Azure Functions)](../connectors/oktasinglesignon%28usingazurefunctions%29.md)

**Publisher:** Okta

The [Okta Single Sign-On (SSO)](https://www.okta.com/products/single-sign-on/) connector provides the capability to ingest audit and event logs from the Okta API into Microsoft Sentinel. The connector provides visibility into these log types in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `OktaV2_CL` |
| | `Okta_CL` |
| | `signIns` |
| **Connector Definition Files** | [azuredeploy_Okta_native_poller_connector_v2.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Data%20Connectors/OktaNativePollerConnectorV2/azuredeploy_Okta_native_poller_connector_v2.json) |

[→ View full connector details](../connectors/oktasinglesignon%28usingazurefunctions%29.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OktaNativePoller_CL` | [Okta Single Sign-On (Polling CCP)](../connectors/oktasso-polling.md) |
| `OktaV2_CL` | [Okta Single Sign-On](../connectors/oktassov2.md), [Okta Single Sign-On (using Azure Functions)](../connectors/oktasinglesignon(usingazurefunctions).md) |
| `Okta_CL` | [Okta Single Sign-On](../connectors/oktasso.md), [Okta Single Sign-On](../connectors/oktassov2.md), [Okta Single Sign-On (using Azure Functions)](../connectors/oktasinglesignon(usingazurefunctions).md) |
| `signIns` | [Okta Single Sign-On (Preview)](../connectors/oktassov2.md), [Okta Single Sign-On (using Azure Functions)](../connectors/oktasinglesignon(usingazurefunctions).md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                            |
|-------------|--------------------------------|---------------------------------------------------------------|
| 3.1.2       | 06-01-2025                     | Removing Custom Entity mappings from **Analytic Rule**                         |
| 3.1.1       | 08-11-2024                     | Fixed CCP **Data Connector** connection bug                          |
| 3.1.0       | 27-11-2024                     | Fixed Solution version in Maintemplate and resolved ARM template error                           |
| 3.0.10      | 08-11-2024                     | Updated **Parser** to fix the schema                          |
| 3.0.9       | 17-10-2024                     | Updated package to fix connectivity of CCP connector |
| 3.0.8       | 14-08-2024                     | Data Connector Globally Available         |
| 3.0.7       | 25-04-2024                     | Repackaged for parser issue with old names       |
| 3.0.6       | 17-04-2024                     | Repackaged solution for parser fix   |
| 3.0.5       | 08-04-2024                     | Added Azure Deploy button for government portal deployments   |
| 3.0.4       | 18-03-2024                     | Updated description in data file, data connector and added logo for ccp data connector                    |
| 3.0.3       | 08-03-2024                     | Updated ccp with domainname in dcr, tables, name change in definition and poller                     |
| 3.0.2       | 20-02-2024                     | Updated _solutionVersion to resource specific version and repackage                    |
| 3.0.1       | 24-01-2024                     | New **Analytic Rule** added (UserSessionImpersonation.yaml)  |
| 3.0.0       | 10-10-2023                     | Manual deployment instructions updated for **Data Connector** |

[← Back to Solutions Index](../solutions-index.md)
