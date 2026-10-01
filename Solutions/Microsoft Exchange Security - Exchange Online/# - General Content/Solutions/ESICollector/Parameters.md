# ExchSecIns Configuration

Current parameter schema version: **3.0**

## Table of Contents

- [ExchSecIns Configuration](#exchsecins-configuration)
  - [Table of Contents](#table-of-contents)
  - [Parameters](#parameters)
    - [Global](#global)
    - [Advanced](#advanced)
    - [LogCollection](#logcollection)
    - [InternetAddonCollectionConfiguration](#internetaddoncollectionconfiguration)
    - [MGGraphAPIConnection](#mggraphapiconnection)
    - [InstanceConfiguration](#instanceconfiguration)
    - [AuditFunctionsFiles](#auditfunctionsfiles)
    - [AuditFunctionProtectedArea](#auditfunctionprotectedarea)
  - [Description](#description)
    - [UDSLogProcessor](#udslogprocessor)
    - [Azure Monitor Log Ingestion API parameters](#azure-monitor-log-ingestion-api-parameters)
    - [InternetAddonCollectionConfiguration](#internetaddoncollectionconfiguration-1)
    - [InstanceConfiguration](#instanceconfiguration-1)
    - [AuditFunctionsFiles](#auditfunctionsfiles-1)
    - [Other parameters](#other-parameters)
  - [Migration from configuration version 2.5 to 3.0](#migration-from-configuration-version-25-to-30)

## Parameters

Parameters can be found in the "CollectExchSecConfiguration.json" file for On-Premises deployment or the "GlobalConfiguration" variable for Runbook deployment.

### Global

| Parameter                   | Type    | Description                                                                                | Default          | Required |
|-----------------------------|---------|--------------------------------------------------------------------------------------------|------------------|----------|
| ParallelTimeoutMinutes      | Int     | Maximum time in minutes to wait for a parallel job to finish                               | 5                | False    |
| MaxParallelRunningJobs      | Int     | Maximum number of parallel jobs running at the same time                                   | 8                | False    |
| GlobalParallelProcessing    | Boolean | Collect information by using parallel processing. Recommended.                             | true             | False    |
| PerServerParallelProcessing | Boolean | Collect information for individual servers by using parallel processing.                   | true             | False    |
| DefaultDurationTracking     | Int     | Default duration tracking in days                                                          | 30               | False    |
| ESIProcessingType           | String  | Type of processing, online or offline                                                      | Online           | False    |
| EnvironmentIdentification   | String  | Identification of the environment. Could be any text, the name of the tenant or AD domain  | MyOwnEnvironment | False    |

> [!NOTE]
> The `Output` section has been removed in configuration version 3.0. `ExportDomainsInformation` and the output file setting are now part of the [LogCollection](#logcollection) section.

### Advanced

| Parameter                        | Type    | Description                                                                                                                                                 | Default                                                | Required |
|----------------------------------|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|----------|
| ParralelWaitRunning              | Int     | Time in seconds to wait for parallel processing before considering a timeout                                                                                | 10                                                     | False    |
| ParralelPingWaitRunning          | Int     | Time in seconds to wait for parallel ping processing before considering a timeout                                                                           | 10                                                     | False    |
| OnlyExplicitActivation           | Boolean | Process only explicitly activated functions. In this mode, each function must be tagged for processing.                                                    | false                                                  | False    |
| ExchangeServerBinPath            | String  | Path of the Exchange Server Binaries. Could be changed if Exchange is not installed in the default folder path                                              | c:\Program Files\Microsoft\Exchange Server\V15\bin     | False    |
| BypassServerAvailabilityTest     | Boolean | Bypass the server availability test. If activated, the collector will try to work with all servers including inaccessible servers.                          | false                                                  | False    |
| ExplicitExchangeServerList       | Array   | List of explicit Exchange servers. If the previous parameter is activated, it could be good to build a static list of servers to use                        | []                                                     | False    |
| FunctionsListInline              | Boolean | Read the function list from the main configuration file. This option is retained for backward compatibility.                                                | false                                                  | False    |
| FunctionsListWithoutInternet     | Boolean | Functions list without internet. If activated, the collector will use the local files instead of files in the GitHub repository                             | false                                                  | False    |
| Beta                             | Boolean | Activating Beta feature, collecting Beta version of functions to execute.                                                                                   | false                                                  | False    |
| Useproxy                         | Boolean | Use Proxy boolean if you need it. The next option needs to be filled.                                                                                       | false                                                  | False    |
| ProxyUrl                         | String  | Proxy URL                                                                                                                                                   | http://proxy.dom.net:8080                              | False    |
| MaximalSentinelPacketSizeMb      | Int     | Max Packet size for Sentinel in Mb. **Recommended value with the Log Ingestion API is `0.9`** (payload limit of 1 MB per POST).                             | 32                                                     | False    |
| PaginationErrorThreshold         | Int     | Pagination Error Threshold when an executed function uses a pagination                                                                                      | 5                                                      | False    |
| UpdateVersionCheckingDeactivated | Boolean | Deactivate the version checking                                                                                                                             | false                                                  | False    |
| ExplicitESIDataPath              | String  | Explicit path where the collector stores its data (CSV, tracking, cache). If empty, the default location is computed automatically from the script context. | (empty)                                                | False    |
| DeactivateUDSLogs                | Boolean | Deactivate the log summary (called UDS Logs) at the end of the script.                                                                                      | false                                                  | False    |
| LogVerboseActivated              | Boolean | Log Verbose Activated                                                                                                                                       | true                                                   | False    |
| UDSLogProcessor                  | Array   | UDS Log Processor definition. By default UDS logs are displayed at the end. They can be stored in a file or an Azure Storage account if needed.             | [{Activated:true, StorageType:Output}]                 | False    |

### LogCollection

| Parameter                        | Type    | Description                                                                                                                                                                | Default              | Required                                        |
|----------------------------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|-------------------------------------------------|
| ActivateLogUpdloadToSentinel     | Boolean | Activate the log upload to Sentinel. If not activated, results are stored in a file only.                                                                                  | true                 | False                                           |
| WorkspaceId                      | String  | Workspace ID. **Used only when `SentinelLogIngestionAPIActivated` is `false`** (legacy Log Analytics HTTP Data Collector API).                                              | (guid)               | Legacy API only                                 |
| WorkspaceKey                     | String  | Workspace Key. **Used only when `SentinelLogIngestionAPIActivated` is `false`** (legacy Log Analytics HTTP Data Collector API).                                             | (key)                | Legacy API only                                 |
| LogTypeName                      | String  | Name of the target table (legacy API) or stream suffix (new API — `Custom-<LogTypeName>` is sent to the DCR).                                                              | ESIExchangeConfig    | False                                           |
| TogetherMode                     | Boolean | If true, results are stored in a file **in addition to** the Sentinel upload.                                                                                              | false                | False                                           |
| SentinelLogIngestionAPIActivated | Boolean | Activate the **Azure Monitor Log Ingestion API** (DCE / DCR / Entra ID identity). When `true`, the legacy `WorkspaceId` / `WorkspaceKey` are ignored.                       | false                | False                                           |
| DataCollectionEndpointURI        | String  | URI of the Data Collection Endpoint (DCE) displayed by the **Exchange Security Insights Online Collector (Azure Monitor)** data connector.                                   | (empty)              | Yes, if new API activated                       |
| DCRImmutableId                   | String  | Immutable ID of the target Data Collection Rule (DCR). One of the outputs of the ARM template (`OnPremises`, `Online`, or `MessageTracking`).                               | (empty)              | Yes, if new API activated                       |
| UseManagedIdentity               | Boolean | If `true`, the collector uses the system-assigned managed identity (recommended for Azure Automation). If `false`, uses a certificate-based Entra ID service principal.     | false                | False                                           |
| TargetLogTenantID                | String  | Tenant ID hosting the Entra ID application used for ingestion.                                                                                                             | (empty)              | Yes, if `UseManagedIdentity` = `false`          |
| TargetLogAppID                   | String  | Application (client) ID of the Entra ID application used for ingestion.                                                                                                    | (empty)              | Yes, if `UseManagedIdentity` = `false`          |
| TargetLogCertificateThumbprint   | String  | Thumbprint of the certificate authenticating the Entra ID application (local certificate store).                                                                           | (empty)              | Yes, if `UseManagedIdentity` = `false`          |
| TargetLogAppSecretReference      | String  | Name of the Automation variable referencing the certificate (Azure Automation, certificate mode).                                                                          | (empty)              | Azure Automation with certificate mode          |
| CSVOutputFile                    | String  | Default output file when `ActivateLogUpdloadToSentinel` is `false` or when `TogetherMode` is `true`. Replaces the previous `Output.DefaultOutputFile`.                       | ExchSecIns.csv       | False                                           |
| ExportDomainsInformation         | Boolean | Export AD Domain Information in Sentinel Table. Moved from the removed `Output` section.                                                                                   | True                 | False                                           |

> [!IMPORTANT]
> The Log Ingestion API replaces the legacy Log Analytics HTTP Data Collector API. If `SentinelLogIngestionAPIActivated` is `false`, the collector emits a runtime warning banner at each execution. For migration instructions, see [Upgrade an existing deployment](../../Documentations/README_LogIngestionAPI.md#upgrade-an-existing-deployment).

### InternetAddonCollectionConfiguration

Controls how the collector downloads Add-On files from GitHub. It replaces the historical implicit download through the raw content endpoint by giving the choice between the raw endpoint (unauthenticated) and the GitHub REST API (authenticated for higher rate limits or private repositories).

| Parameter                     | Type    | Description                                                                                                              | Default                    | Required                                                     |
|-------------------------------|---------|--------------------------------------------------------------------------------------------------------------------------|----------------------------|--------------------------------------------------------------|
| UseGithubAPI                  | Boolean | If `true`, download Add-Ons through the GitHub REST API. If `false`, use the raw content endpoint (no authentication).   | false                      | False                                                        |
| GithubRawUrlforOnPremises     | String  | Base URL of the raw endpoint for On-Premises Add-Ons.                                                                    | (Azure-Sentinel raw URL)   | Used when `UseGithubAPI` = `false`                           |
| GithubRawUrlforOnline         | String  | Base URL of the raw endpoint for Exchange Online Add-Ons.                                                                | (Azure-Sentinel raw URL)   | Used when `UseGithubAPI` = `false`                           |
| GithubAPIToken                | String  | GitHub Personal Access Token used when `GithubAPIConnectionType` = `Token` and the token is embedded in the config file. | (empty)                    | With `GithubAPIConnectionType` = `Token`                     |
| GithubAPITokenVariableName    | String  | Name of the environment variable holding the GitHub token when using `EnvironmentVariable` mode.                         | (empty)                    | With `GithubAPIConnectionType` = `EnvironmentVariable`       |
| GithubAPITokenSecretReference | String  | Name of the Azure Automation variable referencing the GitHub token when running as a runbook.                            | (empty)                    | With `GithubAPIConnectionType` = `AutomationVariable`        |
| GithubAPIConnectionType       | String  | Authentication mode for the GitHub API. Allowed values: `NoAuth`, `Token`, `EnvironmentVariable`, `AutomationVariable`.  | NoAuth                     | Yes, if `UseGithubAPI` = `true`                              |

### MGGraphAPIConnection

| Parameter                 | Type   | Description                  | Default | Required |
|---------------------------|--------|------------------------------|---------|----------|
| MGGraphAzureRMCertificate | String | MGGraph Azure RM Certificate |         | False    |
| MGGraphAzureRMAppId       | String | MGGraph Azure RM App Id      |         | False    |

### InstanceConfiguration

| Parameter                     | Type   | Description                                     | Default                                                                                              | Required |
|-------------------------------|--------|-------------------------------------------------|------------------------------------------------------------------------------------------------------|----------|
| Default                       | Object | Default configuration, see details below.       | {All:true, Capabilities:OP\|OL\|MGGRAPH\|ADINFOS}                                                     | False    |
| IIS-IoCs                      | Object | IIS IoCs configuration, see details below.      | {All:true, Category:IIS-IoCs, Capabilities:IIS, OutputName:ESIIISIoCs}                                | False    |
| ExchangeOnlineMessageTracking | Object | Exchange Online Message Tracking configuration. | {All:true, Category:OnlineMessageTracking, Capabilities:OL, OutputName:ExchangeOnlineMessageTracking} | False    |
| InstanceExample               | Object | Instance Example configuration.                 | {SelectedAddons:[Filename1, Filename2], FileteredAddons:[Filename1, Filename2]}                      | False    |

### AuditFunctionsFiles

| Parameter   | Type    | Description | Default      | Required |
|-------------|---------|-------------|--------------|----------|
| Filename    | String  | Filename    | FiletoIgnore | False    |
| Deactivated | Boolean | Deactivated | false        | False    |

### AuditFunctionProtectedArea

| Parameter       | Type   | Description      | Default | Required |
|-----------------|--------|------------------|---------|----------|
| ContentCheckSum | String | Content CheckSum |         | False    |

## Description

This configuration file is used to configure the CollectExchSecIns script. It contains all the parameters needed to run the script.
Below are specific parameters and their description.

### UDSLogProcessor

`UDSLogProcessor` controls how UDS logs are displayed or stored. Logs can be written to a file or an Azure Storage account, or displayed only.
`UDSLogProcessor` is an array of objects. Each object contains the following parameters:

- Activated: Boolean. If true, the log will be processed.
- StorageType: String. The type of storage. Could be Output, File or AzureStorageAccount.
- StoragePath: String. The path of the storage. If the StorageType is File, this parameter is required.
- Prefix: String. The prefix of the file or the Blob. It's optional.
- LogStorageRetentionDays: Int. The retention days of the log in the storage. It's optional.
- StorageAccountName: String. The name of the storage account. If the StorageType is AzureStorageAccount, this parameter is required.
- StorageBlobContainer: String. The name of the storage container. If the StorageType is AzureStorageAccount, this parameter is required.
- ConnexionType: String. Connection type. Supported values are `ManagedIdentity` and `Certificate`. This parameter is required when `StorageType` is `AzureStorageAccount`.
- TenantId: String. The tenant id. If the StorageType is AzureStorageAccount, this parameter is required.
- ApplicationID: String. Application ID. This parameter is required when `StorageType` is `AzureStorageAccount` and `ConnexionType` is `Certificate`.
- CertificateThumbprint: String. Certificate thumbprint. This parameter is required when `StorageType` is `AzureStorageAccount` and `ConnexionType` is `Certificate`.

### Azure Monitor Log Ingestion API parameters

Starting with configuration version 3.0, the collector natively supports the Azure Monitor **Log Ingestion API** in addition to the legacy Log Analytics HTTP Data Collector API. The switch between the two APIs is controlled by `SentinelLogIngestionAPIActivated` in the `LogCollection` section. Both APIs remain supported to enable a phased migration.

Prerequisites when `SentinelLogIngestionAPIActivated` is `true`:

- Deploy **Exchange Security Insights Online Collector (Azure Monitor)** to create the Data Collection Endpoint, Data Collection Rule, and table.
- Deploy the Azure Automation template to create the Automation account with a system-assigned managed identity.
- Keep `UseManagedIdentity` set to `true`.
- The Automation template assigns **Monitoring Metrics Publisher** to the managed identity on the DCR.

Parameter selection matrix:

| Scenario | Required parameters |
|----------|---------------------|
| Legacy Log Analytics API | `SentinelLogIngestionAPIActivated = false`, `WorkspaceId`, `WorkspaceKey`, `LogTypeName` |
| Azure Monitor with the Automation account managed identity | `SentinelLogIngestionAPIActivated = true`, `DataCollectionEndpointURI`, `DCRImmutableId`, `UseManagedIdentity = true`, `TargetLogTenantID`, `LogTypeName = ESIExchangeOnlineConfig` |

Recommended companion setting: set `MaximalSentinelPacketSizeMb` to `0.9` when the Log Ingestion API is activated (payload limit is 1 MB per POST).

Full Azure Monitor setup and migration procedure: [README_LogIngestionAPI.md](../../Documentations/README_LogIngestionAPI.md).

### InternetAddonCollectionConfiguration

The `InternetAddonCollectionConfiguration` section controls how the collector retrieves Add-On configuration files (JSON) from GitHub.

Two modes are supported:

- **Raw content endpoint** (`UseGithubAPI = false`) — unauthenticated download from `raw.githubusercontent.com`. Recommended for public repositories and low-frequency runs. Requires the `GithubRawUrlforOnPremises` and `GithubRawUrlforOnline` base URLs to point at the target branch.
- **GitHub REST API** (`UseGithubAPI = true`) — authenticated download from the GitHub API. Provides higher rate limits and supports private repositories. Authentication mode is chosen through `GithubAPIConnectionType`:
  - `NoAuth` — anonymous API call. Subject to strict rate limits.
  - `Token` — reads the PAT from `GithubAPIToken` (embedded in the config).
  - `EnvironmentVariable` — reads the PAT from the environment variable whose name is `GithubAPITokenVariableName`.
  - `AutomationVariable` — reads the PAT from the Azure Automation variable whose name is `GithubAPITokenSecretReference` (recommended for Runbook deployments).

> [!TIP]
> For Runbook deployments accessing a private repository, use `UseGithubAPI = true` + `GithubAPIConnectionType = AutomationVariable` and store the PAT as an **encrypted** Automation variable.

### InstanceConfiguration

`InstanceConfiguration` defines multiple collection instances. Three standard instances are available: `Default`, `IIS-IoCs`, and `ExchangeOnlineMessageTracking`. Additional instances can be created from `InstanceExample`, using the intended instance name as the property name.
`InstanceConfiguration` is an object that contains the following parameters:

- Default: Object. Default configuration, mandatory. It contains the following parameters:
  - All: Boolean. If true (by default), all the functions are activated.
  - Capabilities: String. Capabilities to activate: `OP` for Exchange On-Premises, `OL` for Exchange Online, `MGGRAPH` for Microsoft Graph, and `ADINFOS` for Active Directory information. Capabilities are used only when required by a function.
  - SelectedAddons: Array, Mandatory if All is deactivated. The list of selected addons to activate by inserting the filename of the addon like "ESICollector-POPIMAPConfiguration.json".
  - FileteredAddons: Array, optional. Add-on filenames to deactivate, for example `ESICollector-POPIMAPConfiguration.json`.
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
  - FileteredAddons: Array. Add-on filenames to deactivate, for example `ESICollector-POPIMAPConfiguration.json`.
  - Capabilities: String. Capabilities to activate: `OP`, `OL`, `MGGRAPH`, `ADINFOS`, or `IIS`.
  - OutputName: String. Name of the output file or Log Analytics table.
  - Category: String, optional. The category of the functions to activate. This parameter is linked to "Add-Ons" folders. If the category is not present, the selected functions are selected from the root Add-ons folder. If the category is present, the selected functions are selected from the category folder. 2 categories are available by default: "IIS" and "OnlineMessageTracking".

### AuditFunctionsFiles

`AuditFunctionsFiles` is an array of objects used to exclude a set of functions grouped in a file such as `ESICollector-POPIMAPConfiguration.json`. Each object contains the following parameters:

- Filename: String. The filename to ignore like "ESICollector-POPIMAPConfiguration.json".
- Deactivated: Boolean. If true, the function file is deactivated.

### Other parameters

The parameter AuditFunctionProtectedArea is not used for the moment. They are reserved for future use.
The parameter AuditFunctions is not used anymore, only present for backward comptability.

## Migration from configuration version 2.5 to 3.0

Configuration version 3.0 introduces the following structural changes:

- The whole **`Output` section has been removed**.
  - `Output.DefaultOutputFile` → `LogCollection.CSVOutputFile`
  - `Output.ExportDomainsInformation` → `LogCollection.ExportDomainsInformation`
- New parameters in **`LogCollection`** to enable the Azure Monitor Log Ingestion API — see [LogCollection](#logcollection) and [Azure Monitor Log Ingestion API parameters](#azure-monitor-log-ingestion-api-parameters).
- New **`InternetAddonCollectionConfiguration`** section to control Add-On downloads through the GitHub raw endpoint or the authenticated GitHub REST API.
- New optional parameter **`ExplicitESIDataPath`** in `Advanced` to override the default data folder used by the collector.
- The default of **`MaximalSentinelPacketSizeMb`** should be lowered to `0.9` when the new API is used.

Legacy configurations continue to work — the collector keeps supporting the legacy Log Analytics HTTP Data Collector API and displays a runtime warning banner at each execution until the migration is completed. See [Upgrade an existing deployment](../../Documentations/README_LogIngestionAPI.md#upgrade-an-existing-deployment).
