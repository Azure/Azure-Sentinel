#  Microsoft Active-Directory Domain Controllers Security Event Logs

| | |
|----------|-------|
| **Connector ID** | `ESI-Opt34DomainControllersSecurityEventLogs` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`SecurityEvent`](../tables-index.md#securityevent) |
| **Used in Solutions** | [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md) |
| **Connector Definition Files** | [ESI-Opt34DomainControllersSecurityEventLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt34DomainControllersSecurityEventLogs.json) |

[Option 3 & 4] - Using Azure Monitor Agent -You can stream a part or all Domain Controllers Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Detailled documentation**: >**NOTE:** Detailled documentation on Installation procedure and usage can be found [here](https://aka.ms/MicrosoftExchangeSecurityGithub)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This solution is based on options. This allows you to choose which data will be ingest as some options can generate a very high volume of data. Depending on what you want to collect, track in your Workbooks, Analytics Rules, Hunting capabilities you will choose the option(s) you will deploy. Each options are independant for one from the other. To learn more about each option: ['Microsoft Exchange Security' wiki](https://aka.ms/ESI_DataConnectorOptions)

>This Data Connector is the **option 3 and 4** of the wiki.

**1.  Download and install the agents needed to collect logs for Microsoft Sentinel**

Type of servers (Exchange Servers, Domain Controllers linked to Exchange Servers or all Domain Controllers) depends on the option you want to deploy.
**Deploy Monitor Agents**

  This step is required only if it's the first time you onboard your Exchange Servers/Domain Controllers
**Deploy the Azure Arc Agent**
> [Learn more](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install?tabs=ARMAgentPowerShell,PowerShellWindows,PowerShellWindowsArc,CLIWindows,CLIWindowsArc)

**1. Security logs of Domain Controllers**

Select how to stream Security logs of Domain Controllers. If you want to implement Option 3, you just need to select DC on same site as Exchange Servers. If you want to implement Option 4, you can select all DCs of your forest.
**[Option 3] List only Domain Controllers on the same site as Exchange Servers for next step**

  **This limits the quantity of data injested but some incident can't be detected.**

  **[Option 4] List all Domain Controllers of your Active-Directory Forest for next step**

  **This allows collecting all security events**
**Security Event log collection**

**Data Collection Rules - Security Event logs**

  **Enable data collection rule for Security Logs**
Security Events logs are collected only from **Windows** agents.
1. Add chosen DCs on *Resources* tab.
2. Select Security log level

>  **Common level** is the minimum required. Please select 'Common' or 'All Security Events' on DCR definition.
  - **Create data collection rule**

[← Back to Connectors Index](../connectors-index.md)
