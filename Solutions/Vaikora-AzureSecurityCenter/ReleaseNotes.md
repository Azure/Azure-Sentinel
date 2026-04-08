| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|---|---|---|
| 3.0.0 | 02-04-2026 | Initial release. Logic App playbook polls Vaikora API every 6 hours for high-severity actions, anomalies, and threat detections. Writes to Vaikora_SecurityAlerts_CL via Log Analytics Data Collector API. Includes 3 analytic rules (High Severity Alerts, Anomaly Detection, Feed Outage Detection). |
