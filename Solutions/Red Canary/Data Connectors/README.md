# Red Canary Data Connector for Microsoft Sentinel

## Introduction

This folder contains the Red Canary Codeless Connector Framework (CCF) push connector for Microsoft Sentinel. The connector creates the resources required for Red Canary to send detections to the `RedCanaryDetections_CL` table through the Azure Monitor Logs Ingestion API.

## Folders

1. `RedCanaryDetections_ccp/` - Connector definition, push connector resource, DCR, table schema, sample payload, and connector-specific setup notes.

## Installing for users

After the solution is published, the connector is available in the Microsoft Sentinel data connectors gallery.

1. Go to **Microsoft Sentinel** > **Data connectors**.
2. Select **Red Canary Threat Detection (via Codeless Connector Framework)**.
3. Select **Deploy Red Canary connector resources**.
4. Copy the generated tenant, application, secret, data collection endpoint, data collection rule, and stream values from the connector page.
5. Configure the Red Canary Microsoft Sentinel response action with those values.

The connector shows data after Red Canary successfully posts detection records to the Logs Ingestion API.

## Installing for testing

For package validation, deploy the Red Canary solution package to a Microsoft Sentinel workspace and open the installed connector page. After deploying the connector resources, post a test JSON array to the `Custom-RedCanaryDetections` stream. The solution README includes the expected payload shape.

Confirm that:

- Records appear in `RedCanaryDetections_CL`.
- The connector graph shows recent data.
- One new `detection_id_s` creates one alert and one incident.
- Re-sending the same `detection_id_s` creates another raw row while the analytic rule continues to evaluate one representative record per detection ID in its query window.
- Matching alerts group into the same open incident by `detection_id` for up to seven days.

Useful ingestion check:

```kusto
RedCanaryDetections_CL
| where detection_id_s == "rc-detection-12345"
| summarize Rows=count(), FirstSeen=min(TimeGenerated), LastSeen=max(TimeGenerated) by detection_id_s
```

The solution README includes the payload contract, alert behavior, and validation queries.
