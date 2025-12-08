# Vectra XDR

| | |
|----------|-------|
| **Connector ID** | `VectraXDR` |
| **Publisher** | Vectra |
| **Tables Ingested** | [`Audits_Data_CL`](../tables-index.md#audits_data_cl), [`Detections_Data_CL`](../tables-index.md#detections_data_cl), [`Entities_Data_CL`](../tables-index.md#entities_data_cl), [`Entity_Scoring_Data_CL`](../tables-index.md#entity_scoring_data_cl), [`Health_Data_CL`](../tables-index.md#health_data_cl), [`Lockdown_Data_CL`](../tables-index.md#lockdown_data_cl) |
| **Used in Solutions** | [Vectra XDR](../solutions/vectra-xdr.md) |
| **Connector Definition Files** | [VectraXDR_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Data%20Connectors/VectraDataConnector/VectraXDR_API_FunctionApp.json) |

The [Vectra XDR](https://www.vectra.ai/) connector gives the capability to ingest Vectra Detections, Audits, Entity Scoring, Lockdown, Health and Entities data into Microsoft Sentinel through the Vectra REST API. Refer to the API documentation: `https://support.vectra.ai/s/article/KB-VS-1666` for more information.

[← Back to Connectors Index](../connectors-index.md)
