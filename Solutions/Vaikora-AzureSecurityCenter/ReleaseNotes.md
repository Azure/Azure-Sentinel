| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.1       | 28-05-2026                     | Fixed Poll_Vaikora_Actions to omit the agent_id query parameter when VaikoraAgentId is empty. The action now builds the query string inside the URI instead of using the queries object so the agent_id segment can be conditionally omitted. Without the fix the Vaikora API rejects the request with HTTP 422. |
| 3.0.0       | 28-04-2026                     | Initial release. Vaikora AI to Microsoft Defender for Cloud integration with security alert ingestion and three analytic rules for high-severity, anomaly, and feed outage detection.|
