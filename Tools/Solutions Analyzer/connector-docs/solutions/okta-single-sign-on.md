# Okta Single Sign-On

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-03-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [Okta Single Sign-On](../connectors/oktasso.md)

**Publisher:** Okta

### [Okta Single Sign-On (Polling CCP)](../connectors/oktasso-polling.md)

**Publisher:** Okta

### [Okta Single Sign-On](../connectors/oktassov2.md)

**Publisher:** Microsoft

The [Okta Single Sign-On (SSO)](https://www.okta.com/products/single-sign-on/) data connector provides the capability to ingest audit and event logs from the Okta Sysem Log API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform and uses the Okta System Log API to fetch the events. The connector supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

| | |
|--------------------------|---|
| **Tables Ingested** | `OktaV2_CL` |
| | `Okta_CL` |
| | `signIns` |
| **Connector Definition Files** | [OktaSSOv2_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Data%20Connectors/OktaNativePollerConnectorV2/OktaSSOv2_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/oktassov2.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OktaNativePoller_CL` | [Okta Single Sign-On (Polling CCP)](../connectors/oktasso-polling.md) |
| `OktaV2_CL` | [Okta Single Sign-On](../connectors/oktassov2.md) |
| `Okta_CL` | [Okta Single Sign-On](../connectors/oktasso.md), [Okta Single Sign-On](../connectors/oktassov2.md) |
| `signIns` | [Okta Single Sign-On (Preview)](../connectors/oktassov2.md) |

[← Back to Solutions Index](../solutions-index.md)
