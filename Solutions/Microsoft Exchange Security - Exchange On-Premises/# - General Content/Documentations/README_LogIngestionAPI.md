# Configure the Exchange Security Insights On-Premises Collector with Azure Monitor

## Overview

The **Exchange Security Insights On-Premises Collector (Azure Monitor)** data connector configures the Azure resources required by the Exchange Security Insights Collector to send data through the Azure Monitor Log Ingestion API.

The connector deployment creates and configures:

- The `ESIAPIExchangeOnPremConfig_CL` custom Log Analytics table.
- The Data Collection Endpoint (DCE).
- The Data Collection Rule (DCR).
- The Microsoft Entra application used by the collector.
- The required link and permissions between the application and the DCR.

After the connector deployment completes, the remaining local action is to configure `Config\CollectExchSecConfiguration.json` on the collector server.

## Prerequisites

Before starting, verify that:

- The **Microsoft Exchange Security for Exchange On-Premises** solution is installed in Microsoft Sentinel.
- You have sufficient permissions to configure the data connector and deploy its resources.
- Version 8.0.0.0 or later of the Exchange Security Insights Collector is available on the collector server.
- The collector server meets the requirements documented in [Exchange Security Insights Collector for Exchange Server](./ESICollector.md).
- You are a local administrator on the collector server.

## Choose the appropriate scenario

The procedure differs depending on whether this is a new collector deployment or an upgrade of an existing deployment.

### New deployment

For a new deployment, create a new collector configuration. Do not follow an upgrade or migration procedure.

