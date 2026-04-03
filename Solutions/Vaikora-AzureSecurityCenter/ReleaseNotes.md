# Vaikora Security Center — Release Notes

## Version 1.0.0 (2026-04-02)

**Initial release.**

- Logic App playbook (`VaikoraToAzureSecurityCenter`) polls the Vaikora `/api/v1/actions` endpoint every 6 hours and writes high-severity, anomaly, and threat-detected actions to `Vaikora_SecurityAlerts_CL` via the Log Analytics Data Collector API.
- Analytic rule: **Vaikora - High Severity Security Alerts** — fires on any `high` or `critical` severity event ingested in the last 6 hours.
- Analytic rule: **Vaikora - Anomaly Detection** — fires on actions flagged `is_anomaly` or `threat_detected` that fall below the high/critical severity threshold.
- Analytic rule: **Vaikora - Feed Outage Detection** — fires when the custom table receives no records for 12 or more hours, signaling a broken playbook or expired API key.
