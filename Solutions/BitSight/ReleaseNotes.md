| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.3.0       | 20-05-2026                     | Added **10 V1 (snake_case) Parser variants** for all CCF-backed tables; updated existing **Parsers** to properly map CCF arm to PascalCase output schema; updated solution ownership to Microsoft; fixed **Parser** table references for CCF connectors (BitSightCompanyRatingDetails, BitSightFindingsCCF, BitSightVulnerabilitiesFindingsSummary); fixed CCF connector packaging: BitSightAlerts\_CL and BitSightBreaches\_CL tables now correctly placed in Events connector template |
| 3.2.0       | 11-05-2026                     | Added CCF **Data Connector** support with 3 new **Parsers** and updated existing **Parsers** to support BitSight CCF data |
| 3.1.1       | 22-04-2026                     | Updated **Solution Package** with the fix of solutionId |
| 3.1.0       | 31-03-2026                     | Updated the python runtime version to 3.12. Added support for Log Ingestion API and updated parsers accordingly. <br> Reverted the solution id to fix the BitSight Solution publishing issue.                   |
| 3.0.2       | 26-07-2024                     | Update **Analytic rules** for missing TTP                          |
| 3.0.1       | 15-04-2024                     | Added Bitsight prefix in data tables name                           |
| 3.0.0       | 23-01-2024                     | Updated **Data Connector** code with the fix of Pagination and Checkpoint related issue |
         
                                                                                                                 