1. Install the **Microsoft Exchange Security for Exchange On-Premises** solution from Microsoft Sentinel Content Hub.
2. Open **Data connectors** in Microsoft Sentinel.
3. Select **Exchange Security Insights On-Premises Collector (Azure Monitor)**.
4. Open the connector page and select **Deploy Exchange Collector Push connector resources**.
5. Wait for the connector deployment to complete.
6. Create the authentication certificate and add its public part to the Entra application created by the connector by following [Create the authentication certificate](#create-the-authentication-certificate).
7. Download and extract the latest `CollectExchSecIns.zip` package on the collector server.
8. Use the [`WinformConfig\SetupCollectExchSecConfiguration.ps1` user interface](./WinformConfigReadme.md) to configure the new `Config\CollectExchSecConfiguration.json` file and create the mandatory scheduled task during the same setup session. Alternatively, `setup.ps1` can configure the file and create the task.
9. Run the collector manually and verify ingestion.

### Upgrade an existing deployment

For an existing deployment, preserve the current configuration and update only the settings required for Azure Monitor ingestion.

1. Update the collector to version 8.0.0.0 or later by following the [collector upgrade instructions](../Solutions/ESICollector/README.md). This includes deploying the updated `WinformConfig` folder.
2. Back up the existing `Config\CollectExchSecConfiguration.json` file.
3. Update the **Microsoft Exchange Security for Exchange On-Premises** solution from Microsoft Sentinel Content Hub.
4. Open **Data connectors** in Microsoft Sentinel.
5. Select the new **Exchange Security Insights On-Premises Collector (Azure Monitor)** connector.
6. Open the connector page and select **Deploy Exchange Collector Push connector resources**.
7. Wait for the connector deployment to complete.
8. Create or select the authentication certificate and add its public part to the Entra application created by the connector by following [Create the authentication certificate](#create-the-authentication-certificate).
9. Update the existing `Config\CollectExchSecConfiguration.json` file. Prefer the [`WinformConfig\SetupCollectExchSecConfiguration.ps1` user interface](./WinformConfigReadme.md), and preserve all existing environment, instance, scheduling, and add-on settings.
10. Verify that the mandatory scheduled task still points to the updated collector. If it is missing, create it during the same WinformConfig setup session.
11. Run the collector manually and verify ingestion before relying on the scheduled task.

## Create the authentication certificate

Complete this section only after **Deploy Exchange Collector Push connector resources** has finished and the Entra application exists.

Run the following commands from an elevated Windows PowerShell session on the collector server:

```powershell
# Create a self-signed certificate valid for 2 years
$cert = New-SelfSignedCertificate `
    -Subject "CN=ESI-Collector-Auth" `
    -CertStoreLocation "Cert:\LocalMachine\My" `
    -KeyExportPolicy Exportable `
    -KeySpec Signature `
    -KeyLength 2048 `
    -HashAlgorithm SHA256 `
    -NotAfter (Get-Date).AddYears(2)

# Display the thumbprint (you need it for configuration)
Write-Host "Certificate Thumbprint: $($cert.Thumbprint)"

# Export the public key (.cer) for uploading to the Entra ID application
Export-Certificate -Cert $cert -FilePath ".\ESI-Collector-Auth.cer" -Type CERT
```

The exported `.cer` file contains only the public certificate. The private key remains in `Cert:\LocalMachine\My`.

### Add the certificate to the Entra application

1. Copy the **Entra application ID** displayed on the data connector page.
2. Open the [Microsoft Entra admin center](https://entra.microsoft.com/).
3. Go to **Identity** > **Applications** > **App registrations**.
4. Select **All applications**.
5. Search for the application by using its **Application (client) ID** and open it.
6. Select **Certificates & secrets**.
7. Open the **Certificates** tab.
8. Select **Upload certificate**.
9. Select the `ESI-Collector-Auth.cer` file, optionally enter a description, and select **Add**.
10. Verify that the certificate appears with the expected thumbprint and expiration date.

Do not create a client secret. The on-premises collector authenticates by using the certificate.

### Grant the service account access to the private key

Complete this step when the scheduled task runs under an account that is not a member of the local **Administrators** group.

On the collector server:

1. Run `certlm.msc`.
2. Go to **Certificates (Local Computer)** > **Personal** > **Certificates**.
3. Locate the `ESI-Collector-Auth` certificate.
4. Right-click the certificate and select **All Tasks** > **Manage Private Keys**.
5. Add the collector's service account and grant it **Read** permission.
6. Record the certificate thumbprint for the WinformConfig setup.

## Values provided by the data connector

After deployment, the connector page displays the values required to configure the collector:

- Tenant ID (Directory ID).
- Entra application ID.
- Data Collection Endpoint URI.
- Data Collection Rule immutable ID.
- Stream name: `Custom-ESIExchangeConfig`.

You must also provide the thumbprint of the authentication certificate created before configuring the collector.

Use the [WinformConfig editor](./WinformConfigReadme.md) as the preferred method for applying these values and creating the mandatory scheduled task during the same configuration session. The `setup.ps1` script remains available as an alternative guided configuration method.

The on-premises collector uses certificate authentication. Do not configure an application secret.

## Validate the JSON configuration

The configuration tools update the authentication fields according to the selected mode. At minimum, verify that the following Azure Monitor settings are configured:

```json
{
  "LogCollection": {
    "ActivateLogUpdloadToSentinel": "true",
    "SentinelLogIngestionAPIActivated": "true",
    "DataCollectionEndpointURI": "<value displayed by the data connector>",
    "DCRImmutableId": "<value displayed by the data connector>",
    "TargetLogTenantID": "<tenant ID displayed by the data connector>",
    "TargetLogAppID": "<application ID displayed by the data connector>",
    "TargetLogCertificateThumbprint": "<authentication certificate thumbprint>",
    "LogTypeName": "ESIExchangeConfig"
  }
}
```

This is a partial example. Do not replace the complete `LogCollection` section with this example.

When the Log Ingestion API is enabled:

- `WorkspaceId` and `WorkspaceKey` are legacy settings and are not used for ingestion.
- `DataCollectionEndpointURI` must match the DCE displayed by the connector.
- `DCRImmutableId` must match the DCR displayed by the connector.
- `TargetLogCertificateThumbprint` must identify a certificate with a private key accessible to the collector's service account.
- `LogTypeName` must remain `ESIExchangeConfig`, which produces the `Custom-ESIExchangeConfig` stream used by the DCR.

## Validate data ingestion

Run the collector manually after saving the configuration. Confirm that it completes without authentication or ingestion errors.

Then run the following query in the Microsoft Sentinel workspace:

```kql
ESIAPIExchangeOnPremConfig_CL
| summarize Entries = count(), LastIngestion = max(TimeGenerated)
    by GenerationInstanceID_g, ESIEnvironment_s
| order by LastIngestion desc
```

The data connector status should change to **Connected** after data is received.

## Data destination

The connector sends data through the following route:

| Component | Value |
|-----------|-------|
| Table | `ESIAPIExchangeOnPremConfig_CL` |
| Stream | `Custom-ESIExchangeConfig` |
| Collector `LogTypeName` | `ESIExchangeConfig` |

Column suffixes follow Log Analytics conventions:

- `_s`: string
- `_d`: real
- `_g`: GUID
- `_b`: boolean
- `_t`: datetime
- `_l`: long
- `_i`: integer

The DCR transform extracts the `Identity_*` columns from the source `Identity` object. The original `Identity_s` column is preserved for compatibility with existing analytics, hunting queries, and workbooks.

## After upgrading an existing deployment

### Post-migration cleanup

After several successful scheduled executions:

1. Keep the backed-up legacy configuration for the agreed rollback period.
2. Remove the legacy workspace key from scripts, scheduled-task arguments, and unsecured files.
3. Remove the workspace key from password vaults only after the rollback period ends.
4. Update custom analytics, hunting queries, or workbooks that directly reference `ESIExchangeConfig_CL`.
5. Retain the legacy table for historical data until its retention period expires.

Do not delete the DCE, DCR, Entra application, certificate, or new table while the collector uses the Log Ingestion API.

### Rollback during validation

Rollback is intended only for the validation period and only while the legacy API remains available.

1. Stop the scheduled task.
2. Restore the backed-up `CollectExchSecConfiguration.json` file, including the legacy `WorkspaceId` and `WorkspaceKey`.
3. Confirm that `SentinelLogIngestionAPIActivated` is set to `false`.
4. Run the collector manually.
5. Verify that new data appears in `ESIExchangeConfig_CL`.
6. Restart the scheduled task.

The Azure Monitor resources can remain deployed while the migration issue is investigated.

## Troubleshooting

### The new data connector is not available

Confirm that the **Microsoft Exchange Security for Exchange On-Premises** solution has been installed or updated from Content Hub.

### Deployment values are not displayed

Confirm that **Deploy Exchange Collector Push connector resources** completed successfully on the data connector page. Do not replace this action with a manual ARM template deployment.

### Authentication failure

Reopen the configuration tool and verify:

- The tenant and Entra application information against the values displayed by the data connector.
- The certificate thumbprint.
- The presence of the certificate and its private key in a certificate store accessible to the collector's service account.
- The presence of the public certificate on the Entra application created by the connector.

### HTTP 400 or `InvalidPayload`

Verify that:

- `DCRImmutableId` matches the value displayed by the connector.
- `DataCollectionEndpointURI` contains the correct ingestion endpoint.
- `LogTypeName` is `ESIExchangeConfig`.
- The collector is version 8.0.0.0 or later.

### HTTP 401 or 403

Confirm that the connector deployment completed successfully and that the collector is using the Entra application created by that deployment. If necessary, redeploy the connector resources from the data connector page instead of assigning the DCR role manually.

### No data appears in the table

1. Run the collector manually.
2. Review the collector logs for authentication, payload, or endpoint errors.
3. Confirm that `SentinelLogIngestionAPIActivated` is set to `"true"`.
4. Confirm that the DCE, DCR immutable ID, and stream settings match the data connector values.
5. Run the validation query again after several minutes.

## Related documentation

- [Exchange Security Insights Collector prerequisites](./ESICollector.md)
- [Collector configuration parameters](../Solutions/ESICollector/Parameters.md)
- [Collector upgrade instructions](../Solutions/ESICollector/README.md)
- [WinformConfig editor](./WinformConfigReadme.md)
- [Forwarder quick start](../Forwarder/QUICKSTART-Forwarder.md)
- [Forwarder Pickup Processor reference](../Forwarder/README-ForwarderPickup.md)
