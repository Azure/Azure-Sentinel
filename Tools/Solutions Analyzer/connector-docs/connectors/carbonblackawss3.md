# VMware Carbon Black Cloud via AWS S3

| | |
|----------|-------|
| **Connector ID** | `carbonBlackAWSS3` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ASimAuthenticationEventLogs`](../tables-index.md#asimauthenticationeventlogs), [`ASimFileEventLogs`](../tables-index.md#asimfileeventlogs), [`ASimNetworkSessionLogs`](../tables-index.md#asimnetworksessionlogs), [`ASimProcessEventLogs`](../tables-index.md#asimprocesseventlogs), [`ASimRegistryEventLogs`](../tables-index.md#asimregistryeventlogs), [`CarbonBlack_Alerts_CL`](../tables-index.md#carbonblack_alerts_cl), [`CarbonBlack_Watchlist_CL`](../tables-index.md#carbonblack_watchlist_cl) |
| **Used in Solutions** | [VMware Carbon Black Cloud](../solutions/vmware-carbon-black-cloud.md) |
| **Connector Definition Files** | [CarbonBlackViaAWSS3_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Data%20Connectors/CarbonBlackViaAWSS3_ConnectorDefinition.json), [CarbonBlack_DataConnectorDefination.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Data%20Connectors/VMwareCarbonBlackCloud_ccp/CarbonBlack_DataConnectorDefination.json) |

The [VMware Carbon Black Cloud](https://www.vmware.com/products/carbon-black-cloud.html) via AWS S3 data connector provides the capability to ingest watchlist, alerts, auth and endpoints events via AWS S3 and stream them to ASIM normalized tables. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[← Back to Connectors Index](../connectors-index.md)
