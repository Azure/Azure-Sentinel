| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       | 28-04-2026                     | Fixed timestamp type mismatch in **Parsers** (DynatraceAttacks, DynatraceAuditLogs, DynatraceProblems, DynatraceSecurityProblems): V1 Unix epoch millisecond fields now converted to datetime, resolving duplicate typed columns in query results. |
| 3.0.2       | 02-04-2026                     | Added DCR based connectors.                 |
| 3.0.1       | 18-01-2024                     | Changes for rebranding from Microsoft 365 Defender to Microsoft Defender XDR, Updated user-agent strings used when calling Dynatrace REST API's, Added new Entity Mappings to **Analytic Rules**                                    Aligned Playbook, Data Connector & Workbook version numbers with rest of solution.           |
| 3.0.0       | 16-10-2023                     | Enabled new api paging mode on **Data Connector** to fix issues related to polling Dynatrace REST API's with a large number of results.     |
