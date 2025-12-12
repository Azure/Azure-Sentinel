# IIS Logs of Microsoft Exchange Servers

| | |
|----------|-------|
| **Connector ID** | `ESI-Opt5ExchangeIISLogs` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`W3CIISLog`](../tables-index.md#w3ciislog) |
| **Used in Solutions** | [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md) |
| **Connector Definition Files** | [ESI-Opt5ExchangeIISLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt5ExchangeIISLogs.json) |

[Option 5] - Using Azure Monitor Agent - You can stream all IIS Logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to create custom alerts, and improve investigation.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Detailled documentation**: >**NOTE:** Detailled documentation on Installation procedure and usage can be found [here](https://aka.ms/MicrosoftExchangeSecurityGithub)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This solution is based on options. This allows you to choose which data will be ingest as some options can generate a very high volume of data. Depending on what you want to collect, track in your Workbooks, Analytics Rules, Hunting capabilities you will choose the option(s) you will deploy. Each options are independant for one from the other. To learn more about each option: ['Microsoft Exchange Security' wiki](https://aka.ms/ESI_DataConnectorOptions)

>This Data Connector is the **option 5** of the wiki.

**1.  Download and install the agents needed to collect logs for Microsoft Sentinel**

Type of servers (Exchange Servers, Domain Controllers linked to Exchange Servers or all Domain Controllers) depends on the option you want to deploy.
**Deploy Monitor Agents**

  This step is required only if it's the first time you onboard your Exchange Servers/Domain Controllers
**Deploy the Azure Arc Agent**
> [Learn more](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install?tabs=ARMAgentPowerShell,PowerShellWindows,PowerShellWindowsArc,CLIWindows,CLIWindowsArc)

**1. [Option 5] IIS logs of Exchange Servers**

Select how to stream IIS logs of Exchange Servers
**Enable data collection rule**

  > IIS logs are collected only from **Windows** agents.
  > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `AdminAuditEvents`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.
**Option 1 - Azure Resource Manager (ARM) Template (Preferred Method)**

    Use this method for automated deployment of the DCE and DCR.
**A. Create DCE (If not already created for Exchange Servers)**

      1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESI-DCEExchangeServers)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. You can change the proposed name of the DCE.
5.  Click **Create** to deploy.

      **B. Deploy Data Connection Rule**

      1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESI-DCROption5-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID** 'and/or Other required fields'.
>4.  Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5.  Click **Purchase** to deploy.

    **Option 2 - Manual Deployment of Azure Automation**

    Use the following step-by-step instructions to deploy manually a Data Collection Rule.
**A. Create DCE (If not already created for Exchange Servers)**

      1.  From the Azure Portal, navigate to [Azure Data collection Endpoint](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/dataCollectionEndpoints).
2. Click **+ Create** at the top.
3. In the **Basics** tab, fill the required fields and give a name to the DCE. 
3. 'Make other preferable configuration changes', if needed, then click **Create**.

      **B. Create DCR, Type IIS log**

      1.  From the Azure Portal, navigate to [Azure Data collection rules](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/dataCollectionRules).
2. Click **+ Create** at the top.
3. In the **Basics** tab, fill the required fields, Select Windows as platform type and give a name to the DCR. Select the created DCE. 
4. In the **Resources** tab, enter you Exchange Servers.
5. In 'Collect and deliver', add a Data Source type 'IIS logs' (Do not enter a path if IIS Logs path is configured by default). Click on 'Add data source'
6. 'Make other preferable configuration changes', if needed, then click **Create**.

    **Assign the DCR to all Exchange Servers**

    Add all your Exchange Servers to the DCR

[← Back to Connectors Index](../connectors-index.md)
