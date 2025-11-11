# ExchSecIns Configuration

Actual Parameter version : 2.5

## Table of Contents

- [ExchSecIns Configuration](#exchsecins-configuration)
  - [Table of Contents](#table-of-contents)
  - [Parameters](#parameters)
    - [Global](#global)
    - [Output](#output)
    - [Advanced](#advanced)
    - [LogCollection](#logcollection)
    - [MGGraphAPIConnection](#mggraphapiconnection)
    - [InstanceConfiguration](#instanceconfiguration)
    - [AuditFunctionsFiles](#auditfunctionsfiles)
    - [AuditFunctionProtectedArea](#auditfunctionprotectedarea)
  - [Description](#description)
    - [UDSLogProcessor](#udslogprocessor)
    - [InstanceConfiguration](#instanceconfiguration-1)
    - [AuditFunctionsFiles](#auditfunctionsfiles-1)
    - [other parameters](#other-parameters)

## Parameters

Parameters can be found in the "CollectExchSecConfiguration.json" file for On-Premises deployment or the "GlobalConfiguration" variable for Runbook deployment.

### Global

| Parameter | Type | Description | Default | Required |
| --- | --- | --- | --- | --- |
| ParallelTimeoutMinutes | Int | Maximum time in minutes to wait for a parallel job to finish | 5 | False |
| MaxParallelRunningJobs | Int | Maximum number of parallel jobs running at the same time | 8 | False |
| GlobalParallelProcessing | Boolean | Activate the collection of information by using paralleling mechanism. Recommanded | true | False |
| PerServerParallelProcessing | Boolean | Activate the collection of information concerning a specific server by using paralleling mechanism. Recommanded | true | False |
| DefaultDurationTracking | Int | Default duration tracking in days | 30 | False |
| ESIProcessingType | String | Type of processing, online or offline | Online | False |
| EnvironmentIdentification | String | Identification of the environment. Could be any text, the name of the tenant or AD domain | MyOwnEnvironment | False |

### Output

| Parameter | Type | Description | Default | Required |
| --- | --- | --- | --- | --- |
| DefaultOutputFile | String | Default output file where data will be written if log collection by API is not activated. | C:\ExchSecIns\data\ExchSecIns.csv | False |
| ExportDomainsInformation | Boolean | Export AD Domain Information in Sentinel Table | True | False |

### Advanced

| Parameter | Type | Description | Default | Required |
| --- | --- | --- | --- | --- |
| ParralelWaitRunning | Int | Time in seconds to wait for parallel processing before considering a timeout | 10 | False |
| ParralelPingWaitRunning | Int | Time in seconds to wait for parallel ping processing before considering a timeout | 10 | False |
| OnlyExplicitActivation | Boolean | Only the explicit activation of the functions are processed. In this mode, each function needs to be taggued for processig | false | False |
| ExchangeServerBinPath | String | Path of the Exchange Server Binaries. Could be changed if Exchange is not installed in the default folder path | c:\Program Files\Microsoft\Exchange Server\V15\bin | False |
| BypassServerAvailabilityTest | Boolean | Bypass the server availability test. If this feature is activated, the collector will try to work with all servers including inaccessible servers. | false | False |
| ExplicitExchangeServerList | Array | List of explicit Exchange servers. If the previous parameter is activated, it could be good to build a static list of server to use | [] | False |
| FunctionsListInline | Boolean | Functions list inline. The functions will be read in the main config file. This option is more for retrocompatibility | false | False |
| FunctionsListWithoutInternet | Boolean | Functions list without internet. If this option is activated, the collector will use the local files instead of files in the Github repository | false | False |
| Beta | Boolean | Activating Beta feature, collecting Beta version of functions to execute. | false | False |
| Useproxy | Boolean | Use Proxy boolean if you need it. The next option need to be filled. | false | False |
| ProxyUrl | String | Proxy URL | http://proxy.dom.net:8080 | False |
| MaximalSentinelPacketSizeMb | Int | Max Packet size for Sentinel in Mb | 32 | False |
| PaginationErrorThreshold | Int | Pagination Error Threshold when an executed function use a pagination | 5 | False |
| UpdateVersionCheckingDeactivated | Boolean | Deactivate the version checking | false | False |
| DeactivateUDSLogs | Boolean | Deactivate the log summary (Called USD Logs) at the end of the script. | false | False |
| LogVerboseActivated | Boolean | Log Verbose Activated | true | False |
| UDSLogProcessor | Array | UDS Log Processor definition. By Default USD logs are displayed at the end. It could stored in a file or an Azure Storage account if needed. See Below description. | [{Activated:true, StorageType:Output}] | False |

### LogCollection

| Parameter | Type | Description | Default | Required |
| --- | --- | --- | --- | --- |
| ActivateLogUpdloadToSentinel | Boolean | Activate the log upload to Sentinel. If not activated, results are stored in a file. | true | False |
| WorkspaceId | String | Workspace Id | e15121b8-fc25-4ec2-8d21-44532bfd219a | False |
| WorkspaceKey | String | Workspace Key | WKey | False |
| LogTypeName | String | Name of the Table to store data. ESIExchangeConfig is the default table used by Sentinel Solution | ESIExchangeConfig | False |
| TogetherMode | Boolean | Together Mode can be activated to store results in a file in addition to sentinel upload | false | False |

### MGGraphAPIConnection

| Parameter | Type | Description | Default | Required |
| --- | --- | --- | --- | --- |
| MGGraphAzureRMCertificate | String | MGGraph Azure RM Certificate | | False |
| MGGraphAzureRMAppId | String | MGGraph Azure RM App Id | | False |

### InstanceConfiguration

| Parameter | Type | Description | Default | Required |
| --- | --- | --- | --- | --- |
| Default | Object | Default configuration, see details below. | {All:true, Capabilities:OP\|OL\|MGGRAPH\|ADINFOS} | False |
| IIS-IoCs | Object | IIS IoCs configuration, see details below. | {All:true, Category:IIS-IoCs, Capabilities:IIS, OutputName:ESIIISIoCs} | False |
| ExchangeOnlineMessageTracking | Object | Exchange Online Message Tracking configuration, see details below. | {All:true, Category:OnlineMessageTracking, Capabilities:OL, OutputName:ExchangeOnlineMessageTracking} | False |
| InstanceExample | Object | Instance Example configuration, see details below. | {SelectedAddons:[Filename1, Filename2], FileteredAddons:[Filename1, Filename2]} | False |

### AuditFunctionsFiles

| Parameter | Type | Description | Default | Required |
| --- | --- | --- | --- | --- |
| Filename | String | Filename | FiletoIgnore | False |
| Deactivated | Boolean | Deactivated | false | False |

### AuditFunctionProtectedArea

| Parameter | Type | Description | Default | Required |
| --- | --- | --- | --- | --- |
| ContentCheckSum | String | Content CheckSum | | False |

## Description

This configuration file is used to configure the CollectExchSecIns script. It contains all the parameters needed to run the script.
Below are specific parameters and their description.

### UDSLogProcessor

The USDLogProcessor allows to describe the way the USD logs are displayed or stored. It could be stored in a file or an Azure Storage account if needed or only displayed.
The UDSLogProcessor is an array of object. Each object contains the following parameters:

- Activated: Boolean. If true, the log will be processed.
- StorageType: String. The type of storage. Could be Output, File or AzureStorageAccount.
- StoragePath: String. The path of the storage. If the StorageType is File, this parameter is required.
- Prefix: String. The prefix of the file or the Blob. It's optional.
- LogStorageRetentionDays: Int. The retention days of the log in the storage. It's optional.
- StorageAccountName: String. The name of the storage account. If the StorageType is AzureStorageAccount, this parameter is required.
- StorageBlobContainer: String. The name of the storage container. If the StorageType is AzureStorageAccount, this parameter is required.
- ConnexionType: String. The type of the connexion. Could be ManagedIdentity or Certificate. If the StorageType is AzureStorageAccount, this parameter is required.
- TenantId: String. The tenant id. If the StorageType is AzureStorageAccount, this parameter is required.
- ApplicationID: String. The application id. If the StorageType is AzureStorageAccount and ConnexionType is Certificate, this parameter is required.
- CertificateThumbprint: String. The certificate thumbprint. If the StorageType is AzureStorageAccount and ConnexionType is Certificate, this parameter is required.

### InstanceConfiguration

The InstanceConfiguration allows to configure multiple instances to collect different data. 3 main instances are available: Default, IIS-IoCs and ExchangeOnlineMessageTracking. It's possible to configure more instances by using the InstanceExample example where InstanceExample is the name of the instance to configure. 
The InstanceConfiguration is an object. It contains the following parameters:

- Default: Object. Default configuration, mandatory. It contains the following parameters:
  - All: Boolean. If true (by default), all the functions are activated.
  - Capabilities: String. The capabilities to activate. Could be 'OP' for Exchange On-Premises, 'OL' for Exchange Online, 'MGGRAPH' for connexion to Microsoft Graph API and 'ADINFOS' to collect AD Information. The capabilities are used only if the functions require them.
  - SelectedAddons: Array, Mandatory if All is deactivated. The list of selected addons to activate by inserting the filename of the addon like "ESICollector-POPIMAPConfiguration.json".
  - FileteredAddons: Array, Optional. The list of filtered addons to deactivate by inserting the filename of the addon like "ESICollector-POPIMAPConfiguration.json".
  - OutputName: String, Optional. The name of the output file to use. The Default name in the configuration is used if not present.

- IIS-IoCs: Object. IIS IoCs configuration, a specific configuration to collect information from IIS Logs. It contains the following parameters:
  - All: Boolean. If true, all the functions are activated.
  - Category: String. The category of the functions to activate, by default 'IIS-IoCs'.
  - Capabilities: String. The capabilities to activate. For IIS, a specific capability is used : 'IIS'.

- ExchangeOnlineMessageTracking: Object. Exchange Online Message Tracking configuration to extract Message Tracking from Online platform and store it to Sentinel. It contains the following parameters:
  - All: Boolean. If true, all the functions are activated.
  - Category: String. The category of the functions to activate, by default 'OnlineMessageTracking'.
  - Capabilities: String. The capabilities to activate. For ExchangeOnlineMessageTracking, the 'OL' capability is needed.
  - OutputName: String. The name of the Log Analytic Table to store Message Tracking.

- InstanceExample: Object. Instance Example configuration where InstanceExample is the name of the Instance you want to create. It contains the following parameters:
  - All: Boolean. If true, all the functions are activated.
  - SelectedAddons: Array, mandatory only if All is false. The list of selected addons to activate by inserting the filename of the addon like "ESICollector-POPIMAPConfiguration.json".
  - FileteredAddons: Array. The list of filtered addons to deactivate by inserting the filename of the addon like "ESICollector-POPIMAPConfiguration.json".
  - Capabilities: String. The capabilities to activate. It could be 'OP' for Exchange On-Premises, 'OL' for Exchange Online, 'MGGRAPH' for connexion to Microsoft Graph API and 'ADINFOS' to collect AD Information, 'IIS' for IIS logs.
  - OutputName: String. The name of the output file or Log Analytic table.
  - Category: String, optional. The category of the functions to activate. This parameter is linked to "Add-Ons" folders. If the category is not present, the selected functions are selected from the root Add-ons folder. If the category is present, the selected functions are selected from the category folder. 2 categories are available by default: "IIS" and "OnlineMessageTracking".

### AuditFunctionsFiles

The AuditFunctionsFiles is an array of object. It's used to ignore a specific set of functions grouped in a file like "ESICollector-POPIMAPConfiguration.json". Each object contains the following parameters:

- Filename: String. The filename to ignore like "ESICollector-POPIMAPConfiguration.json".
- Deactivated: Boolean. If true, the function file is deactivated.

### other parameters

The parameter AuditFunctionProtectedArea is not used for the moment. They are reserved for future use.
The parameter AuditFunctions is not used anymore, only present for backward comptability.
