# Exchange Security Insights Online Collector package and upgrade guide

This README accompanies the Exchange Online collector package. It documents the current version, Azure Monitor configuration changes, runbook update procedure, data model changes, and version availability.

For deployment and migration, see [Configure the Exchange Security Insights Online Collector with Azure Monitor](../../Documentations/README_LogIngestionAPI.md). For modules and permissions, see [Collector prerequisites and permissions](../../Documentations/ESICollector.md). For individual settings, see the [configuration parameter reference](./Parameters.md).

## Current version

The current collector version is **8.0.0.0**.

## Upgrade from 7.6.0.1 to 8.0.0.0

> [!IMPORTANT]
> Version 8.0.0.0 adds native support for the Azure Monitor Log Ingestion API. Existing deployments can upgrade the runbook before switching from the legacy Log Analytics HTTP Data Collector API.

### Upgrade procedure

1. Back up the `GlobalConfiguration` variable in the existing Automation account.
2. Update the **Microsoft Exchange Security for Exchange Online** solution in Microsoft Sentinel Content Hub.
3. Configure **Exchange Security Insights Online Collector (Azure Monitor)** and select **Deploy Exchange Collector Push connector resources**.
4. Record the DCE URI and DCR immutable ID displayed by the connector. Retrieve the DCR name by following [Retrieve the DCR name](../../Documentations/README_LogIngestionAPI.md#retrieve-the-dcr-name).
5. Update the existing `Start-ESICollector` runbook and `GlobalConfiguration` variable by following [Update an existing Azure Automation deployment](../../Documentations/README_LogIngestionAPI.md#update-an-existing-azure-automation-deployment).
6. Verify that the runbook, modules, configuration variables, and daily schedule were updated.
7. Verify that the Automation account system-assigned managed identity has **Monitoring Metrics Publisher** on the DCR.
8. Run `Start-ESICollector` manually and verify ingestion.

For the complete procedure, see [Upgrade an existing deployment](../../Documentations/README_LogIngestionAPI.md#upgrade-an-existing-deployment).

## Azure Monitor configuration

The Automation deployment generates the `GlobalConfiguration` variable with:

| Setting | Required value |
|---------|----------------|
| `SentinelLogIngestionAPIActivated` | `true` |
| `DataCollectionEndpointURI` | DCE URI displayed by the data connector |
| `DCRImmutableId` | DCR immutable ID displayed by the data connector |
| `UseManagedIdentity` | `true` |
| `TargetLogTenantID` | Microsoft Entra tenant ID |
| `LogTypeName` | `ESIExchangeOnlineConfig` |

The legacy `WorkspaceId` and `WorkspaceKey` settings are not used when the Log Ingestion API is enabled.

For managed identity, Microsoft Graph, Exchange Online, and directory role requirements, see [Collector prerequisites and permissions](../../Documentations/ESICollector.md).

## Data model changes

The Azure Monitor table includes `Identity_*` subproperty columns extracted during ingestion by the DCR transform:

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

The original `Identity_s` string column is preserved. Existing content that uses `Identity_s` remains compatible.

## Version availability policy

Only the two most recent collector versions are retained in the public repository.

The unversioned ZIP package always contains the latest available collector version.
