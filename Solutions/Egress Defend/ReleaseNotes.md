| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.1.0       | 01-09-2026                     | Added a new **Data Connector** using the Logs Ingestion API (CCF RestApiPoller with DCR/DCE), replacing the retiring HTTP Data Collector API. Added a new **Parser** `DefendAuditData_v4`. Updated **Analytic Rules**, **Workbook** and **Hunting Query** to read from `DefendAuditData_v4`. The original connector, table and parser are unchanged, so existing installations keep working until the new connector is enabled. |
| 3.0.0       | 02-08-2023                     | Initial Solution Release.                   |
