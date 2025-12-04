# VMware Carbon Black Cloud

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [VMware Carbon Black Cloud](../connectors/vmwarecarbonblack.md)

**Publisher:** VMware

### [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md)

**Publisher:** Microsoft

The [VMware Carbon Black Cloud](https://www.vmware.com/products/carbon-black-cloud.html) via AWS S3 data connector provides the capability to ingest watchlist, alerts, auth and endpoints events via AWS S3 and stream them to ASIM normalized tables. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
| **Tables Ingested** | `ASimAuthenticationEventLogs` |
| | `ASimFileEventLogs` |
| | `ASimNetworkSessionLogs` |
| | `ASimProcessEventLogs` |
| | `ASimRegistryEventLogs` |
| | `CarbonBlack_Alerts_CL` |
| | `CarbonBlack_Watchlist_CL` |
| **Connector Definition Files** | [CarbonBlackViaAWSS3_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Data%20Connectors/CarbonBlackViaAWSS3_ConnectorDefinition.json) |
| | [CarbonBlack_DataConnectorDefination.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Data%20Connectors/VMwareCarbonBlackCloud_ccp/CarbonBlack_DataConnectorDefination.json) |

[→ View full connector details](../connectors/carbonblackawss3.md)

## Tables Reference

This solution ingests data into **10 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ASimAuthenticationEventLogs` | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) |
| `ASimFileEventLogs` | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) |
| `ASimNetworkSessionLogs` | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) |
| `ASimProcessEventLogs` | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) |
| `ASimRegistryEventLogs` | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) |
| `CarbonBlackAuditLogs_CL` | [VMware Carbon Black Cloud](../connectors/vmwarecarbonblack.md) |
| `CarbonBlackEvents_CL` | [VMware Carbon Black Cloud](../connectors/vmwarecarbonblack.md) |
| `CarbonBlackNotifications_CL` | [VMware Carbon Black Cloud](../connectors/vmwarecarbonblack.md) |
| `CarbonBlack_Alerts_CL` | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) |
| `CarbonBlack_Watchlist_CL` | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) |

[← Back to Solutions Index](../solutions-index.md)
