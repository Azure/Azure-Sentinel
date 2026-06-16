| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 4.0.0       | 15-06-2026                     | Replaced the legacy Azure Function (REST API pull) **Connector** with the Microsoft Sentinel push integration (DCR + RBAC grant). Data is now pushed by Wiz to `WizIssuesV3_CL`, `WizDetectionsV3_CL`, and `WizAuditLogsV3_CL` (Issues, Detections, Audit Logs). **Workbook** rewritten to the new tables and columns. |
| 3.0.0       | 15-07-2024                     | Updated the queries on the **Workbook** and **Connector** to match with the new table names we offer  |
| 2.0.0       | 07-09-2023                     | Updated **Workbook** query in Maintemplate  |
