| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                |
|-------------|--------------------------------|-----------------------------------|
| 3.0.2       | 08-08-2026                     | Corrected the **Data Connector** stream schema and DCR transformations to match the payload sent by the Valence platform, and added a **sentinelSeverity** column that maps Valence's Critical severity into Microsoft Sentinel's supported range. |
| 3.0.1       | 04-08-2026                     | Migrated the **Data Connector** to CCF Push (Codeless Connector Framework). Alerts now ingest into **ValenceAlerts_CL** (previously ValenceAlert_CL) and a new **ValenceAuditLogs_CL** table was added. |
|  3.0.0      |  27-11-2023                    |  Initial Solution Release         |