# WhoisFreaks Microsoft Sentinel Azure Function

Timer-triggered Python Azure Function that retrieves WhoisFreaks feeds and sends normalized records to Microsoft Sentinel using the Azure Monitor Logs Ingestion API and a DCR.

The function is deployed by the Microsoft Sentinel solution template. It uses:
- a system-assigned managed identity;
- a solution-created Storage Account for Function host state, checkpoints and distributed locks;
- a solution-created Data Collection Endpoint and Data Collection Rule;
- application settings populated by the solution template.

No WhoisFreaks API key is stored in source control.
