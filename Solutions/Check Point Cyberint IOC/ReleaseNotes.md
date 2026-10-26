| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**       |
| ----------- | ------------------------------ | ------------------------ |
| 3.0.5       | 21-08-2026                     | Fixed ARM template expression escaping in the data connector polling config (stray `]`) that caused the **Connect** deployment to fail with a template language expression parse error.<br>Fixed feed polling request body to send strict JSON (double-quoted): the Argos API now rejects single-quoted bodies with 422 Unprocessable Entity. |
| 3.0.4       | 02-06-2026                     | Updated support contact information and documentation links. |
| 3.0.2       | 03-04-2026                     | Fixed table schema definition causing connector creation failure.<br>Fixed apiEndpoint URL construction (removed duplicate https:// prefix).<br>Added Customer Name configuration field.<br>Improved connector UI with field descriptions, placeholders, and password masking for API Token.<br>Updated connector description and prerequisites text. |
| 3.0.1       | 12-09-2025                     | Replaces the variable reference for graphQueriesTableName with the explicit table name **'iocsent_CL'** |
| 3.0.0       | 17-06-2025                     | Initial Solution release. |
