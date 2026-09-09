| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                           |
|-------------|--------------------------------|--------------------------------------------------------------|
| 3.0.3       | 08-09-2026                     | Reduced duplicate ingestion across Check Point streams by correcting security-event cursor placement and treating exception endpoints as daily non-paginated snapshots |
| 3.0.2       | 08-09-2026                     | Fixed security event pagination to pass the continuation token in the POST request body and prevent duplicate ingestion |
| 3.0.1       | 21-07-2026                     | Promote CCF Data Connector to GA. |
| 3.0.0       | 08-07-2026                     | Initial release. Added **Data Connector** for Check Point Email Security (via Codeless Connector Framework) ingesting Security Events, Anti-Phishing Exceptions, Spam Exceptions, and Audit Logs data streams. |
