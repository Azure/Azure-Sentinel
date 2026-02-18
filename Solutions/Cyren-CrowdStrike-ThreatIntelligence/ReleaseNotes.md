**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 1.0.0      | 17-02-2026                    | Initial Cyren CrowdStrike Threat Intelligence solution. Polls Cyren CCF feeds (IP reputation, malware URLs) and pushes IOCs to CrowdStrike Falcon Custom IOC API with PersistentToken pagination. Safety parameters: count=1000, queryWindowInMin=360, recurrence=6h. |
