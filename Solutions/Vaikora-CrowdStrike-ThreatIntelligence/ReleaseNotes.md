| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.1       | 28-05-2026                     | Fixed Get_Vaikora_Actions URI to omit the agent_id query parameter when VaikoraAgentId is empty. Without the fix the request includes agent_id= and the Vaikora API rejects it with HTTP 422. |
| 3.0.0       | 28-04-2026                     | Initial release. Vaikora AI to CrowdStrike IOC integration with automated severity mapping and deduplication.|
