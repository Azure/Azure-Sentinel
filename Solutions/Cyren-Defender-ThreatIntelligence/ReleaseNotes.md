| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.0       | 23-02-2026                     | Initial release — Polls Cyren CCF threat intelligence feed every 6 hours, transforms IP reputation data into STIX indicators, pushes to Microsoft Sentinel ThreatIntelligenceIndicator table via createIndicator API. Logic App with managed identity auth, PersistentToken pagination, cost safety parameters (count=1000, queryWindowInMin=360, 5 iteration limit). |
