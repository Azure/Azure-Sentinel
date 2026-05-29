# Red Canary Solution for Microsoft Sentinel

## Overview

The Red Canary solution for Microsoft Sentinel ingests Red Canary detections into the `RedCanaryDetections_CL` custom table and includes analytic content for creating Microsoft Sentinel incidents from those detections.

The data connector uses the Microsoft Sentinel Codeless Connector Framework (CCF) push pattern. The connector page deploys the Data Collection Endpoint (DCE), Data Collection Rule (DCR), Microsoft Entra application, application secret, and DCR role assignment required for Red Canary to send detections through the Azure Monitor Logs Ingestion API.

## Solution Contents

- Data connector: **Red Canary Threat Detection (via Codeless Connector Framework)**
- Table: `RedCanaryDetections_CL`
- Stream: `Custom-RedCanaryDetections`
- Analytic rule: **Red Canary Threat Detection**

## Configuration

1. Install the Red Canary solution from Microsoft Sentinel Content Hub.
2. Open **Microsoft Sentinel** > **Data connectors**.
3. Select **Red Canary Threat Detection (via Codeless Connector Framework)**.
4. Select **Deploy Red Canary connector resources**.
5. Copy the generated connector values:
   - Tenant ID
   - Entra App Registration Application ID
   - Entra App Registration Secret
   - Data Collection Endpoint URI
   - Data Collection Rule Immutable ID
   - Stream name: `Custom-RedCanaryDetections`
6. Configure the Red Canary Microsoft Sentinel response action with those values.
7. Create and enable the **Red Canary Threat Detection** analytic rule from the installed rule template.

Red Canary sends detections to:

```text
{Data Collection Endpoint URI}/dataCollectionRules/{Data Collection Rule Immutable ID}/streams/Custom-RedCanaryDetections?api-version=2023-01-01
```

Use OAuth 2.0 client credentials with the generated Microsoft Entra application. For Azure public cloud, request a token with this scope:

```text
https://monitor.azure.com/.default
```

## Payload

The request body is a JSON array of Red Canary detection records. The preferred payload matches the current Red Canary Automate payload shape:

```json
[
  {
    "detection": {
      "id": "12345",
      "url": "https://example.my.redcanary.co/detections/12345",
      "headline": "Suspicious activity affecting HOSTNAME",
      "details": "Detection details from Red Canary.",
      "severity": "High"
    },
    "host": {
      "name": "HOSTNAME",
      "full_name": "HOSTNAME.example.com",
      "os_family": "Windows",
      "os_version": "10.0"
    },
    "tactics": "Execution, DefenseEvasion",
    "process_iocs": [],
    "child_process_iocs": [],
    "cross_process_iocs": [],
    "file_modification_iocs": [],
    "network_connection_iocs": [],
    "registry_modification_iocs": [],
    "identities": []
  }
]
```

The DCR accepts the nested Red Canary detection payload, flat field names such as `detection_id`, and Log Analytics field names such as `detection_id_s`. Supported shapes are normalized into the `*_s` columns in `RedCanaryDetections_CL`. `TimeGenerated` is set at ingestion time.

## Alert Behavior

Raw ingestion is append-only. If Red Canary sends the same `detection_id_s` more than once, multiple rows can exist in `RedCanaryDetections_CL`.

The analytic rule runs every five minutes with a one-day query period. It evaluates one representative record per `detection_id_s` in that query window and creates an alert when the detection first appears in the current rule interval.

Incident behavior:

- A new Red Canary detection ID creates one Microsoft Sentinel alert and one incident.
- Multiple IOC values on the same Red Canary detection are included in the alert context without changing alert cardinality.
- Detections with empty IOC arrays still produce an alert and incident.
- Matching alerts group into the same open incident by the `detection_id` custom detail for up to seven days.
- Closed incidents are not reopened.

## Validation Queries

Verify ingestion:

```kusto
RedCanaryDetections_CL
| where detection_id_s == "rc-detection-12345"
| project TimeGenerated, detection_id_s, detection_headline_s, detection_severity_s, host_name_s
| sort by TimeGenerated desc
```

Check repeated raw deliveries:

```kusto
RedCanaryDetections_CL
| where detection_id_s == "rc-detection-12345"
| summarize Rows=count(), FirstSeen=min(TimeGenerated), LastSeen=max(TimeGenerated) by detection_id_s
```

Check analytic output:

```kusto
SecurityAlert
| where AlertName == "Red Canary has published Detection-rc-detection-12345"
| summarize Alerts=count(), FirstAlert=min(TimeGenerated), LastAlert=max(TimeGenerated) by AlertName
```

## References

- [Azure Monitor Logs Ingestion API](https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview)
- [Microsoft Sentinel Codeless Connector Framework push connectors](https://learn.microsoft.com/azure/sentinel/create-push-codeless-connector)
