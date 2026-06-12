| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.1       | 06-04-2026                     | Fix ARM deployment failure from Content Hub — inner Logic App template was evaluating `workspaceResourceId` incorrectly at deployment scope, causing `InvalidTemplate` error at position 61. Fixed by referencing `variables('workspace-name')` (which equals `parameters('workspace')`) consistent with the outer ARM evaluation scope. |
| 3.0.0       | 20-03-2026                     | Initial release — Cyren CCF feed polling with NDJSON parsing, SentinelOne IOC push via Threat Intelligence API, PersistentToken pagination, 6-hour recurrence, cost safety parameters enforced. |
