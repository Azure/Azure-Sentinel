# Vectra XDR

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Vectra Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.vectra.ai/support](https://www.vectra.ai/support) |
| **Categories** | domains |
| **First Published** | 2023-07-04 |
| **Last Updated** | 2024-08-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Vectra XDR](../connectors/vectraxdr.md)

**Publisher:** Vectra

The [Vectra XDR](https://www.vectra.ai/) connector gives the capability to ingest Vectra Detections, Audits, Entity Scoring, Lockdown, Health and Entities data into Microsoft Sentinel through the Vectra REST API. Refer to the API documentation: `https://support.vectra.ai/s/article/KB-VS-1666` for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `Audits_Data_CL` |
| | `Detections_Data_CL` |
| | `Entities_Data_CL` |
| | `Entity_Scoring_Data_CL` |
| | `Health_Data_CL` |
| | `Lockdown_Data_CL` |
| **Connector Definition Files** | [VectraXDR_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Data%20Connectors/VectraDataConnector/VectraXDR_API_FunctionApp.json) |

[→ View full connector details](../connectors/vectraxdr.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Audits_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |
| `Detections_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |
| `Entities_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |
| `Entity_Scoring_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |
| `Health_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |
| `Lockdown_Data_CL` | [Vectra XDR](../connectors/vectraxdr.md) |

[← Back to Solutions Index](../solutions-index.md)
