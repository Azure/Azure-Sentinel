| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                               |
|-------------|--------------------------------|------------------------------------------------- |
| 3.1.1       | 10-04-2026                     |  Fixed CCF connector silently dropping logs containing quotation characters in JSON fields (e.g. cs10, cs11, additionalReqHeaders) by setting `csvEscapeMode: NoEscape` to disable RFC 4180 quote-escape handling |
| 3.1.0       | 30-03-2026                     |  Promoted the Imperva Cloud WAF CCF connector to Public Preview |
| 3.0.2       | 06-06-2025                     |  Migrated the **Function app** connector to **CCF** Data connector and updated **Parser**     |
| 3.0.1       | 07-11-2024                     |  Added existing ***Parser* into the solution     | 
| 3.0.0       | 22-08-2024                     |  Updated the python runtime version to **3.11**  | 