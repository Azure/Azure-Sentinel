# Check Point CloudGuard CNAPP Connector for Microsoft Sentinel

| | |
|----------|-------|
| **Connector ID** | `CloudGuardCCPDefinition` |
| **Publisher** | CheckPoint |
| **Tables Ingested** | [`CloudGuard_SecurityEvents_CL`](../tables-index.md#cloudguard_securityevents_cl) |
| **Used in Solutions** | [Check Point CloudGuard CNAPP](../solutions/check-point-cloudguard-cnapp.md) |
| **Connector Definition Files** | [CloudGuard_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point%20CloudGuard%20CNAPP/Data%20Connectors/CloudGuard_ccp/CloudGuard_DataConnectorDefinition.json) |

The [CloudGuard](https://sc1.checkpoint.com/documents/CloudGuard_Dome9/Documentation/Overview/CloudGuard-CSPM-Introduction.htm?cshid=help_center_documentation) data connector enables the ingestion of security events from the CloudGuard API into Microsoft Sentinel™, using Microsoft Sentinel’s Codeless Connector Platform. The connector supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) which parses incoming security event data into custom columns. This pre-parsing process eliminates the need for query-time parsing, resulting in improved performance for data queries.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **CloudGuard API Key**: Refer to the instructions provided [here](https://sc1.checkpoint.com/documents/CloudGuard_Dome9/Documentation/Settings/Users-Roles.htm#add_service) to generate an API key.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect CloudGuard Security Events to Microsoft Sentinel**

To enable the CloudGuard connector for Microsoft Sentinel, enter the required information below and select Connect.
>
- **API Key ID**: api_key
- **API Key Secret**: (password field)
- **CloudGuard Endpoint URL**: e.g. https://api.dome9.com
- **Filter**: Paste filter from CloudGuard
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
