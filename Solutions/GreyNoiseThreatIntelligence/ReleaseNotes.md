| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.1.2       | 24-09-2026                     | Moved the **Analytic Rules** and **Workbook** from the retired `ThreatIntelligenceIndicator` table to `ThreatIntelIndicators`. The **Data Connector** now runs on Python 3.12 with GreyNoise SDK 3.1.0, and waits out GreyNoise and Sentinel API rate limits instead of failing. Indicator tags now show GreyNoise tag names. |
| 3.1.1       | 9-04-2026                     | Fix packaging issues, updated Data Connector status query and workbook templates to reflect the new ThreatIntelIndicators table |
| 3.1.0       | 12-03-2026                     | Updated to use GreyNoise Python SDK v3.0.3, updated Data Connector instructions, Fixed python module mismatches, bumped Az Functions Runtime |
| 3.0.3      | 17-07-2025                     | Updated to use GreyNoise Python SDK v3.0.1, use new Threat Intel API, updated requirements.txt, updated Data Connector instructions |
| 3.0.2       | 30-05-2024                     | Added missing AMA **Data Connector** reference in **Analytic rules**  |
| 3.0.1       | 29-11-2023                     | Updated the **Data Connector** Instructions, Fixed a Data Connector bug with Benign Indicator Ingest|
| 3.0.0       | 21-09-2023                     | Initial Solution Release                    |

