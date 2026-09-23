| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.1.2       | 10-09-2026                     | Migrated all 5 **Analytic Rules** from the retired `ThreatIntelligenceIndicator` table to `ThreatIntelIndicators` (STIX 2.1 schema); rewrote the **Workbook** queries, which still used legacy columns after the 3.1.1 table rename; moved the **Data Connector** Function App from Python 3.10 (end of support October 2026) to Python 3.12 and rebuilt its package; updated to GreyNoise Python SDK v3.1.0; Data Connector now backs off for 5 minutes on GreyNoise API rate limits (HTTP 429) and logs the exception type for other failures |
| 3.1.1       | 9-04-2026                     | Fix packaging issues, updated Data Connector status query and workbook templates to reflect the new ThreatIntelIndicators table |
| 3.1.0       | 12-03-2026                     | Updated to use GreyNoise Python SDK v3.0.3, updated Data Connector instructions, Fixed python module mismatches, bumped Az Functions Runtime |
| 3.0.3      | 17-07-2025                     | Updated to use GreyNoise Python SDK v3.0.1, use new Threat Intel API, updated requirements.txt, updated Data Connector instructions |
| 3.0.2       | 30-05-2024                     | Added missing AMA **Data Connector** reference in **Analytic rules**  |
| 3.0.1       | 29-11-2023                     | Updated the **Data Connector** Instructions, Fixed a Data Connector bug with Benign Indicator Ingest|
| 3.0.0       | 21-09-2023                     | Initial Solution Release                    |

