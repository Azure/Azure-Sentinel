# [Deprecated] Microsoft Exchange Logs and Events

| | |
|----------|-------|
| **Connector ID** | `ESI-ExchangeAdminAuditLogEvents` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`Event`](../tables-index.md#event), [`ExchangeHttpProxy_CL`](../tables-index.md#exchangehttpproxy_cl), [`MessageTrackingLog_CL`](../tables-index.md#messagetrackinglog_cl), [`SecurityEvent`](../tables-index.md#securityevent), [`W3CIISLog`](../tables-index.md#w3ciislog) |
| **Used in Solutions** | [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md) |
| **Connector Definition Files** | [ESI-ExchangeAdminAuditLogEvents.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-ExchangeAdminAuditLogEvents.json) |

Deprecated, use the 'ESI-Opt' dataconnectors. You can stream all Exchange Audit events, IIS Logs, HTTP Proxy logs and Security Event logs from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This is used by Microsoft Exchange Security Workbooks to provide security insights of your On-Premises Exchange environment

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Detailled documentation**: >**NOTE:** Detailled documentation on Installation procedure and usage can be found [here](https://aka.ms/MicrosoftExchangeSecurityGithub)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This solution is based on options. This allows you to choose which data will be ingest as some options can generate a very high volume of data. Depending on what you want to collect, track in your Workbooks, Analytics Rules, Hunting capabilities you will choose the option(s) you will deploy. Each options are independant for one from the other. To learn more about each option: ['Microsoft Exchange Security' wiki](https://aka.ms/ESI_DataConnectorOptions)

**1.  Download and install the agents needed to collect logs for Microsoft Sentinel**

Type of servers (Exchange Servers, Domain Controllers linked to Exchange Servers or all Domain Controllers) depends on the option you want to deploy.
**Deploy Monitor Agents**

  This step is required only if it's the first time you onboard your Exchange Servers/Domain Controllers
  **Select which agent you want to install in your servers to collect logs:**

**[Prefered] Azure Monitor Agent via Azure Arc**

    **Deploy the Azure Arc Agent**
> [Learn more](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install?tabs=ARMAgentPowerShell,PowerShellWindows,PowerShellWindowsArc,CLIWindows,CLIWindowsArc)

    **Install Azure Log Analytics Agent (Deprecated on 31/08/2024)**

    1. Download the Azure Log Analytics Agent and choose the deployment method in the below link.
    - **Install/configure: InstallAgentOnNonAzure**

**2.  Deploy log injestion following choosed options**
**[Option 1] MS Exchange Management Log collection**

  Select how to stream MS Exchange Admin Audit event logs
  **MS Exchange Admin Audit event logs**

**Data Collection Rules - When Azure Monitor Agent is used**

    **Enable data collection rule**
>  Microsoft Exchange Admin Audit Events logs are collected only from **Windows** agents.
**Option 1 - Azure Resource Manager (ARM) Template**

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

    **Data Collection Rules - When the legacy Azure Log Analytics Agent is used**

    **Configure the logs to be collected**

Configure the Events you want to collect and their severities.

1.  Under workspace **Legacy agents management**, select **Windows Event logs**.
2.  Click **Add Windows event log** and enter **MSExchange Management** as log name.
3.  Collect Error, Warning and Information types
4.  Click **Save**.
    - **Open Syslog settings**
**[Option 2] Security/Application/System logs of Exchange Servers**

  Select how to stream Security/Application/System logs of Exchange Servers
  **Security Event log collection**

**Data Collection Rules - Security Event logs**

    **Enable data collection rule for Security Logs**
Security Events logs are collected only from **Windows** agents.
1. Add Exchange Servers on *Resources* tab.
2. Select Security log level

>  **Common level** is the minimum required. Please select 'Common' or 'All Security Events' on DCR definition.
    - **Create data collection rule**
  **Application and System Event log collection**

**Data Collection Rules - When Azure Monitor Agent is used**

    **Enable data collection rule**
>  Application and System Events logs are collected only from **Windows** agents.
**Option 1 - Azure Resource Manager (ARM) Template**

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

    **Data Collection Rules - When the legacy Azure Log Analytics Agent is used**

    **Configure the logs to be collected**

Configure the Events you want to collect and their severities.

1.  Under workspace advanced settings **Configuration**, select **Data** and then **Windows Event logs**.
2.  Click **Add Windows event log** and search **Application** as log name.
3.  Click **Add Windows event log** and search **System** as log name.
4.  Collect Error (for all), Warning (for all) and Information (for System) types
5.  Click **Save**.
    - **Open Syslog settings**
**[Option 3 and 4] Security logs of Domain Controllers**

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
**[Option 5] IIS logs of Exchange Servers**

  Select how to stream IIS logs of Exchange Servers
**Data Collection Rules - When Azure Monitor Agent is used**

    **Enable data collection rule**
> IIS logs are collected only from **Windows** agents.
    > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `AdminAuditEvents`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.
**Option 1 - Azure Resource Manager (ARM) Template**

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

    **Data Collection Rules - When the legacy Azure Log Analytics Agent is used**

    **Configure the logs to be collected**

Configure the Events you want to collect and their severities.

1.  Under workspace advanced settings **Configuration**, select **Data** and then **IIS Logs**.
2. Check **Collect W3C format IIS log files**
5.  Click **Save**.
    - **Open Syslog settings**
**[Option 6] Message Tracking of Exchange Servers**

  Select how to stream Message Tracking of Exchange Servers
**Data Collection Rules - When Azure Monitor Agent is used**

    **Enable data collection rule**
> Message Tracking are collected only from **Windows** agents.

    ℹ️ **Attention**, Custom logs in Monitor Agent is in Preview. The deployment doesn't work as expected for the moment (March 2023).
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
**A. Create DCE (If not already created for Exchange Servers)**

        1.  From the Azure Portal, navigate to [Azure Data collection Endpoint](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/dataCollectionEndpoints).
2. Click **+ Create** at the top.
3. In the **Basics** tab, fill the required fields and give a name to the DCE, like ESI-ExchangeServers. 
3. 'Make other preferable configuration changes', if needed, then click **Create**.

        **B. Create Custom DCR Table**

        1. Download the Example file from [Microsoft Sentinel GitHub](https://aka.ms/Sentinel-Sample-ESI-MessageTrackingExampleFile).
2.  From the Azure Portal, navigate to [Workspace Analytics](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces) and select your target Workspace.
3. Click in 'Tables', click **+ Create** at the top and select **New Custom log (DCR-Based)**.
4. In the **Basics** tab, enter **MessageTrackingLog** on the Table name, create a Data Collection rule with the name **DCR-Option6-MessageTrackingLogs** (for example) and select the previously created Data collection Endpoint.
5. In the **Schema and Transformation** tab, choose the downloaded sample file and click on **Transformation Editor**.
6. In the transformation field, enter the following KQL request :
*source
| extend TimeGenerated = todatetime(['date-time'])
| extend
    clientHostname = ['client-hostname'],
    clientIP = ['client-ip'],
    connectorId = ['connector-id'],
    customData = ['custom-data'],
    eventId = ['event-id'],
    internalMessageId = ['internal-message-id'],
    logId = ['log-id'],
    messageId = ['message-id'],
    messageInfo = ['message-info'],
    messageSubject = ['message-subject'],
    networkMessageId = ['network-message-id'],
    originalClientIp =  ['original-client-ip'],
    originalServerIp = ['original-server-ip'],
    recipientAddress= ['recipient-address'],
    recipientCount= ['recipient-count'],
    recipientStatus= ['recipient-status'],
    relatedRecipientAddress= ['related-recipient-address'],
    returnPath= ['return-path'],
    senderAddress= ['sender-address'],
    senderHostname= ['server-hostname'],
    serverIp= ['server-ip'],
    sourceContext= ['source-context'],
    schemaVersion=['schema-version'],
    messageTrackingTenantId = ['tenant-id'],
    totalBytes = ['total-bytes'],
    transportTrafficType = ['transport-traffic-type']
| project-away
    ['client-ip'],
    ['client-hostname'],
    ['connector-id'],
    ['custom-data'],
    ['date-time'],
    ['event-id'],
    ['internal-message-id'],
    ['log-id'],
    ['message-id'],
    ['message-info'],
    ['message-subject'],
    ['network-message-id'],
    ['original-client-ip'],
    ['original-server-ip'],
    ['recipient-address'],
    ['recipient-count'],
    ['recipient-status'],
    ['related-recipient-address'],
    ['return-path'],
    ['sender-address'],
    ['server-hostname'],
    ['server-ip'],
    ['source-context'],
    ['schema-version'],
    ['tenant-id'],
    ['total-bytes'],
    ['transport-traffic-type']*

8. Click 'Run' and after 'Apply'.
9. Click **Next**, then click **Create**.

        **C. Modify the created DCR, Type Custom log**

        1.  From the Azure Portal, navigate to [Azure Data collection rules](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/dataCollectionRules).
2. Select the previously created DCR, like **DCR-Option6-MessageTrackingLogs**.
3. In the **Resources** tab, enter you Exchange Servers.
4. In **Data Sources**, add a Data Source type 'Custom Text logs' and enter 'C:\Program Files\Microsoft\Exchange Server\V15\TransportRoles\Logs\MessageTracking\*.log' in file pattern, 'MessageTrackingLog_CL' in Table Name.
6.in Transform field, enter the following KQL request :
*source
| extend TimeGenerated = todatetime(['date-time'])
| extend
    clientHostname = ['client-hostname'],
    clientIP = ['client-ip'],
    connectorId = ['connector-id'],
    customData = ['custom-data'],
    eventId = ['event-id'],
    internalMessageId = ['internal-message-id'],
    logId = ['log-id'],
    messageId = ['message-id'],
    messageInfo = ['message-info'],
    messageSubject = ['message-subject'],
    networkMessageId = ['network-message-id'],
    originalClientIp =  ['original-client-ip'],
    originalServerIp = ['original-server-ip'],
    recipientAddress= ['recipient-address'],
    recipientCount= ['recipient-count'],
    recipientStatus= ['recipient-status'],
    relatedRecipientAddress= ['related-recipient-address'],
    returnPath= ['return-path'],
    senderAddress= ['sender-address'],
    senderHostname= ['server-hostname'],
    serverIp= ['server-ip'],
    sourceContext= ['source-context'],
    schemaVersion=['schema-version'],
    messageTrackingTenantId = ['tenant-id'],
    totalBytes = ['total-bytes'],
    transportTrafficType = ['transport-traffic-type']
| project-away
    ['client-ip'],
    ['client-hostname'],
    ['connector-id'],
    ['custom-data'],
    ['date-time'],
    ['event-id'],
    ['internal-message-id'],
    ['log-id'],
    ['message-id'],
    ['message-info'],
    ['message-subject'],
    ['network-message-id'],
    ['original-client-ip'],
    ['original-server-ip'],
    ['recipient-address'],
    ['recipient-count'],
    ['recipient-status'],
    ['related-recipient-address'],
    ['return-path'],
    ['sender-address'],
    ['server-hostname'],
    ['server-ip'],
    ['source-context'],
    ['schema-version'],
    ['tenant-id'],
    ['total-bytes'],
    ['transport-traffic-type']* 
7. Click on 'Add data source'.

      **Assign the DCR to all Exchange Servers**

      Add all your Exchange Servers to the DCR

    **Data Collection Rules - When the legacy Azure Log Analytics Agent is used**

    **Configure the logs to be collected**

1.  Under workspace **Settings** part, select **Tables**, click **+ Create** and click on **New custom log (MMA-Based)**.
2.  Select Sample file **[MessageTracking Sample](https://aka.ms/Sentinel-Sample-ESI-MessageTrackingLogsSampleCSV)** and click Next
3. Select type **Windows** and enter the path **C:\Program Files\Microsoft\Exchange Server\V15\TransportRoles\Logs\MessageTracking\*.log**. Click Next.
4. Enter **MessageTrackingLog** as Table name and click Next.
5.  Click **Save**.
    - **Open Syslog settings**
**[Option 7] HTTP Proxy of Exchange Servers**

  Select how to stream HTTP Proxy of Exchange Servers
**Data Collection Rules - When Azure Monitor Agent is used**

    **Enable data collection rule**
> Message Tracking are collected only from **Windows** agents.

    ℹ️ **Attention**, Custom logs in Monitor Agent is in Preview. The deployment doesn't work as expected for the moment (March 2023).
**Option 1 - Azure Resource Manager (ARM) Template**

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
**A. Create DCE (If not already created for Exchange Servers)**

        1.  From the Azure Portal, navigate to [Azure Data collection Endpoint](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/dataCollectionEndpoints).
2. Click **+ Create** at the top.
3. In the **Basics** tab, fill the required fields and give a name to the DCE. 
3. 'Make other preferable configuration changes', if needed, then click **Create**.

        **B. Create Custom DCR Table**

        1. Download the Example file from [Microsoft Sentinel GitHub](https://aka.ms/Sentinel-Sample-ESI-HTTPProxyExampleFile).
2.  From the Azure Portal, navigate to [Workspace Analytics](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.OperationalInsights%2Fworkspaces) and select your target Workspace.
3. Click in 'Tables', click **+ Create** at the top and select **New Custom log (DCR-Based)**.
4. In the **Basics** tab, enter **ExchangeHttpProxy** on the Table name, create a Data Collection rule with the name **DCR-Option7-HTTPProxyLogs** (for example) and select the previously created Data collection Endpoint.
5. In the **Schema and Transformation** tab, choose the downloaded sample file and click on **Transformation Editor**.
6. In the transformation field, enter the following KQL request :
*source
| extend TimeGenerated = todatetime(DateTime)
| project-away DateTime
*

8. Click 'Run' and after 'Apply'.
9. Click **Next**, then click **Create**.

        **C. Modify the created DCR, Type Custom log**

        1.  From the Azure Portal, navigate to [Azure Data collection rules](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/~/dataCollectionRules).
2. Select the previously created DCR, like **DCR-Option7-HTTPProxyLogs**.
3. In the **Resources** tab, enter you Exchange Servers.
4. In **Data Sources**, add a Data Source type 'Custom Text logs' and enter 'C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Autodiscover\*.log' in file pattern, 'ExchangeHttpProxy_CL' in Table Name.
6.in Transform field, enter the following KQL request :
*source
| extend TimeGenerated = todatetime(DateTime)
| project-away DateTime* 
7. Click on 'Add data source'.

      **Assign the DCR to all Exchange Servers**

      Add all your Exchange Servers to the DCR

    **Data Collection Rules - When the legacy Azure Log Analytics Agent is used**

    **Configure the logs to be collected**

1.  Under workspace **Settings** part, select **Tables**, click **+ Create** and click on **New custom log (MMA-Based)**.
2.  Select Sample file **[MessageTracking Sample](https://aka.ms/Sentinel-Sample-ESI-HttpProxySampleCSV)** and click Next
3. Select type **Windows** and enter all the following paths **C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Autodiscover\*.log**, **C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Eas\*.log**, **C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Ecp\*.log**, **C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Ews\*.log**, **C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Mapi\*.log**, **C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Oab\*.log**, **C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\Owa\*.log**, **C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\OwaCalendar\*.log**, **C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\PowerShell\*.log** and **C:\Program Files\Microsoft\Exchange Server\V15\Logging\HttpProxy\RpcHttp\*.log** . Click Next.
4. Enter **ExchangeHttpProxy** as Table name and click Next.
5.  Click **Save**.
    - **Open Syslog settings**

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
