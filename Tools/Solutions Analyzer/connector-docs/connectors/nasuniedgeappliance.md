# [Deprecated] Nasuni Edge Appliance

| | |
|----------|-------|
| **Connector ID** | `NasuniEdgeAppliance` |
| **Publisher** | Nasuni |
| **Tables Ingested** | [`Nasuni`](../tables-index.md#nasuni), [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [Nasuni](../solutions/nasuni.md) |
| **Connector Definition Files** | [Nasuni%20Data%20Connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Nasuni/Data%20Connectors/Nasuni%20Data%20Connector.json) |

The [Nasuni](https://www.nasuni.com/) connector allows you to easily connect your Nasuni Edge Appliance Notifications and file system audit logs with Microsoft Sentinel. This gives you more insight into activity within your Nasuni infrastructure and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Install and onboard the agent for Linux**

Typically, you should install the agent on a different computer from the one on which the logs are generated.

>  Syslog logs are collected only from **Linux** agents.
**Choose where to install the agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**2. Configure the logs to be collected**

Follow the configuration steps below to configure your Linux machine to send Nasuni event information to Microsoft Sentinel. Refer to the [Azure Monitor Agent documenation](https://learn.microsoft.com/en-us/azure/azure-monitor/agents/agents-overview) for additional details on these steps.
Configure the facilities you want to collect and their severities.
1. Select the link below to open your workspace agents configuration, and select the Syslog tab.
2. Select Add facility and choose from the drop-down list of facilities. Repeat for all the facilities you want to add.
3. Mark the check boxes for the desired severities for each facility.
4. Click Apply.
- **Open Syslog settings**

**3. Configure Nasuni Edge Appliance settings**

Follow the instructions in the [Nasuni Management Console Guide](https://view.highspot.com/viewer/629a633ae5b4caaf17018daa?iid=5e6fbfcbc7143309f69fcfcf) to configure Nasuni Edge Appliances to forward syslog events. Use the IP address or hostname of the Linux device running the Azure Monitor Agent in the Servers configuration field for the syslog settings.

[← Back to Connectors Index](../connectors-index.md)
