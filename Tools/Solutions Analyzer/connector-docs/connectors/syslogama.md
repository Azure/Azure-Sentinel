# Syslog via AMA

| | |
|----------|-------|
| **Connector ID** | `SyslogAma` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [Syslog](../solutions/syslog.md) |
| **Connector Definition Files** | [template_SyslogAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Data%20Connectors/template_SyslogAma.json) |

Syslog is an event logging protocol that is common to Linux. Applications will send messages that may be stored on the local machine or delivered to a Syslog collector. When the Agent for Linux is installed, it configures the local Syslog daemon to forward messages to the agent. The agent then sends the message to the workspace.



[Learn more >](https://aka.ms/sysLogInfo)

[← Back to Connectors Index](../connectors-index.md)
