# OneLogin IAM Platform (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `OneLoginIAMLogsCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`OneLoginEventsV2_CL`](../tables-index.md#onelogineventsv2_cl), [`OneLoginUsersV2_CL`](../tables-index.md#oneloginusersv2_cl) |
| **Used in Solutions** | [OneLoginIAM](../solutions/oneloginiam.md) |
| **Connector Definition Files** | [OneLoginIAMLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneLoginIAM/Data%20Connectors/OneLoginIAMLogs_ccp/OneLoginIAMLogs_ConnectorDefinition.json) |

The [OneLogin](https://www.onelogin.com/) data connector provides the capability to ingest common OneLogin IAM Platform events into Microsoft Sentinel through REST API by using OneLogin [Events API](https://developers.onelogin.com/api-docs/1/events/get-events) and OneLogin [Users API](https://developers.onelogin.com/api-docs/1/users/get-users). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[← Back to Connectors Index](../connectors-index.md)
