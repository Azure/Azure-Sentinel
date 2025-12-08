# NXLog DNS Logs

| | |
|----------|-------|
| **Connector ID** | `NXLogDNSLogs` |
| **Publisher** | NXLog |
| **Tables Ingested** | [`NXLog_DNS_Server_CL`](../tables-index.md#nxlog_dns_server_cl) |
| **Used in Solutions** | [NXLogDnsLogs](../solutions/nxlogdnslogs.md) |
| **Connector Definition Files** | [NXLogDnsLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogDnsLogs/Data%20Connectors/NXLogDnsLogs.json) |

The NXLog DNS Logs data connector uses Event Tracing for Windows ([ETW](https://docs.microsoft.com/windows/apps/trace-processing/overview)) for collecting both Audit and Analytical DNS Server events. The [NXLog *im_etw* module](https://docs.nxlog.co/refman/current/im/etw.html) reads event tracing data directly for maximum efficiency, without the need to capture the event trace into an .etl file. This REST API connector can forward DNS Server events to Microsoft Sentinel in real time.

[← Back to Connectors Index](../connectors-index.md)
