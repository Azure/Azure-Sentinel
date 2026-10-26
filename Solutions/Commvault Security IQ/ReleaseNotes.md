| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.8 | 05-10-2026 | Enhanced **Commvault Security IQ (via Codeless Connector Framework)** data connector with configurable **Ingestion Mode** options: **Incremental (Time Window)** and **All Active Anomalies (No Time Window)**, and transitioned connector to General Availability. Fixed the CCF poller to send `fromTime` and `toTime` as query string parameters in **Incremental (Time Window)** mode. |
| 3.0.7 | 27-08-2026 | Fixed the CCF poller's Unix timestamp formatting for the `fromTime` and `toTime` query parameters. |
| 3.0.6 | 04-08-2026 | Updated the CCF connector and solution documentation. |
| 3.0.5 | 27-07-2026 | Added **Commvault Security IQ (via Codeless Connector Framework)** data connector, introduced **CommvaultAlertsCCF_CL** custom table and Data Collection Rule (DCR), updated analytics rule to detect client anomalies using **AnomalyType**, enhanced connector UI with sample queries and configuration guidance, and updated solution documentation for CCF-based deployment. |
| 3.0.4 | 05-03-2025 | Migrate to new data ingestion model via DCR & DCE setup |
| 3.0.3 | 12-09-2025 | Enhanced **Data connector** with configurable event collection and streamlined deployment |
| 3.0.2 | 28-03-2024 | Update **Playbook** - Bug fix in disabling data aging |
| 3.0.1 | 28-03-2024 | Adding **Data Connector** for Commvault Sentinel Integration |
| 3.0.0 | 21-08-2023 | Initial Solution Release |
