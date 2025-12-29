# Syslog via AMA

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `SyslogAma` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [Syslog](../solutions/syslog.md) |
| **Collection Method** | AMA |
| **Connector Definition Files** | [template_SyslogAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Data%20Connectors/template_SyslogAma.json) |

Syslog is an event logging protocol that is common to Linux. Applications will send messages that may be stored on the local machine or delivered to a Syslog collector. When the Agent for Linux is installed, it configures the local Syslog daemon to forward messages to the agent. The agent then sends the message to the workspace.



[Learn more >](https://aka.ms/sysLogInfo)

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`Syslog`](../tables/syslog.md) | — | ✓ |

> 💡 **Tip:** Tables with Ingestion API support allow data ingestion via the [Azure Monitor Data Collector API](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview), which also enables custom transformations during ingestion.

## Permissions

**Resource Provider Permissions:**
- **Workspace data sources** (Workspace): read and write permissions.

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Enable data collection rule​**

You can collect Syslog events from your local machine by installing the agent on it. You can also collect Syslog generated on a different source by running the installation script below on the local machine, where the agent is installed.

>  Syslog logs are collected only from **Linux** agents.
- Configure SysLogAma data connector

- **Create data collection rule**

**2. Run the following command to install and apply the Syslog collector:**

> To collect logs generated on a different machine run this script on the machine where the agent is installed.

[← Back to Connectors Index](../connectors-index.md)
