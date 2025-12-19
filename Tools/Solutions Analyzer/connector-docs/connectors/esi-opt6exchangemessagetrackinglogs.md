# Microsoft Exchange Message Tracking Logs

| | |
|----------|-------|
| **Connector ID** | `ESI-Opt6ExchangeMessageTrackingLogs` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`MessageTrackingLog_CL`](../tables-index.md#messagetrackinglog_cl) |
| **Used in Solutions** | [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md) |
| **Connector Definition Files** | [ESI-Opt6ExchangeMessageTrackingLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt6ExchangeMessageTrackingLogs.json) |

[Option 6] - Using Azure Monitor Agent - You can stream all Exchange Message Tracking from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. Those logs can be used to track the flow of messages in your Exchange environment. This data connector is based on the option 6 of the [Microsoft Exchange Security wiki](https://aka.ms/ESI_DataConnectorOptions).

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

>This Data Connector is the **option 6** of the wiki.

**1.  Download and install the agents needed to collect logs for Microsoft Sentinel**

Type of servers (Exchange Servers, Domain Controllers linked to Exchange Servers or all Domain Controllers) depends on the option you want to deploy.
**Deploy Monitor Agents**

  This step is required only if it's the first time you onboard your Exchange Servers/Domain Controllers
**Deploy the Azure Arc Agent**
> [Learn more](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install?tabs=ARMAgentPowerShell,PowerShellWindows,PowerShellWindowsArc,CLIWindows,CLIWindowsArc)

**2. Message Tracking of Exchange Servers**

Select how to stream Message Tracking of Exchange Servers
**Data Collection Rules - When Azure Monitor Agent is used**

  **Enable data collection rule**
> Message Tracking are collected only from **Windows** agents.
**Option 1 - Azure Resource Manager (ARM) Template**

    Use this method for automated deployment of the DCE and DCR.
**A. Create DCE (If not already created for Exchange Servers)**

      1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESI-DCEExchangeServers)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. You can change the proposed name of the DCE.
5.  Click **Create** to deploy.

      **B. Deploy Data Connection Rule and Custom Table**

      1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESI-DCROption6-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID** 'and/or Other required fields'.
>4.  Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5.  Click **Purchase** to deploy.

    **Option 2 - Manual Deployment of Azure Automation**

    Use the following step-by-step instructions to deploy manually a Data Collection Rule.
**Create Custom Table - Explanation**

      The Custom Table can't be created using the Azure Portal. You need to use an ARM template, a PowerShell Script or another method [described here](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/create-custom-table?tabs=azure-powershell-1%2Cazure-portal-2%2Cazure-portal-3#create-a-custom-table).

      **Create Custom Table using an ARM Template**

      1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESI-MessageTrackingCustomTable)
2. Select the preferred **Subscription**, **Resource Group**, **Location** and **Analytic Workspace Name**. 
3.  Click **Create** to deploy.

      **Create Custom Table using PowerShell in Cloud Shell**

      1.  From the Azure Portal, open a Cloud Shell.
2. Copy and paste and Execute the following script in the Cloud Shell to create the table.
		$tableParams = @'
		{
			"properties": {
				"schema": {
					   "name": "MessageTrackingLog_CL",
					   "columns": [
								{
									"name": "directionality",
									"type": "string"
								},
								{
									"name": "reference",
									"type": "string"
								},
								{
									"name": "source",
									"type": "string"
								},
								{
									"name": "TimeGenerated",
									"type": "datetime"
								},
								{
									"name": "clientHostname",
									"type": "string"
								},
								{
									"name": "clientIP",
									"type": "string"
								},
								{
									"name": "connectorId",
									"type": "string"
								},
								{
									"name": "customData",
									"type": "string"
								},
								{
									"name": "eventId",
									"type": "string"
								},
								{
									"name": "internalMessageId",
									"type": "string"
								},
								{
									"name": "logId",
									"type": "string"
								},
								{
									"name": "messageId",
									"type": "string"
								},
								{
									"name": "messageInfo",
									"type": "string"
								},
								{
									"name": "messageSubject",
									"type": "string"
								},
								{
									"name": "networkMessageId",
									"type": "string"
								},
								{
									"name": "originalClientIp",
									"type": "string"
								},
								{
									"name": "originalServerIp",
									"type": "string"
								},
								{
									"name": "recipientAddress",
									"type": "string"
								},
								{
									"name": "recipientCount",
									"type": "string"
								},
								{
									"name": "recipientStatus",
									"type": "string"
								},
								{
									"name": "relatedRecipientAddress",
									"type": "string"
								},
								{
									"name": "returnPath",
									"type": "string"
								},
								{
									"name": "senderAddress",
									"type": "string"
								},
								{
									"name": "senderHostname",
									"type": "string"
								},
								{
									"name": "serverIp",
									"type": "string"
								},
								{
									"name": "sourceContext",
									"type": "string"
								},
								{
									"name": "schemaVersion",
									"type": "string"
								},
								{
									"name": "messageTrackingTenantId",
									"type": "string"
								},
								{
									"name": "totalBytes",
									"type": "string"
								},
								{
									"name": "transportTrafficType",
									"type": "string"
								},
								{
									"name": "FilePath",
									"type": "string"
								}
							]
				}
			}
		}
		'@
