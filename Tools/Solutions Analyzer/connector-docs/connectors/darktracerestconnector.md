# Darktrace Connector for Microsoft Sentinel REST API

| | |
|----------|-------|
| **Connector ID** | `DarktraceRESTConnector` |
| **Publisher** | Darktrace |
| **Tables Ingested** | [`darktrace_model_alerts_CL`](../tables-index.md#darktrace_model_alerts_cl) |
| **Used in Solutions** | [Darktrace](../solutions/darktrace.md) |
| **Connector Definition Files** | [DarktraceConnectorRESTAPI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Darktrace/Data%20Connectors/DarktraceConnectorRESTAPI.json) |

The Darktrace REST API connector pushes real-time events from Darktrace to Microsoft Sentinel and is designed to be used with the Darktrace Solution for Sentinel. The connector writes logs to a custom log table titled "darktrace_model_alerts_CL"; Model Breaches, AI Analyst Incidents, System Alerts and Email Alerts can be ingested - additional filters can be set up on the Darktrace System Configuration page. Data is pushed to Sentinel from Darktrace masters.

[← Back to Connectors Index](../connectors-index.md)
