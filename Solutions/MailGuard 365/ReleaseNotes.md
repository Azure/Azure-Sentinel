| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 14-09-2026                     | Migrated data connector from the deprecated HTTP Data Collector API to the Azure Monitor Logs Ingestion API (Codeless Connector Framework Push pattern). Data now lands in the `MG365ThreatData_CL` table via a Data Collection Rule; the legacy `MailGuard365_Threats_CL` table is no longer written to. Updated workbook and hunting queries to the new schema. |
| 3.0.0       | 31-08-2023                     | Initial Solution Release                     |
