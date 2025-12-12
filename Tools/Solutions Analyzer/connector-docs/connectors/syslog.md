# Syslog via Legacy Agent

| | |
|----------|-------|
| **Connector ID** | `Syslog` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [Syslog](../solutions/syslog.md) |
| **Connector Definition Files** | [template_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Data%20Connectors/template_Syslog.json) |

Syslog is an event logging protocol that is common to Linux. Applications will send messages that may be stored on the local machine or delivered to a Syslog collector. When the Agent for Linux is installed, it configures the local Syslog daemon to forward messages to the agent. The agent then sends the message to the workspace.



[Learn more >](https://aka.ms/sysLogInfo)

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Install and onboard the agent for Linux**

You can collect Syslog events from your local machine by installing the agent on it. You can also collect Syslog generated on a different source by running the installation script below on the local machine, where the agent is installed.

>  Syslog logs are collected only from **Linux** agents.
**Choose where to install the agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**2. Configure the logs to be collected**

Configure the facilities you want to collect and their severities.

1.  Select the link below to open your workspace **agents configuration**, and select the **Syslog** tab.
2.  Select **Add facility** and choose from the drop-down list of facilities. Repeat for all the facilities you want to add.
3.  Mark the check boxes for the desired severities for each facility.
4.  Click **Apply**.
- **Open Syslog settings**

[← Back to Connectors Index](../connectors-index.md)
