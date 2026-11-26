| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**        |
|-------------|--------------------------------|---------------------------|
| 3.1.0       | 11-11-2026                     | Migrated the data connector to the NordPass Activities API v2. Added the **NordPassActivities** parser, which normalizes both v1 and v2 rows so existing data keeps working. Retargeted all 9 **Analytic Rules** to the parser. Extended the custom table and DCR to the v2 schema. Removed the **Workbook**. |
| 3.0.2       | 15-09-2026                     | Added the missing DCR stream declaration, required by Azure Monitor validation for custom streams used with transformKql. |
| 3.0.1       | 25-08-2025                     | Added new Activity Logs   |
| 3.0.0       | 22-04-2025                     | Initial Solution Release. | 
 
