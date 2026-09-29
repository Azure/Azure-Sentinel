# Exchange Security Insights Collector

## Overview

The Exchange Security Insights Collector is a PowerShell-based data collection tool for Exchange Server and Exchange Online environments. It collects security configuration data and sends it to Microsoft Sentinel for use by the Microsoft Exchange Security solutions.

For on-premises Exchange environments, the collector runs on a Windows machine and can be scheduled to execute at regular intervals. For more information about Exchange Online Solution, see the [Microsoft Exchange Security - Exchange Online solution](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online).

For installation and configuration instructions, see the [Exchange Security Insights Collector documentation](../../Documentations/ESICollector.md).

For a detailed description of the configuration parameters, see the [configuration parameter reference](./Parameters.md).

## Current version

The current version of the Exchange Security Insights Collector is **8.0.0.0**.

## Upgrade paths

### From 7.6.0.1 to 8.0.0.0

> [!IMPORTANT]
> Version 8.0.0.0 adds native support for the Azure Monitor Log Ingestion API, based on Data Collection Endpoints (DCEs) and Data Collection Rules (DCRs). This API replaces the legacy Log Analytics HTTP Data Collector API.
>
> The collector continues to support both APIs. The API used is controlled by the `SentinelLogIngestionAPIActivated` setting, allowing the migration to be completed in two phases:
>
> 1. Upgrade the collector while continuing to use the legacy API.
> 2. Deploy the required Azure resources and switch to the Log Ingestion API.
>
> For complete migration instructions, see [Upgrade an existing deployment](../../Documentations/README_LogIngestionAPI.md#upgrade-an-existing-deployment).

#### Configuration changes

The configuration schema remains backward compatible. Existing configurations continue to work without changes, but the collector displays a warning until migration to the Log Ingestion API is completed.

The following settings in the `LogCollection` section are required only when using the Log Ingestion API:

| Setting | Description |
|---------|-------------|
| `SentinelLogIngestionAPIActivated` | Set to `true` to use the Log Ingestion API. The default is `false`. |
| `DataCollectionEndpointURI` | URI of the DCE created by the `azuredeploy_ESI_LogIngestionAPI.json` ARM template. |
| `DCRImmutableId` | Immutable ID of the target DCR for Exchange Online, Exchange on-premises, or Message Tracking data. |
| `TargetLogTenantID` | Microsoft Entra tenant ID used for certificate-based authentication when `UseManagedIdentity` is `false`. |
| `TargetLogAppID` | Application ID used for certificate-based authentication when `UseManagedIdentity` is `false`. |
| `TargetLogCertificateThumbprint` | Thumbprint of the certificate used for authentication when `UseManagedIdentity` is `false`. |

Additional configuration changes:

- `ExportDomainsInformation` has moved from the `Global` section to the `LogCollection` section. Its default value remains `true`.
- In the `Advanced` section:
  - `MaximalSentinelPacketSizeMb` defaults to `0.9` when the Log Ingestion API is used because each POST request has a 1 MB payload limit.
  - New GitHub download settings allow configuration retrieval through the GitHub API instead of a raw file download.

After configuring the new connector, go to the collect server and update the configuration file manually or use the **WinformConfig editor** at `ExchSecIns/WinformConfig/SetupCollectExchSecConfiguration.ps1`. The editor validates the payload and hides the legacy `WorkspaceId` and `WorkspaceKey` fields when the Log Ingestion API is enabled.

#### Collector update

1. Back up the existing `Config\CollectExchSecConfiguration.json` file.
2. Before extracting the package, unblock the downloaded ZIP file:

   ```powershell
   Unblock-File -LiteralPath .\CollectExchSecIns.zip
   ```

3. Extract `CollectExchSecIns.zip` into a new folder.
4. Replace the existing `CollectExchSecIns.ps1` file with the new version.
5. Copy the new `WinformConfig` folder and all its contents to the collector directory.

If the package has already been extracted, unblock every file in `WinformConfig` and its subfolders:

```powershell
Get-ChildItem -LiteralPath .\WinformConfig -Recurse -File |
    Unblock-File
```

- **Continue using the legacy API temporarily:** No additional changes are required. The collector displays a warning during each execution until the migration is completed.
- **Switch to the Log Ingestion API:**
  1. Update the solution in Microsoft Sentinel Content Hub. The update deploys the **Exchange Security Insights On-Premises Collector (Azure Monitor)** data connector.
  2. Open **Data connectors** and follow the instructions on the connector page.
  3. Go to the on-premises collector server.
  4. Update the required configuration settings by editing the configuration file or, preferably, by using the [WinformConfig editor](../../Documentations/WinformConfigReadme.md).
  5. Run the collector manually.
  6. Verify that data is ingested into the expected custom tables and that the collector completes without authentication or ingestion errors.

#### Data model changes

The new tables include the following `Identity` subproperty columns, which are extracted during ingestion by the DCR `transformKql`:

- `Identity_Depth_d`
- `Identity_DistinguishedName_s`
- `Identity_DomainId_s`
- `Identity_IsDeleted_b`
- `Identity_IsRelativeDn_b`
- `Identity_Name_s`
- `Identity_ObjectGuid_g`
- `Identity_Parent_s`
- `Identity_PartitionFQDN_s`
- `Identity_PartitionGuid_g`
- `Identity_Rdn_s`

The original `Identity_s` string column is preserved. Existing analytic rules, hunting queries, and workbooks that use `Identity_s` remain compatible.

### Legacy upgrade history

For every upgrade path below, replace the existing collector script with the new version. The table lists any additional configuration changes.

| Upgrade path | Configuration changes |
|--------------|-----------------------|
| 7.6.0.0 to 7.6.0.1 | No configuration changes are required. |
| 7.5.2.2 to 7.6.0.0 | No configuration changes are required. |
| 7.5.2.1 to 7.5.2.2 | Update the configuration file to the new version and preserve all custom settings. |
| 7.5.2.0 to 7.5.2.1 | Add `PaginationErrorThreshold` to the `Advanced` section. You can also add the optional `ExchangeOnlineMessageTracking` category described below. |
| 7.5.1.1 to 7.5.2.0 | No configuration changes are required. |
| 7.5.0 to 7.5.1.1 | Add `PaginationErrorThreshold` to the `Advanced` section. You can also add the optional `ExchangeOnlineMessageTracking` category described below. |
| 7.4.2 to 7.5.0 | No configuration changes are required. |
| 7.3.2 to 7.4.2 | Add the new parameters to the `Advanced` section and configure a managed identity for Exchange Online as described below. |
| 7.3.1 to 7.3.2 | Add the new parameters to the `Advanced` section. |
| 7.3.0 to 7.3.1 | No configuration changes are required. |
| 7.2.0 to 7.3.0 | Add the `Beta` property to the `Advanced` section as described below. |

#### Beta setting

Starting with version 7.3.0, the `Advanced` section includes a `Beta` property. Its default value is `false`. Set it to `true` only when using beta add-on files. Beta features may contain defects and should be used with caution.

## Version availability policy

Only the two most recent collector versions are retained in the public repository.

The unversioned ZIP package always contains the latest available version of the collector.
