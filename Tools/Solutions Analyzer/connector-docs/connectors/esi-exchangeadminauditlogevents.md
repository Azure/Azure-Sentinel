# [Deprecated] Microsoft Exchange Logs and Events

| | |
|----------|-------|
| **Connector ID** | `ESI-ExchangeAdminAuditLogEvents` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`Event`](../tables-index.md#event), [`ExchangeHttpProxy_CL`](../tables-index.md#exchangehttpproxy_cl), [`MessageTrackingLog_CL`](../tables-index.md#messagetrackinglog_cl), [`SecurityEvent`](../tables-index.md#securityevent), [`W3CIISLog`](../tables-index.md#w3ciislog) |
| **Used in Solutions** | [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md) |
| **Connector Definition Files** | [ESI-ExchangeAdminAuditLogEvents.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-ExchangeAdminAuditLogEvents.json) |

Deprecated, use the 'ESI-Opt' dataconnectors. You can stream all Exchange Audit events, IIS Logs, HTTP Proxy logs and Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This is used by Microsoft Exchange Security Workbooks to provide security insights of your On-Premises Exchange environment

[← Back to Connectors Index](../connectors-index.md)