3.  Copy, Replace, Paste and execute the following parameters with your own values:
		$SubscriptionID = 'YourGUID'
		$ResourceGroupName = 'YourResourceGroupName'
		$WorkspaceName = 'YourWorkspaceName'
4.  Execute the Following Cmdlet to create the table:
		Invoke-AzRestMethod -Path "/subscriptions/$SubscriptionID/resourcegroups/$ResourceGroupName/providers/microsoft.operationalinsights/workspaces/$WorkspaceName/tables/MessageTrackingLog_CL?api-version=2021-12-01-preview" -Method PUT -payload $tableParams
**A. Create DCE (If not already created for Exchange Servers)**

      1.  From the Azure Portal, navigate to [Azure Data collection Endpoint](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/dataCollectionEndpoints).
2. Click **+ Create** at the top.
3. In the **Basics** tab, fill the required fields and give a name to the DCE, like ESI-ExchangeServers. 
3. 'Make other preferable configuration changes', if needed, then click **Create**.

      **B. Create a DCR, Type Custom log**

      1.  From the Azure Portal, navigate to [Azure Data collection rules](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/dataCollectionRules).
2. Click on 'Create' button.
3. On 'Basics' tab, fill the Rule name like **DCR-Option6-MessageTrackingLogs**, select the 'Data Collection Endpoint' with the previously created endpoint and fill other parameters.
4. In the **Resources** tab, add your Exchange Servers.
5. In **Collect and Deliver**, add a Data Source type 'Custom Text logs' and enter 'C:\Program Files\Microsoft\Exchange Server\V15\TransportRoles\Logs\MessageTracking\*.log' in file pattern, 'MessageTrackingLog_CL' in Table Name.
6.in Transform field, enter the following KQL request :
		source | extend d = split(RawData,',') | extend TimeGenerated =todatetime(d[0]) ,clientIP =tostring(d[1]) ,clientHostname =tostring(d[2]) ,serverIp=tostring(d[3]) ,senderHostname=tostring(d[4]) ,sourceContext=tostring(d[5]) ,connectorId =tostring(d[6]) ,source=tostring(d[7]) ,eventId =tostring(d[8]) ,internalMessageId =tostring(d[9]) ,messageId =tostring(d[10]) ,networkMessageId =tostring(d[11]) ,recipientAddress=tostring(d[12]) ,recipientStatus=tostring(d[13]) ,totalBytes=tostring(d[14]) ,recipientCount=tostring(d[15]) ,relatedRecipientAddress=tostring(d[16]) ,reference=tostring(d[17]) ,messageSubject =tostring(d[18]) ,senderAddress=tostring(d[19]) ,returnPath=tostring(d[20]) ,messageInfo =tostring(d[21]) ,directionality=tostring(d[22]) ,messageTrackingTenantId =tostring(d[23]) ,originalClientIp =tostring(d[24]) ,originalServerIp =tostring(d[25]) ,customData=tostring(d[26]) ,transportTrafficType =tostring(d[27]) ,logId =tostring(d[28]) ,schemaVersion=tostring(d[29]) | project-away d,RawData
 and click on 'Destination'.
6. In 'Destination', add a destination and select the Workspace where you have previously created the Custom Table 
7. Click on 'Add data source'.
8. Fill other required parameters and tags and create the DCR

    **Assign the DCR to all Exchange Servers**

    Add all your Exchange Servers to the DCR

[← Back to Connectors Index](../connectors-index.md)
