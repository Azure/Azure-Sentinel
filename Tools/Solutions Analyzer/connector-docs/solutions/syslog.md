# Syslog

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Syslog via Legacy Agent](../connectors/syslog.md)

**Publisher:** Microsoft

### [Syslog via AMA](../connectors/syslogama.md)

**Publisher:** Microsoft

Syslog is an event logging protocol that is common to Linux. Applications will send messages that may be stored on the local machine or delivered to a Syslog collector. When the Agent for Linux is installed, it configures the local Syslog daemon to forward messages to the agent. The agent then sends the message to the workspace.



[Learn more >](https://aka.ms/sysLogInfo)

**Permissions:**

**Resource Provider Permissions:**
- **Workspace data sources** (Workspace): read and write permissions.

**Custom Permissions:**

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Enable data collection rule​**

You can collect Syslog events from your local machine by installing the agent on it. You can also collect Syslog generated on a different source by running the installation script below on the local machine, where the agent is installed.

>  Syslog logs are collected only from **Linux** agents.
- Configure SysLogAma data connector

- **Create data collection rule**

**2. Run the following command to install and apply the Syslog collector:**

> To collect logs generated on a different machine run this script on the machine where the agent is installed.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [template_SyslogAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Data%20Connectors/template_SyslogAma.json) |

[→ View full connector details](../connectors/syslogama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [Syslog via AMA](../connectors/syslogama.md), [Syslog via Legacy Agent](../connectors/syslog.md) |

[← Back to Solutions Index](../solutions-index.md)
