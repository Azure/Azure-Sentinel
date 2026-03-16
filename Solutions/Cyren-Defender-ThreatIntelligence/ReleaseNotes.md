| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.2      | 16-03-2026                    | **Optional JWT token + Marketplace link:** Made Cyren JWT token optional (minLength:0) with conditional Logic App deployment — connector only deploys when a token is provided. Added Azure Marketplace trial link to connector UI. Customers purchasing only one Cyren feed (IP Reputation or Malware URL) can now install without providing both tokens. |
| 3.0.1       | 06-03-2026                     | Added Logic App workflow definition with correct NDJSON payload parsing (payload.identifier, payload.detection), managed identity authentication for Sentinel createIndicator API, null identifier guard, and confidence mapping from Cyren risk score. |
| 3.0.0       | 23-02-2026                     | Initial release — Content Hub solution packaging with metadata and playbook reference. |
