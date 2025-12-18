# Microsoft Exchange Logs and Events

| | |
|----------|-------|
| **Connector ID** | `ESI-Opt2ExchangeServersEventLogs` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`Event`](../tables-index.md#event) |
| **Used in Solutions** | [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md) |
| **Connector Definition Files** | [ESI-Opt2ExchangeServersEventLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt2ExchangeServersEventLogs.json) |

[Option 2] - Using Azure Monitor Agent - You can stream all Exchange Security & Application Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Azure Log Analytics will be deprecated**: Azure Log Analytics will be deprecated, to collect data from non-Azure VMs, Azure Arc is recommended. [Learn more](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install?tabs=ARMAgentPowerShell,PowerShellWindows,PowerShellWindowsArc,CLIWindows,CLIWindowsArc)
- **Detailled documentation**: >**NOTE:** Detailled documentation on Installation procedure and usage can be found [here](https://aka.ms/MicrosoftExchangeSecurityGithub)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This solution is based on options. This allows you to choose which data will be ingest as some options can generate a very high volume of data. Depending on what you want to collect, track in your Workbooks, Analytics Rules, Hunting capabilities you will choose the option(s) you will deploy. Each options are independant for one from the other. To learn more about each option: ['Microsoft Exchange Security' wiki](https://aka.ms/ESI_DataConnectorOptions)

>This Data Connector is the **option 2** of the wiki.

**1.  Download and install the agents needed to collect logs for Microsoft Sentinel**

Type of servers (Exchange Servers, Domain Controllers linked to Exchange Servers or all Domain Controllers) depends on the option you want to deploy.
**Deploy Monitor Agents**

  This step is required only if it's the first time you onboard your Exchange Servers/Domain Controllers
**Deploy the Azure Arc Agent**
> [Learn more](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install?tabs=ARMAgentPowerShell,PowerShellWindows,PowerShellWindowsArc,CLIWindows,CLIWindowsArc)

**2. [Option 2] Security/Application/System logs of Exchange Servers**

The Security/Application/System logs of Exchange Servers are collected using Data Collection Rules (DCR).
**Security Event log collection**

**Data Collection Rules - Security Event logs**

  **Enable data collection rule for Security Logs**
Security Events logs are collected only from **Windows** agents.
1. Add Exchange Servers on *Resources* tab.
2. Select Security log level

>  **Common level** is the minimum required. Please select 'Common' or 'All Security Events' on DCR definition.
  - **Create data collection rule**
**Application and System Event log collection**

**Enable data collection rule**

  >  Application and System Events logs are collected only from **Windows** agents.
**Option 1 - Azure Resource Manager (ARM) Template (Prefered method)**

    Use this method for automated deployment of the DCR.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESI-DCROption2-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace Name** 'and/or Other required fields'.
>4.  Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5.  Click **Purchase** to deploy.

    **Option 2 - Manual Deployment of Azure Automation**

    Use the following step-by-step instructions to deploy manually a Data Collection Rule.
**A. Create DCR, Type Event log**

      1.  From the Azure Portal, navigate to [Azure Data collection rules](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/dataCollectionRules).
2. Click **+ Create** at the top.
3. In the **Basics** tab, fill the required fields, Select Windows as platform type and give a name to the DCR. 
4. In the **Resources** tab, enter you Exchange Servers.
5. In 'Collect and deliver', add a Data Source type 'Windows Event logs' and select 'Basic' option.
6. For Application, select 'Critical', 'Error' and 'Warning'. For System, select Critical/Error/Warning/Information. 
7. 'Make other preferable configuration changes', if needed, then click **Create**.

    **Assign the DCR to all Exchange Servers**

    Add all your Exchange Servers to the DCR

[← Back to Connectors Index](../connectors-index.md)
