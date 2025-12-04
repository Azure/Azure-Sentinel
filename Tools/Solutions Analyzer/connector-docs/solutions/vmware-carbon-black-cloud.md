# VMware Carbon Black Cloud

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### VMware Carbon Black Cloud

**Publisher:** VMware

The [VMware Carbon Black Cloud](https://www.vmware.com/products/carbon-black-cloud.html) connector provides the capability to ingest Carbon Black data into Microsoft Sentinel. The connector provides visibility into Audit, Notification and Event logs in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

**Tables Ingested:**

- `CarbonBlackAuditLogs_CL`
- `CarbonBlackEvents_CL`
- `CarbonBlackNotifications_CL`

**Connector Definition Files:**

- [VMwareCarbonBlack_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Data%20Connectors/VMwareCarbonBlack_API_FunctionApp.json)

### VMware Carbon Black Cloud via AWS S3

**Publisher:** Microsoft

The [VMware Carbon Black Cloud](https://www.vmware.com/products/carbon-black-cloud.html) via AWS S3 data connector provides the capability to ingest watchlist, alerts, auth and endpoints events via AWS S3 and stream them to ASIM normalized tables. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

**Tables Ingested:**

- `ASimAuthenticationEventLogs`
- `ASimFileEventLogs`
- `ASimNetworkSessionLogs`
- `ASimProcessEventLogs`
- `ASimRegistryEventLogs`
- `CarbonBlack_Alerts_CL`
- `CarbonBlack_Watchlist_CL`

**Connector Definition Files:**

- [CarbonBlackViaAWSS3_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Data%20Connectors/CarbonBlackViaAWSS3_ConnectorDefinition.json)
- [CarbonBlack_DataConnectorDefination.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Data%20Connectors/VMwareCarbonBlackCloud_ccp/CarbonBlack_DataConnectorDefination.json)

## Tables Reference

This solution ingests data into **10 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ASimAuthenticationEventLogs` | VMware Carbon Black Cloud via AWS S3 |
| `ASimFileEventLogs` | VMware Carbon Black Cloud via AWS S3 |
| `ASimNetworkSessionLogs` | VMware Carbon Black Cloud via AWS S3 |
| `ASimProcessEventLogs` | VMware Carbon Black Cloud via AWS S3 |
| `ASimRegistryEventLogs` | VMware Carbon Black Cloud via AWS S3 |
| `CarbonBlackAuditLogs_CL` | VMware Carbon Black Cloud |
| `CarbonBlackEvents_CL` | VMware Carbon Black Cloud |
| `CarbonBlackNotifications_CL` | VMware Carbon Black Cloud |
| `CarbonBlack_Alerts_CL` | VMware Carbon Black Cloud via AWS S3 |
| `CarbonBlack_Watchlist_CL` | VMware Carbon Black Cloud via AWS S3 |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n