| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 4.0.0       | 19-08-2026                     | Migrated the data connector from the retiring HTTP Data Collector API to the Logs Ingestion API (DCR/DCE, RestApiPoller). Added a new `EgressDefend_v4_CL` table deployed side-by-side with the classic `EgressDefend_CL`, and a new `DefendAuditData_v4` parser that unions both tables (deduped) so history stays continuous during migration. Analytic rules, workbook and hunting query now use `DefendAuditData_v4`. |
| 3.0.0       | 02-08-2023                     | Initial Solution Release.                   |
