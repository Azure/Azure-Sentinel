# **Exchange Security Insight Collector Download**

## Description

The Exchange Security Insight Collector is a PowerShell script that collects data from Exchange Servers and Exchange Online. The script is designed to be run on a Windows machine and can be scheduled to run at regular intervals. The script collects data from Exchange Servers and Exchange Online and sends it to the Microsoft Exchange Security Insight solution for Microsoft Sentinel.

You can refer to the Exchange Securitty Insight Collector [here](https://github.com/nlepagnez/ESI-PublicContent/blob/main/ESICollector.md)

Parameters are described in the Configuration file. Explanation of the parameters is available in the [the Parameters description document](./Parameters.md)

## Versioning

## Actual Version : 8.0.0.0

## Upgrade paths

### From 7.6.0.1 to 8.0.0.0

> [!IMPORTANT]
> Version 8.0.0.0 introduces native support for the **Azure Monitor Log Ingestion API** (DCE/DCR based) that replaces the legacy Log Analytics HTTP Data Collector API. The collector still supports both APIs, controlled by the `SentinelLogIngestionAPIActivated` toggle, so the upgrade can be performed in two phases (script upgrade first, cutover later).
>
> Full migration guide : [Migrate from the Log Analytics HTTP Data Collector API to the Log Ingestion API](https://aka.ms/MES-Migrate_From_LogAnalyticsAPI_To_LogIngestionAPI).

#### **Configuration File**

The configuration schema is backward compatible. Legacy configurations keep working with no change and will trigger a runtime warning banner to remind operators to migrate.

New or updated settings:

- **`LogCollection` section** — new keys required only if you switch to the Log Ingestion API:
  - `SentinelLogIngestionAPIActivated` : `true` to activate the new API. Default `false`.
  - `DataCollectionEndpointURI` : DCE URI produced by the ARM template (`azuredeploy_ESI_LogIngestionAPI.json`).
  - `DCRImmutableId` : Immutable ID of the target DCR (Online, OnPremises, or MessageTracking).
  - `UseManagedIdentity` : `true` for Azure Automation with system-assigned managed identity.
  - `TargetLogTenantID` / `TargetLogAppID` / `TargetLogCertificateThumbprint` : required when `UseManagedIdentity` is `false` (certificate-based service principal).
  - `TargetLogAppSecretReference` : Automation variable name referencing the certificate (Azure Automation, certificate mode).
- **`ExportDomainsInformation`** has moved from the `Global` section to the `LogCollection` section. Default value stays `true`.
- **`Advanced` section**:
  - `MaximalSentinelPacketSizeMb` default lowered to `0.9` when the Log Ingestion API is used (payload limit of 1 MB per POST).
  - New GitHub download settings for configuration retrieval via the GitHub API instead of raw download.

Update the file manually or use the **WinformConfig editor** (`ExchSecIns/WinformConfig/SetupCollectExchSecConfiguration.ps1`), which validates the payload and hides the legacy `WorkspaceId` / `WorkspaceKey` fields once the Log Ingestion API is activated.

#### **ESI Collector Script**

Replace the old script version with the new one. Additional tasks depending on your target API:

- **Staying on the legacy API temporarily** : nothing else to do. The collector will display a runtime warning banner at each execution until the migration is completed.
- **Switching to the Log Ingestion API** :
  1. Deploy the ARM template `ExchSecIns/Deployments/azuredeploy_ESI_LogIngestionAPI.json` to provision the DCE, tables (`ESIAPIExchangeOnPremConfig_CL`, `ESIAPIExchangeOnlineConfig_CL`, `ExchangeOnlineMessageTracking_CL`) and DCRs.
  2. Assign **Monitoring Metrics Publisher** on each target DCR to the identity used by the collector (managed identity or Entra ID service principal).
  3. Update the configuration keys listed above.
  4. Trigger a manual run and verify the new `_CL` tables are populated.

#### **Data model changes**

The new tables include the `Identity` sub-property columns extracted at ingestion by the DCR `transformKql` : `Identity_Depth_d`, `Identity_DistinguishedName_s`, `Identity_DomainId_s`, `Identity_IsDeleted_b`, `Identity_IsRelativeDn_b`, `Identity_Name_s`, `Identity_ObjectGuid_g`, `Identity_Parent_s`, `Identity_PartitionFQDN_s`, `Identity_PartitionGuid_g`, `Identity_Rdn_s`. The original `Identity_s` string column is preserved. Analytic rules, hunting queries and workbooks that already rely on `Identity_s` remain valid.

### From 7.6.0.0 to 7.6.0.1

#### **Configuration File**

Nothing to change

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.2.2 to 7.6.0.0

#### **Configuration File**

Notning to change

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.2.1 to 7.5.2.2

#### **Configuration File**

Update Config File to the new version. Be carefull to keep your custom parameters.

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.2.1 to 7.5.2.2

#### **Configuration File**

Nothing to change

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.2.0 to 7.5.2.1

#### **Configuration File**

Parameter "PaginationErrorThreshold": 5 is added in the Advanced part

A new category OnlineMessageTracking could be added. The segment can be added in InstanceConfiguration part : 
    "ExchangeOnlineMessageTracking":{
			"All":"true",
			"Category":"OnlineMessageTracking",
			"Capabilities":"OL",
			"OutputName":"ExchangeOnlineMessageTracking"
		}

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.1.1 to 7.5.2.0

#### **Configuration File**

Nothing changed

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.0 to 7.5.1.1

#### **Configuration File**

Parameter "PaginationErrorThreshold": 5 is added in the Advanced part

A new category OnlineMessageTracking could be added. The segment can be added in InstanceConfiguration part : 
    "ExchangeOnlineMessageTracking":{
			"All":"true",
			"Category":"OnlineMessageTracking",
			"Capabilities":"OL",
			"OutputName":"ExchangeOnlineMessageTracking"
		}

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.


### From 7.4.2 to 7.5.0

#### **Configuration File**

Nothing changed

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.


### From 7.3.2 to 7.4.2

#### **Configuration File**

Parameters added in Advanced Section

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.
Attention, now ManagedIdentity is used for Exchange Online instead of RunAs Account.
Assign rights to Managed Identity following Standard Procedure : [EXO for ManagedIdentity](https://learn.microsoft.com/en-us/powershell/exchange/connect-exo-powershell-managed-identity?view=exchange-ps#step-4-grant-the-exchangemanageasapp-api-permission-for-the-managed-identity-to-call-exchange-online)

### From 7.3.1 to 7.3.2

#### **Configuration File**

Parameters added in Advanced Section

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.


### From 7.3.0 to 7.3.1

#### **Configuration File**

No changes in Configuration file

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.2.0 to 7.3.0

#### **Configuration File**

The only change on the configuration file is adding a "Beta" Property in "Advanced" part. By default "Beta" is "False". If you decide to use Beta off Add-On files, you can switch this parameter to true. Attention, bugs can be present in Beta mode.

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

## Download availability/Rules

Only 2 major versions are kept on the public repository.
The zip file without versioning correspond to the latest version of the Collector.
