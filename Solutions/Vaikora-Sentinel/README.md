# Vaikora AI Agent Behavioral Signals — Microsoft Sentinel Solution

This solution ingests AI agent behavioral data from the [Vaikora](https://vaikora.com) API into Microsoft Sentinel. It deploys a REST API poller connector, a custom log table, data collection rules, analytics rules, and a visualization workbook.

## What Gets Deployed

| Component | Description |
|-----------|-------------|
| Data connector | REST API poller — polls `https://api.vaikora.com/api/v1/actions` every 6 hours |
| Custom table | `Vaikora_AgentSignals_CL` — 17-column schema for agent signals |
| Analytic rule | Vaikora - High Risk AI Agent Action |
| Analytic rule | Vaikora - Behavioral Anomaly Detected |
| Analytic rule | Vaikora - Agent Policy Violation |
| Workbook | Vaikora AI Agent Signals Dashboard |

## Prerequisites

- Microsoft Sentinel workspace
- Vaikora API key (obtain from your Vaikora account)
- Agent ID from your Vaikora deployment

## Data Connector Setup

After deploying the solution:

1. Go to **Microsoft Sentinel > Data connectors**
2. Find **Vaikora AI Agent Behavioral Signals** and open it
3. Click **Open connector page**
4. Enter your Vaikora API key and agent ID
5. Click **Connect**

The connector polls the Vaikora API every 6 hours. Data appears in `Vaikora_AgentSignals_CL` within the first polling window.

## Custom Table Schema

| Column | Type | Description |
|--------|------|-------------|
| TimeGenerated | datetime | Timestamp of the agent action |
| action_id_s | string | Unique action identifier |
| action_type_s | string | Type of action performed |
| agent_id_s | string | Agent identifier |
| status_s | string | Action status (success, failure, blocked) |
| severity_s | string | Severity level (low, medium, high, critical) |
| policy_decision_s | string | Policy enforcement decision (allow, block, warn) |
| policy_id_s | string | Policy that evaluated the action |
| risk_score_d | int | Risk score 0-100 |
| risk_level_s | string | Risk level label |
| is_anomaly_b | bool | Whether Vaikora flagged this as anomalous |
| anomaly_score_d | real | Anomaly score 0.0-1.0 |
| anomaly_reason_s | string | Human-readable anomaly explanation |
| threat_detected_b | bool | Whether a threat was detected |
| threat_score_d | int | Threat score 0-100 |
| resource_type_s | string | Type of resource the agent accessed |
| log_hash_s | string | Unique hash for deduplication |

## Analytic Rules

All three rules are deployed in disabled state. Enable them from **Analytics > Rule templates** after confirming data is flowing.

**Vaikora - High Risk AI Agent Action** — fires when an action has `risk_score_d >= 75` and severity is `high` or `critical`. Severity: High. Frequency: 1h.

**Vaikora - Behavioral Anomaly Detected** — fires when `is_anomaly_b == true` and `anomaly_score_d >= 0.7`. Severity: Medium. Frequency: 30m.

**Vaikora - Agent Policy Violation** — fires when `policy_decision_s == 'block'`. Severity: Medium. Frequency: 15m.

## Workbook

The **Vaikora AI Agent Signals Dashboard** workbook is available under **Workbooks** after deployment. It includes:

- Signal overview tiles (total actions, blocked, anomalies, high-risk, critical)
- Actions over time chart
- Severity and policy decision breakdowns
- Anomaly timeline
- Recent high-risk actions table (top 50)
- Policy violations by agent and policy

## Support

Data443 Risk Mitigation, Inc. — support@data443.com — https://data443.com/support
