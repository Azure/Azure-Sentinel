# Microsoft Exchange Admin Audit Logs by Event Logs

| | |
|----------|-------|
| **Connector ID** | `ESI-Opt1ExchangeAdminAuditLogsByEventLogs` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`Event`](../tables-index.md#event) |
| **Used in Solutions** | [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md) |
| **Connector Definition Files** | [ESI-Opt1ExchangeAdminAuditLogsByEventLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt1ExchangeAdminAuditLogsByEventLogs.json) |

[Option 1] - Using Azure Monitor Agent - You can stream all Exchange Audit events from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This is used by Microsoft Exchange Security Workbooks to provide security insights of your On-Premises Exchange environment

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Detailled documentation**: >**NOTE:** Detailled documentation on Installation procedure and usage can be found [here](https://aka.ms/MicrosoftExchangeSecurityGithub)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This solution is based on options. This allows you to choose which data will be ingest as some options can generate a very high volume of data. Depending on what you want to collect, track in your Workbooks, Analytics Rules, Hunting capabilities you will choose the option(s) you will deploy. Each options are independant for one from the other. To learn more about each option: ['Microsoft Exchange Security' wiki](https://aka.ms/ESI_DataConnectorOptions)

>This Data Connector is the **option 1** of the wiki.

**1. Download and install the agents needed to collect logs for Microsoft Sentinel**

Type of servers (Exchange Servers, Domain Controllers linked to Exchange Servers or all Domain Controllers) depends on the option you want to deploy.
**Deploy Monitor Agents**

  This step is required only if it's the first time you onboard your Exchange Servers/Domain Controllers
**Deploy the Azure Arc Agent**
> [Learn more](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install?tabs=ARMAgentPowerShell,PowerShellWindows,PowerShellWindowsArc,CLIWindows,CLIWindowsArc)

**2. [Option 1] MS Exchange Management Log collection - MS Exchange Admin Audit event logs by Data Collection Rules**

The MS Exchange Admin Audit event logs are collected using Data Collection Rules (DCR) and allow to store all Administrative Cmdlets executed in an Exchange environment.
**DCR**

**Data Collection Rules Deployment**

  **Enable data collection rule**
>  Microsoft Exchange Admin Audit Events logs are collected only from **Windows** agents.
**Option 1 - Azure Resource Manager (ARM) Template (Prefered)**

    Use this method for automated deployment of the DCR.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESI-DCROption1-azuredeploy)
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
5. In 'Collect and deliver', add a Data Source type 'Windows Event logs' and select 'Custom' option, enter 'MSExchange Management' as expression and Add it.
6. 'Make other preferable configuration changes', if needed, then click **Create**.

    **Assign the DCR to all Exchange Servers**

    Add all your Exchange Servers to the DCR

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected. Parsers are automatically deployed with the solution. Follow the steps to create the Kusto Functions alias : [**ExchangeAdminAuditLogs**](https://aka.ms/sentinel-ESI-ExchangeCollector-ExchangeAdminAuditLogs-parser)
**Parsers are automatically deployed during Solution deployment. If you want to deploy manually, follow the steps below**

**Manual Parser Deployment**
**1. Download the Parser file**

    The latest version of the file [**ExchangeAdminAuditLogs**](https://aka.ms/sentinel-ESI-ExchangeCollector-ExchangeAdminAuditLogs-parser)

    **2. Create Parser **ExchangeAdminAuditLogs** function**

    In 'Logs' explorer of your Microsoft Sentinel's log analytics, copy the content of the file to Log explorer

    **3. Save Parser **ExchangeAdminAuditLogs** function**

    Click on save button.
 No parameter is needed for this parser.
Click save again.

[← Back to Connectors Index](../connectors-index.md)
