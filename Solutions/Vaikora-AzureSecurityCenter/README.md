# Vaikora Security Center — Microsoft Sentinel Content Hub Solution

Integrates [Vaikora](https://vaikora.com) AI-driven security signal detection with Microsoft Sentinel and Azure Defender for Cloud.

## How it works

A Logic App playbook (`VaikoraToAzureSecurityCenter`) runs on a 6-hour schedule. Each run:

1. Calls `GET https://api.vaikora.com/api/v1/actions?agent_id={id}&per_page=100` using your Vaikora API key.
2. Filters the response to actions that are `high` or `critical` severity, flagged as anomalies, or flagged as confirmed threats.
3. Writes each matching action to the `Vaikora_SecurityAlerts_CL` custom table in your Log Analytics workspace using the Data Collector API.

Three Sentinel analytic rules query that table to generate incidents:

| Rule | Severity | Fires when |
|------|----------|-----------|
| Vaikora - High Severity Security Alerts | High | Any `high`/`critical` action in the last 6 hours |
| Vaikora - Anomaly Detection | Medium | Any anomaly or threat-detected action below high/critical |
| Vaikora - Feed Outage Detection | Low | No data ingested in the last 12 hours |

## Prerequisites

- Microsoft Sentinel workspace (Log Analytics workspace with Sentinel enabled)
- Vaikora account with API access
- Vaikora API key and Agent ID

## Installation

Deploy through the Microsoft Sentinel Content Hub. During installation you will be prompted for:

| Parameter | Description |
|-----------|-------------|
| Workspace | The Log Analytics workspace where Sentinel is running |
| Playbook Name | Name for the Logic App (default: `VaikoraToAzureSecurityCenter`) |
| Vaikora API Key | Your Vaikora API key (stored securely, not logged) |
| Vaikora Agent ID | The Agent ID to poll for security actions |
| Log Analytics Workspace ID | The workspace GUID (found in Workspace Settings) |
| Log Analytics Primary Key | The workspace primary key used for HMAC-SHA256 signing |

After deployment, enable the three analytic rules from **Sentinel → Analytics → Rule Templates**.

## Custom log table

The playbook creates the `Vaikora_SecurityAlerts_CL` table automatically on first successful write. Fields ingested:

| Field | Type | Description |
|-------|------|-------------|
| AlertId_s | string | Vaikora action/alert ID |
| AgentId_s | string | Vaikora agent that generated the alert |
| ActionType_s | string | Action category |
| Severity_s | string | `low`, `medium`, `high`, `critical` |
| Title_s | string | Short alert title |
| Description_s | string | Full alert description |
| SourceIP_s | string | Source IP address |
| DestinationIP_s | string | Destination IP address |
| SourceHost_s | string | Source hostname |
| DestinationHost_s | string | Destination hostname |
| ProcessName_s | string | Process involved |
| UserName_s | string | User account involved |
| FilePath_s | string | File path involved |
| ConfidenceScore_d | double | Model confidence score (0–1) |
| IsAnomaly_b | bool | Vaikora anomaly flag |
| ThreatDetected_b | bool | Vaikora confirmed-threat flag |
| TimeGenerated | datetime | Event timestamp |

## Troubleshooting

**No data in `Vaikora_SecurityAlerts_CL`:**
- Open the Logic App run history in the Azure portal and check for failed runs.
- Verify the Vaikora API key is valid by calling the API manually.
- Confirm the Workspace ID and Primary Key are correct.

**Feed Outage alert fires after install:**
- The table is empty until the first playbook run. Wait up to 6 hours for the first poll, or trigger the Logic App manually.

## Support

Provided by [Data443 Risk Mitigation, Inc.](https://data443.com). Open an issue or contact support@data443.com.
