# Microsoft Exchange Security - Exchange On-Premises

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-12-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises) |

## Data Connectors

This solution provides **8 data connector(s)**.

### [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md)

**Publisher:** Microsoft

### [Exchange Security Insights On-Premises Collector](../connectors/esi-exchangeonpremisescollector.md)

**Publisher:** Microsoft

### [Microsoft Exchange Admin Audit Logs by Event Logs](../connectors/esi-opt1exchangeadminauditlogsbyeventlogs.md)

**Publisher:** Microsoft

### [Microsoft Exchange Logs and Events](../connectors/esi-opt2exchangeserverseventlogs.md)

**Publisher:** Microsoft

### [ Microsoft Active-Directory Domain Controllers Security Event Logs](../connectors/esi-opt34domaincontrollerssecurityeventlogs.md)

**Publisher:** Microsoft

### [IIS Logs of Microsoft Exchange Servers](../connectors/esi-opt5exchangeiislogs.md)

**Publisher:** Microsoft

### [Microsoft Exchange Message Tracking Logs](../connectors/esi-opt6exchangemessagetrackinglogs.md)

**Publisher:** Microsoft

### [Microsoft Exchange HTTP Proxy Logs](../connectors/esi-opt7exchangehttpproxylogs.md)

**Publisher:** Microsoft

[Option 7] - Using Azure Monitor Agent - You can stream HTTP Proxy logs and Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you create custom alerts, and improve investigation. [Learn more](https://aka.ms/ESI_DataConnectorOptions)

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Azure Log Analytics will be deprecated**: Azure Log Analytics will be deprecated, to collect data from non-Azure VMs, Azure Arc is recommended. [Learn more](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install?tabs=ARMAgentPowerShell,PowerShellWindows,PowerShellWindowsArc,CLIWindows,CLIWindowsArc)
- **Detailled documentation**: >**NOTE:** Detailled documentation on Installation procedure and usage can be found [here](https://aka.ms/MicrosoftExchangeSecurityGithub)

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This solution is based on options. This allows you to choose which data will be ingest as some options can generate a very high volume of data. Depending on what you want to collect, track in your Workbooks, Analytics Rules, Hunting capabilities you will choose the option(s) you will deploy. Each options are independant for one from the other. To learn more about each option: ['Microsoft Exchange Security' wiki](https://aka.ms/ESI_DataConnectorOptions)

>This Data Connector is the **option 7** of the wiki.

**1.  Download and install the agents needed to collect logs for Microsoft Sentinel**

Type of servers (Exchange Servers, Domain Controllers linked to Exchange Servers or all Domain Controllers) depends on the option you want to deploy.
**Deploy Monitor Agents**

  This step is required only if it's the first time you onboard your Exchange Servers/Domain Controllers
**Deploy the Azure Arc Agent**
> [Learn more](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install?tabs=ARMAgentPowerShell,PowerShellWindows,PowerShellWindowsArc,CLIWindows,CLIWindowsArc)

**2. [Option 7] HTTP Proxy of Exchange Servers**

Select how to stream HTTP Proxy of Exchange Servers
**Data Collection Rules - When Azure Monitor Agent is used**

  **Enable data collection rule**
> Message Tracking are collected only from **Windows** agents.
**Option 1 - Azure Resource Manager (ARM) Template (Prefered Method)**

    Use this method for automated deployment of the DCE and DCR.
**A. Create DCE (If not already created for Exchange Servers)**

      1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESI-DCEExchangeServers)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. You can change the proposed name of the DCE.
5.  Click **Create** to deploy.

      **B. Deploy Data Connection Rule**

      1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESI-DCROption7-azuredeploy)
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

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ESI-HTTPProxyCustomTable)
2. Select the preferred **Subscription**, **Resource Group**, **Location** and **Analytic Workspace Name**. 
3.  Click **Create** to deploy.

      **Create Custom Table using PowerShell in Cloud Shell**

      1.  From the Azure Portal, open a Cloud Shell.
