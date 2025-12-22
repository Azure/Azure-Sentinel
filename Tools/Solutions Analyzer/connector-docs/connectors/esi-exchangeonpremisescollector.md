# Exchange Security Insights On-Premises Collector

| | |
|----------|-------|
| **Connector ID** | `ESI-ExchangeOnPremisesCollector` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ESIExchangeConfig_CL`](../tables-index.md#esiexchangeconfig_cl) |
| **Used in Solutions** | [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md) |
| **Connector Definition Files** | [ESI-ExchangeOnPremisesCollector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Data%20Connectors/ESI-ExchangeOnPremisesCollector.json) |

Connector used to push Exchange On-Premises Security configuration for Microsoft Sentinel Analysis

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Service Account with Organization Management role**: The service Account that launch the script as scheduled task needs to be Organization Management to be able to retrieve all the needed security Information.
- **Detailled documentation**: >**NOTE:** Detailled documentation on Installation procedure and usage can be found [here](https://aka.ms/MicrosoftExchangeSecurityGithub)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Install the ESI Collector Script on a server with Exchange Admin PowerShell console**

This is the script that will collect Exchange Information to push content in Microsoft Sentinel.
**Script Deployment**

**Download the latest version of ESI Collector**

  The latest version can be found here : https://aka.ms/ESI-ExchangeCollector-Script. The file to download is CollectExchSecIns.zip

  **Copy the script folder**

  Unzip the content and copy the script folder on a server where Exchange PowerShell Cmdlets are present.

  **Unblock the PS1 Scripts**

  Click right on each PS1 Script and go to Properties tab.
 If the script is marked as blocked, unblock it. You can also use the Cmdlet 'Unblock-File *.* in the unzipped folder using PowerShell.

  **Configure Network Access**

  Ensure that the script can contact Azure Analytics (*.ods.opinsights.azure.com).

**2. Configure the ESI Collector Script**

Be sure to be local administrator of the server.
In 'Run as Administrator' mode, launch the 'setup.ps1' script to configure the collector.
 Fill the Log Analytics (Microsoft Sentinel) Workspace information.
 Fill the Environment name or leave empty. By default, choose 'Def' as Default analysis. The other choices are for specific usage.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Schedule the ESI Collector Script (If not done by the Install Script due to lack of permission or ignored during installation)**

The script needs to be scheduled to send Exchange configuration to Microsoft Sentinel.
 We recommend to schedule the script once a day.
 The account used to launch the Script needs to be member of the group Organization Management

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
