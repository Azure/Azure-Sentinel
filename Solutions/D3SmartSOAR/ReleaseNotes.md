| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.1       | 12-03-2026                     | Fix paging: switch from Offset to CountBasedPaging to prevent duplicate ingestion caused by Page Index not being replaced in nested POST body. Use TotalPages from API response as stop condition. |
| 3.0.0       | 27-02-2026                     | Initial release of D3 Smart SOAR data connector. Polls incidents every 5 minutes into D3SOARIncidents_CL with IncidentRawData and EventRawData dynamic fields via PollFromSentinel parameter. |
