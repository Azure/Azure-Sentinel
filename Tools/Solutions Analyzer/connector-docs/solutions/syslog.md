# Syslog

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### Syslog via Legacy Agent

**Publisher:** Microsoft

Syslog is an event logging protocol that is common to Linux. Applications will send messages that may be stored on the local machine or delivered to a Syslog collector. When the Agent for Linux is installed, it configures the local Syslog daemon to forward messages to the agent. The agent then sends the message to the workspace.



[Learn more >](https://aka.ms/sysLogInfo)

**Tables Ingested:**

- `Syslog`

**Connector Definition Files:**

- [template_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Data%20Connectors/template_Syslog.json)

### Syslog via AMA

**Publisher:** Microsoft

Syslog is an event logging protocol that is common to Linux. Applications will send messages that may be stored on the local machine or delivered to a Syslog collector. When the Agent for Linux is installed, it configures the local Syslog daemon to forward messages to the agent. The agent then sends the message to the workspace.



[Learn more >](https://aka.ms/sysLogInfo)

**Tables Ingested:**

- `Syslog`

**Connector Definition Files:**

- [template_SyslogAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Data%20Connectors/template_SyslogAma.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | Syslog via AMA, Syslog via Legacy Agent |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n