2. Copy and paste and Execute the following script in the Cloud Shell to create the table.
		$tableParams = @'
		{
			"properties": {
				 "schema": {
						"name": "ExchangeHttpProxy_CL",
						"columns": [
								{
									"name": "AccountForestLatencyBreakup",
									"type": "string"
								},
								{
									"name": "ActivityContextLifeTime",
									"type": "string"
								},
								{
									"name": "ADLatency",
									"type": "string"
								},
								{
									"name": "AnchorMailbox",
									"type": "string"
								},
								{
									"name": "AuthenticatedUser",
									"type": "string"
								},
								{
									"name": "AuthenticationType",
									"type": "string"
								},
								{
									"name": "AuthModulePerfContext",
									"type": "string"
								},
								{
									"name": "BackEndCookie",
									"type": "string"
								},
								{
									"name": "BackEndGenericInfo",
									"type": "string"
								},
								{
									"name": "BackendProcessingLatency",
									"type": "string"
								},
								{
									"name": "BackendReqInitLatency",
									"type": "string"
								},
								{
									"name": "BackendReqStreamLatency",
									"type": "string"
								},
								{
									"name": "BackendRespInitLatency",
									"type": "string"
								},
								{
									"name": "BackendRespStreamLatency",
									"type": "string"
								},
								{
									"name": "BackEndStatus",
									"type": "string"
								},
								{
									"name": "BuildVersion",
									"type": "string"
								},
								{
									"name": "CalculateTargetBackEndLatency",
									"type": "string"
								},
								{
									"name": "ClientIpAddress",
									"type": "string"
								},
								{
									"name": "ClientReqStreamLatency",
									"type": "string"
								},
								{
									"name": "ClientRequestId",
									"type": "string"
								},
								{
									"name": "ClientRespStreamLatency",
									"type": "string"
								},
								{
									"name": "CoreLatency",
									"type": "string"
								},
								{
									"name": "DatabaseGuid",
									"type": "string"
								},
								{
									"name": "EdgeTraceId",
									"type": "string"
								},
								{
									"name": "ErrorCode",
									"type": "string"
								},
								{
									"name": "GenericErrors",
									"type": "string"
								},
								{
									"name": "GenericInfo",
									"type": "string"
								},
								{
									"name": "GlsLatencyBreakup",
									"type": "string"
								},
								{
									"name": "HandlerCompletionLatency",
									"type": "string"
								},
								{
									"name": "HandlerToModuleSwitchingLatency",
									"type": "string"
								},
								{
									"name": "HttpPipelineLatency",
									"type": "string"
								},
								{
									"name": "HttpProxyOverhead",
									"type": "string"
								},
								{
									"name": "HttpStatus",
									"type": "string"
								},
								{
									"name": "IsAuthenticated",
									"type": "string"
								},
								{
									"name": "KerberosAuthHeaderLatency",
									"type": "string"
								},
								{
									"name": "MajorVersion",
									"type": "string"
								},
								{
									"name": "Method",
									"type": "string"
								},
								{
									"name": "MinorVersion",
									"type": "string"
								},
								{
									"name": "ModuleToHandlerSwitchingLatency",
									"type": "string"
								},
								{
									"name": "Organization",
									"type": "string"
								},
								{
									"name": "PartitionEndpointLookupLatency",
									"type": "string"
								},
								{
									"name": "Protocol",
									"type": "string"
								},
								{
									"name": "ProtocolAction",
									"type": "string"
								},
								{
									"name": "ProxyAction",
									"type": "string"
								},
								{
									"name": "ProxyTime",
									"type": "string"
								},
								{
									"name": "RequestBytes",
									"type": "string"
								},
								{
									"name": "RequestHandlerLatency",
									"type": "string"
								},
								{
									"name": "RequestId",
									"type": "string"
								},
								{
									"name": "ResourceForestLatencyBreakup",
									"type": "string"
								},
								{
									"name": "ResponseBytes",
									"type": "string"
								},
								{
									"name": "RevisionVersion",
									"type": "string"
								},
								{
									"name": "RouteRefresherLatency",
									"type": "string"
								},
								{
									"name": "RoutingHint",
									"type": "string"
								},
								{
									"name": "RoutingLatency",
									"type": "string"
								},
								{
									"name": "RoutingStatus",
									"type": "string"
								},
								{
									"name": "RoutingType",
									"type": "string"
								},
								{
									"name": "ServerHostName",
									"type": "string"
								},
								{
									"name": "ServerLocatorHost",
									"type": "string"
								},
								{
									"name": "ServerLocatorLatency",
									"type": "string"
								},
								{
									"name": "SharedCacheLatencyBreakup",
									"type": "string"
								},
								{
									"name": "TargetOutstandingRequests",
									"type": "string"
								},
								{
									"name": "TargetServer",
									"type": "string"
								},
								{
									"name": "TargetServerVersion",
									"type": "string"
								},
								{
									"name": "TotalAccountForestLatency",
									"type": "string"
								},
								{
									"name": "TotalGlsLatency",
									"type": "string"
								},
								{
									"name": "TotalRequestTime",
									"type": "string"
								},
								{
									"name": "TotalResourceForestLatency",
									"type": "string"
								},
								{
									"name": "TotalSharedCacheLatency",
									"type": "string"
								},
								{
									"name": "UrlHost",
									"type": "string"
								},
								{
									"name": "UrlQuery",
									"type": "string"
								},
								{
									"name": "UrlStem",
									"type": "string"
								},
								{
									"name": "UserADObjectGuid",
									"type": "string"
								},
								{
									"name": "UserAgent",
									"type": "string"
								},
								{
									"name": "TimeGenerated",
									"type": "datetime"
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
		Invoke-AzRestMethod -Path "/subscriptions/$SubscriptionID/resourcegroups/$ResourceGroupName/providers/microsoft.operationalinsights/workspaces/$WorkspaceName/tables/ExchangeHttpProxy_CL?api-version=2021-12-01-preview" -Method PUT -payload $tableParams
**A. Create DCE (If not already created for Exchange Servers)**

      1.  From the Azure Portal, navigate to [Azure Data collection Endpoint](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/dataCollectionEndpoints).
2. Click **+ Create** at the top.
3. In the **Basics** tab, fill the required fields and give a name to the DCE. 
3. 'Make other preferable configuration changes', if needed, then click **Create**.

      **B. Create a DCR, Type Custom log**

      1.  From the Azure Portal, navigate to [Azure Data collection rules](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/dataCollectionRules).
2. Click on 'Create' button.
3. On 'Basics' tab, fill the Rule name like **DCR-Option7-HTTPProxyLogs**, select the 'Data Collection Endpoint' with the previously created endpoint and fill other parameters.
4. In the **Resources** tab, add your Exchange Servers.
5. In **Collect and Deliver**, add a Data Source type 'Custom Text logs' and enter the following file pattern : 
		'C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Autodiscover\*.log','C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Eas\*.log','C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Ecp\*.log','C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Ews\*.log','C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Mapi\*.log','C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Oab\*.log','C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Owa\*.log','C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\OwaCalendar\*.log','C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\PowerShell\*.log','C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\RpcHttp\*.log'
6. Put 'ExchangeHttpProxy_CL' in Table Name.
7. in Transform field, enter the following KQL request :
		source | extend d = split(RawData,',') | extend DateTime=todatetime(d[0]),RequestId=tostring(d[1]) ,MajorVersion=tostring(d[2]) ,MinorVersion=tostring(d[3]) ,BuildVersion=tostring(d[4]) ,RevisionVersion=tostring(d[5]) ,ClientRequestId=tostring(d[6]) ,Protocol=tostring(d[7]) ,UrlHost=tostring(d[8]) ,UrlStem=tostring(d[9]) ,ProtocolAction=tostring(d[10]) ,AuthenticationType=tostring(d[11]) ,IsAuthenticated=tostring(d[12]) ,AuthenticatedUser=tostring(d[13]) ,Organization=tostring(d[14]) ,AnchorMailbox=tostring(d[15]) ,UserAgent=tostring(d[16]) ,ClientIpAddress=tostring(d[17]) ,ServerHostName=tostring(d[18]) ,HttpStatus=tostring(d[19]) ,BackEndStatus=tostring(d[20]) ,ErrorCode=tostring(d[21]) ,Method=tostring(d[22]) ,ProxyAction=tostring(d[23]) ,TargetServer=tostring(d[24]) ,TargetServerVersion=tostring(d[25]) ,RoutingType=tostring(d[26]) ,RoutingHint=tostring(d[27]) ,BackEndCookie=tostring(d[28]) ,ServerLocatorHost=tostring(d[29]) ,ServerLocatorLatency=tostring(d[30]) ,RequestBytes=tostring(d[31]) ,ResponseBytes=tostring(d[32]) ,TargetOutstandingRequests=tostring(d[33]) ,AuthModulePerfContext=tostring(d[34]) ,HttpPipelineLatency=tostring(d[35]) ,CalculateTargetBackEndLatency=tostring(d[36]) ,GlsLatencyBreakup=tostring(d[37]) ,TotalGlsLatency=tostring(d[38]) ,AccountForestLatencyBreakup=tostring(d[39]) ,TotalAccountForestLatency=tostring(d[40]) ,ResourceForestLatencyBreakup=tostring(d[41]) ,TotalResourceForestLatency=tostring(d[42]) ,ADLatency=tostring(d[43]) ,SharedCacheLatencyBreakup=tostring(d[44]) ,TotalSharedCacheLatency=tostring(d[45]) ,ActivityContextLifeTime=tostring(d[46]) ,ModuleToHandlerSwitchingLatency=tostring(d[47]) ,ClientReqStreamLatency=tostring(d[48]) ,BackendReqInitLatency=tostring(d[49]) ,BackendReqStreamLatency=tostring(d[50]) ,BackendProcessingLatency=tostring(d[51]) ,BackendRespInitLatency=tostring(d[52]) ,BackendRespStreamLatency=tostring(d[53]) ,ClientRespStreamLatency=tostring(d[54]) ,KerberosAuthHeaderLatency=tostring(d[55]) ,HandlerCompletionLatency=tostring(d[56]) ,RequestHandlerLatency=tostring(d[57]) ,HandlerToModuleSwitchingLatency=tostring(d[58]) ,ProxyTime=tostring(d[59]) ,CoreLatency=tostring(d[60]) ,RoutingLatency=tostring(d[61]) ,HttpProxyOverhead=tostring(d[62]) ,TotalRequestTime=tostring(d[63]) ,RouteRefresherLatency=tostring(d[64]) ,UrlQuery=tostring(d[65]) ,BackEndGenericInfo=tostring(d[66]) ,GenericInfo=tostring(d[67]) ,GenericErrors=tostring(d[68]) ,EdgeTraceId=tostring(d[69]) ,DatabaseGuid=tostring(d[70]) ,UserADObjectGuid=tostring(d[71]) ,PartitionEndpointLookupLatency=tostring(d[72]) ,RoutingStatus=tostring(d[73]) | extend TimeGenerated = DateTime  | project-away d,RawData,DateTime | project-away d,RawData,DateTime
 and click on 'Destination'.
8. In 'Destination', add a destination and select the Workspace where you have previously created the Custom Table 
9. Click on 'Add data source'.
10. Fill other required parameters and tags and create the DCR

    **Assign the DCR to all Exchange Servers**

    Add all your Exchange Servers to the DCR

| | |
|--------------------------|---|
| **Tables Ingested** | `ExchangeHttpProxy_CL` |
| **Connector Definition Files** | [ESI-Opt7ExchangeHTTPProxyLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-Opt7ExchangeHTTPProxyLogs.json) |

[→ View full connector details](../connectors/esi-opt7exchangehttpproxylogs.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ESIExchangeConfig_CL` | [Exchange Security Insights On-Premises Collector](../connectors/esi-exchangeonpremisescollector.md) |
| `Event` | [Microsoft Exchange Admin Audit Logs by Event Logs](../connectors/esi-opt1exchangeadminauditlogsbyeventlogs.md), [Microsoft Exchange Logs and Events](../connectors/esi-opt2exchangeserverseventlogs.md), [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md) |
| `ExchangeHttpProxy_CL` | [Microsoft Exchange HTTP Proxy Logs](../connectors/esi-opt7exchangehttpproxylogs.md), [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md) |
| `MessageTrackingLog_CL` | [Microsoft Exchange Message Tracking Logs](../connectors/esi-opt6exchangemessagetrackinglogs.md), [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md) |
| `SecurityEvent` | [ Microsoft Active-Directory Domain Controllers Security Event Logs](../connectors/esi-opt34domaincontrollerssecurityeventlogs.md), [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md) |
| `W3CIISLog` | [IIS Logs of Microsoft Exchange Servers](../connectors/esi-opt5exchangeiislogs.md), [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md) |

[← Back to Solutions Index](../solutions-index.md)
