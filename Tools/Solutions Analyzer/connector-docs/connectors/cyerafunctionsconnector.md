# Cyera DSPM Azure Functions Sentinel Data Connector

| | |
|----------|-------|
| **Connector ID** | `CyeraFunctionsConnector` |
| **Publisher** | Cyera Inc |
| **Tables Ingested** | [`CyeraAssets_CL`](../tables-index.md#cyeraassets_cl), [`CyeraAssets_MS_CL`](../tables-index.md#cyeraassets_ms_cl), [`CyeraClassifications_CL`](../tables-index.md#cyeraclassifications_cl), [`CyeraIdentities_CL`](../tables-index.md#cyeraidentities_cl), [`CyeraIssues_CL`](../tables-index.md#cyeraissues_cl) |
| **Used in Solutions** | [CyeraDSPM](../solutions/cyeradspm.md) |
| **Connector Definition Files** | [FunctionAppDC.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyeraDSPM/Data%20Connectors/CyeraDSPM_Functions/FunctionAppDC.json) |

The **Cyera DSPM Azure Function Connector** enables seamless ingestion of Cyera’s **Data Security Posture Management (DSPM)** telemetry — *Assets*, *Identities*, *Issues*, and *Classifications* — into **Microsoft Sentinel**.\n\nThis connector uses an **Azure Function App** to call Cyera’s REST API on a schedule, fetch the latest DSPM telemetry, and send it to Sentinel through the **Azure Monitor Logs Ingestion API** via a **Data Collection Endpoint (DCE)** and **Data Collection Rule (DCR, kind: Direct)** — no agents required.\n\n**Tables created/used**\n\n| Entity | Table | Purpose |\n|---|---|---|\n| Assets | `CyeraAssets_CL` | Raw asset metadata and data-store context |\n| Identities | `CyeraIdentities_CL` | Identity definitions and sensitivity context |\n| Issues | `CyeraIssues_CL` | Findings and remediation details |\n| Classifications | `CyeraClassifications_CL` | Data class & sensitivity definitions |\n| MS View | `CyeraAssets_MS_CL` | Normalized asset view for dashboards |\n\n> **Note:** This v7 connector supersedes the earlier CCF-based approach and aligns with Microsoft’s recommended Direct ingestion path for Sentinel.

[← Back to Connectors Index](../connectors-index.md)
