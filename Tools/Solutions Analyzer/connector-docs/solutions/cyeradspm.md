# CyeraDSPM

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cyera Inc |
| **Support Tier** | Partner |
| **Support Link** | [https://support.cyera.io](https://support.cyera.io) |
| **Categories** | domains |
| **First Published** | 2025-10-15 |
| **Last Updated** | 2025-10-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyeraDSPM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyeraDSPM) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Cyera DSPM Azure Sentinel Data Connector](../connectors/cyeradspmccf.md)

**Publisher:** Cyera Inc

### [Cyera DSPM Azure Functions Sentinel Data Connector](../connectors/cyerafunctionsconnector.md)

**Publisher:** Cyera Inc

The **Cyera DSPM Azure Function Connector** enables seamless ingestion of Cyera’s **Data Security Posture Management (DSPM)** telemetry — *Assets*, *Identities*, *Issues*, and *Classifications* — into **Microsoft Sentinel**.\n\nThis connector uses an **Azure Function App** to call Cyera’s REST API on a schedule, fetch the latest DSPM telemetry, and send it to Sentinel through the **Azure Monitor Logs Ingestion API** via a **Data Collection Endpoint (DCE)** and **Data Collection Rule (DCR, kind: Direct)** — no agents required.\n\n**Tables created/used**\n\n| Entity | Table | Purpose |\n|---|---|---|\n| Assets | `CyeraAssets_CL` | Raw asset metadata and data-store context |\n| Identities | `CyeraIdentities_CL` | Identity definitions and sensitivity context |\n| Issues | `CyeraIssues_CL` | Findings and remediation details |\n| Classifications | `CyeraClassifications_CL` | Data class & sensitivity definitions |\n| MS View | `CyeraAssets_MS_CL` | Normalized asset view for dashboards |\n\n> **Note:** This v7 connector supersedes the earlier CCF-based approach and aligns with Microsoft’s recommended Direct ingestion path for Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `CyeraAssets_CL` |
| | `CyeraAssets_MS_CL` |
| | `CyeraClassifications_CL` |
| | `CyeraIdentities_CL` |
| | `CyeraIssues_CL` |
| **Connector Definition Files** | [FunctionAppDC.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyeraDSPM/Data%20Connectors/CyeraDSPM_Functions/FunctionAppDC.json) |

[→ View full connector details](../connectors/cyerafunctionsconnector.md)

## Tables Reference

This solution ingests data into **5 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyeraAssets_CL` | [Cyera DSPM Azure Functions Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Azure Sentinel Data Connector](../connectors/cyeradspmccf.md) |
| `CyeraAssets_MS_CL` | [Cyera DSPM Azure Functions Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Azure Sentinel Data Connector](../connectors/cyeradspmccf.md) |
| `CyeraClassifications_CL` | [Cyera DSPM Azure Functions Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Azure Sentinel Data Connector](../connectors/cyeradspmccf.md) |
| `CyeraIdentities_CL` | [Cyera DSPM Azure Functions Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Azure Sentinel Data Connector](../connectors/cyeradspmccf.md) |
| `CyeraIssues_CL` | [Cyera DSPM Azure Functions Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Azure Sentinel Data Connector](../connectors/cyeradspmccf.md) |

[← Back to Solutions Index](../solutions-index.md)
