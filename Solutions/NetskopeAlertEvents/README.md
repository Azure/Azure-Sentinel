# Netskope Alerts & Events Solution for Microsoft Sentinel

## Overview

The **Netskope Alerts & Events** solution streams alert and event logs from the
Netskope Security Cloud into Microsoft Sentinel using **Netskope Log Streaming (NLS)**.
Logs are delivered to an Azure Blob Storage container as **gzip-compressed,
positional CSV** and ingested by Sentinel's **Codeless Connector Framework (CCF)**
Blob Storage connector into the custom Log Analytics table
**`NetskopeAlertEvents_CL`**. The DCR stream declares **254 columns in a fixed
order**; NLS must emit fields in that same order because values are mapped by
position.

The solution provides visibility into:

- DLP incidents and sensitive-data movement
- Malware and threat detections
- Policy violations and enforcement actions
- Anomalous user and application behavior (Shadow IT, risky apps)
- Geographic distribution of activity

**Included content**

| Content        | Count | Notes                                              |
|----------------|-------|----------------------------------------------------|
| Data Connector | 1     | CCF Blob Storage connector (`NetskopeAlertEventsConnector`) |
| Custom Table   | 1     | `NetskopeAlertEvents_CL`                           |
| Parser         | 1     | `NetskopeAlertEvents` (saved function)             |
| Workbook       | 1     | Netskope Alerts & Events Dashboard                 |
| Analytic Rules | 3     | High Severity Alert, Suspicious Application Activity, DLP Incident Spike |

## Architecture

```
        Netskope Log Streaming
                 |
                 v
        Azure Blob Storage            (gzip-compressed JSON)
                 |
                 v
           Event Grid                 (Blob Created notifications)
                 |
                 v
         Storage Queue                (notification queue + dead-letter queue)
                 |
                 v
   Sentinel CCF Connector             (Service Principal auth + DCR transform)
                 |
                 v
      NetskopeAlertEvents_CL          (Log Analytics custom table)
```

## Prerequisites

- A Microsoft Sentinel-enabled Log Analytics workspace.
- Permissions to install solutions from Content Hub and to create:
  - Data Collection Endpoint (DCE) and Data Collection Rule (DCR)
  - Storage queues (notification + dead-letter)
  - Event Grid system topic and subscription
  - Role assignments on the storage account / blob container
- An Azure Storage account + blob container that Netskope NLS streams to.
- A Netskope tenant with administrator access to configure Log Streaming.
- The Service Principal (object) ID of the Microsoft Sentinel CCF storage app
  (`appId 4f05ce56-95b6-4612-9d98-a45c8cc33f9f`) in your tenant.

## Deployment Steps

### 1. Configure Netskope Log Streaming
In the Netskope admin console, create a **Log Streaming** configuration that streams
**Alerts** and **Events** to your Azure Blob Storage container as **gzip-compressed CSV**.
The field order must match the connector's 254-column stream declaration (values are
mapped by position). Refer to the [Netskope NLS documentation](https://docs.netskope.com/en/netskope-help/data-security/netskope-log-streaming/)
and the [Netskope community integration guide](https://community.netskope.com/blogs-21/integration-alerts-events-from-netskope-log-streaming-to-microsoft-sentinel-8746).

### 2. Configure Azure Blob Storage
Create (or identify) the storage account and blob container. Record the:
- Blob Container URL
- Storage Account Location
- Storage Account Resource Group Name
- Storage Account Subscription ID

### 3. Deploy the solution (ARM template)
Install the **Netskope Alerts & Events** solution from **Content Hub**, or deploy
`Package/mainTemplate.json` directly. This registers the data connector definition,
DCR, custom table, parser, workbook, and analytic rule templates.

The deployment / Connect action provisions these Azure resources:

- Data Collection Rule (DCR) + Data Collection Endpoint (DCE)
- Data Connector Definition (`NetskopeAlertEventsConnector`)
- Event Grid system topic + subscription
- Storage Queue (notification queue)
- Storage Queue (dead-letter queue)
- Required role assignments (Storage Blob Data Reader / Storage Queue Data
  Contributor for the Sentinel CCF app)

### 4. Connect in Microsoft Sentinel
Open **Configuration → Data connectors → Netskope Alerts & Events (via Log Streaming)**,
provide:
- Service Principal ID (`principalId`)
- Blob Container URL (`blobContainerUri`)
- Blob Folder Name (optional)
- Storage Account Location / Resource Group / Subscription ID
- Event Grid Topic Name (leave empty to create a new one)

then click **Connect**.

## Validation

1. Confirm the connector shows **Connected** with a recent "Last data received" time.
2. Verify ingestion:
   ```kusto
   NetskopeAlertEvents_CL
   | where TimeGenerated > ago(1h)
   | summarize Count = count(), Last = max(TimeGenerated)
   ```
3. Validate the parser:
   ```kusto
   NetskopeAlertEvents
   | take 10
   ```
4. Confirm alerts populate severity and DLP fields:
   ```kusto
   NetskopeAlertEvents_CL
   | where IsAlert =~ "yes"
   | summarize count() by Severity, AlertType
   ```
5. Open the **Netskope Alerts & Events** workbook and confirm tiles render.

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---------|--------------|------------|
| Connector stuck on "Missing dependencies" | DCR / custom table not provisioned | Re-install from Content Hub; the CCF source files must be present so the package emits the DCR + table. |
| Connect fails: `principalId ... does not correspond to any parameters` | Service Principal control mismatch | The connector uses `ServicePrincipalIDTextBox_test`; ensure the deployed package was built from the provided source. |
| No data in `NetskopeAlertEvents_CL` | NLS not writing, or Event Grid/queue missing | Verify blobs land in the container; confirm Event Grid subscription + notification queue exist and role assignments are granted. |
| Data lands but columns are empty / shifted | NLS field **order** differs from the DCR stream | Logs are positional CSV — the NLS streaming configuration must emit the 254 fields in the exact order of the `Custom-NetskopeAlertEvents` stream declaration in `NetskopeAlertEvents_DCR.json`. A wrong order shifts every column. |
| **No data at all** despite connector "Connected" | Poller `format` mismatch | Confirm the poller `response.format` is **`csv`** with `isGzipCompressed: true` — NLS Alerts & Events are gzipped CSV, not JSON. JSON parsing of CSV yields zero rows. |
| `TimeGenerated` looks wrong | `timestamp` not epoch seconds | The DCR converts epoch seconds; if NLS emits milliseconds, divide by 1000 in the transform. |
| Records routed to dead-letter queue | Malformed / oversized blobs | Inspect the dead-letter queue messages; confirm `isGzipCompressed: true` and `format: csv` match the NLS output. |

## Notes

- The build-critical CCF connector is authored as JSON under
  `Data Connectors/NetskopeAlertEvents_CCF/`. The
  `Data Connectors/NetskopeAlertEventsConnectorDefinition.yaml` file is a
  human-readable specification only.
- `Package/mainTemplate.json` and `Package/createUiDefinition.json` are generated by
  the Sentinel V3 packaging tool (`Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1`).
